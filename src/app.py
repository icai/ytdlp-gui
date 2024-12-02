import streamlit as st
import yt_dlp
import os
import re
import yaml
import random
from yt_dlp.utils import DownloadError
import hashlib

download_percent = 0

# Function to load configuration from YAML file
def load_config():
    config_file = "config.yaml"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    else:
        st.error(f"Config file {config_file} not found.")
        return {}

# Function to update configuration in YAML file
def update_config(key, value):
    config_file = "config.yaml"
    config = load_config()
    config[key] = value
    with open(config_file, 'w') as f:
        yaml.dump(config, f)

# Function to get video formats
def get_video_formats(url, proxy, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])
            title = info_dict.get('title', 'No title available')
            description = info_dict.get('description', 'No description available')
            return formats, title, description
        except DownloadError as e:
            st.error(f"Error extracting video formats: {str(e)}")
            return [], None, None

# Progress callback function to update Streamlit progress bar
def progress_hook(d, progress_placeholder, status_placeholder):
    global download_percent, download_tip
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes', 1)  # Prevent division by zero
        downloaded_bytes = d.get('downloaded_bytes', 0)
        download_percent = max(0.0, min(downloaded_bytes / total_bytes, 1.0))
        speed = d.get('speed', 0)
        eta = d.get('eta', 0)
        download_tip = f"Downloaded: {format_size(downloaded_bytes)}, Speed: {format_size(speed)}/s, ETA: {format_size(eta)}"
        progress_placeholder.progress(download_percent)
        status_placeholder.text(download_tip)


# Function to truncate filenames to avoid errors due to long names
def truncate_filename(filename, max_length=200):
    if len(filename) <= max_length:
        return filename
    
    name, ext = os.path.splitext(filename)
    hash_length = 8
    truncated_length = max_length - len(ext) - hash_length - 1
    
    hashed = hashlib.md5(name.encode()).hexdigest()[:hash_length]
    return f"{name[:truncated_length]}_{hashed}{ext}"

# Function to get the next serial number for downloaded files
def get_next_serial_number(download_dir):
    # Get all files in the directory
    files = os.listdir(download_dir)

    # Extract numbers from filenames that start with a number
    numbers = []
    for f in files:
        # Try to extract the leading number from the filename
        parts = f.split('_', 1)  # Split by the first underscore
        if len(parts) > 1 and parts[0].isdigit():  # Ensure the part before the underscore is a number
            try:
                numbers.append(int(parts[0]))  # Add the number to the list
            except ValueError:
                continue  # Ignore filenames that don't have a valid number

    # If no valid numbers, start from 1, else return the next number
    return max(numbers, default=0) + 1


# Function to download video
def download_video(url, title, ext, format_code, proxy, download_dir, ydl_opts):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Get the next serial number
    serial_number = get_next_serial_number(download_dir)

    def ydl_filename(title, ext='mp4'):
        # Generate filename with truncated title (first 20 characters) and serial number
        filename = f'{serial_number}_{title[:20].replace(" ", "_").replace(":", "").replace("/", "")}.{ext}'
        return filename

    # Update ydl_opts to use ydl_filename dynamically for outtmpl
    filename = ydl_filename(title, ext)
        # Initialize the progress bar and status text
    progress_bar = st.progress(0, text="Starting download...")
    status_text = st.text("Starting download...")
    ydl_opts.update({
        'outtmpl': os.path.join(download_dir, filename),  # Placeholder to ensure structure
        'proxy': proxy,
        'progress_hooks': [lambda d: progress_hook(d, progress_bar, status_text)], 
        'format': format_code,
        'retries': 3,  # Retry on failure
        'fragment_retries': 3,  # Retry on segment failure
        'timeout': 60,  # Timeout for each download segment
    })

    # Use a custom function to generate the filename dynamically
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            st.write(f"Downloading video to {download_dir}...")
            global download_percent, download_tip  # Initialize download_percent
            download_percent = 0
            download_tip = ""
            progress_bar.progress(download_percent)  # Set the initial state
            status_text.text("Starting download...")

            # Start the actual download
            ydl.download([url])

    
            progress_bar.empty()  # Clear the progress bar
            status_text.text(f"Download completed: {filename}")

        except DownloadError as e:
            st.error(f"Error downloading video: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")



# Function to validate the URL
def is_valid_url(url):
    youtube_pattern = r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+"
    tiktok_pattern = r"https?://(?:www\.)?tiktok\.com/.*"

    if re.match(youtube_pattern, url):
        return "YouTube"
    elif re.match(tiktok_pattern, url):
        return "TikTok"
    else:
        return None

# Filter formats based on conditions for YouTube and TikTok
def filter_formats(formats, platform, video=True):
    if platform == "YouTube":
        if video:
            return [
                f for f in formats if 'height' in f and f['height'] in [480, 720, 1080]
                # downloader_options: { http_chunk_size: 10485760 },
                and 'vcodec' in f and f.get('ext', '') == 'mp4' and (f.get('filesize', 0) > 0 or f.get('downloader_options', {}).get('http_chunk_size', 0) > 0)
            ]
        else:
            return [
                f for f in formats if 'acodec' in f and f.get('ext', '') == 'm4a' and f.get('filesize', 0) > 0
            ]
    
    elif platform == "TikTok":
        if video:
            return [
                f for f in formats if 'vcodec' in f and f.get('ext', '') == 'mp4' and f.get('filesize', 0) > 0
            ]
        else:
            return []

    return []

# Helper function to format filesize
def format_size(size):  
    if size is None or size == 0:
        return "Size unknown"
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return size

def get_format_details(f, is_video=True):
    ext = f.get('ext', 'unknown').upper()
    format_id = f.get('format_id', 'N/A')
    filesize = f.get('filesize', None) or f.get('downloader_options', {}).get('http_chunk_size', 0)
    height = f.get('height', 'N/A') if is_video else None
    return f"{format_id} - {ext}, {height}p, {format_size(filesize)}" if is_video else f"{format_id} - {ext}, {format_size(filesize)}"


# Streamlit UI
def main():

    # Set the document title and other page configurations
    st.set_page_config(
        page_title="YTDLP GUI Downloader",  # Title of the document
        page_icon="🎥",  # Icon shown in the browser tab
        layout="wide"  # Optional: Set the layout to wide (default is centered)
    )


    # st.set_page_config(layout="wide")  # Set wide layout

    # Load config from config.yaml
    config = load_config()
    proxy = random.choice(config.get('proxy_list', ['http://127.0.0.1:7890']))
    download_dir = config.get('download_directory', 'output')
    ydl_opts = config.get('yt_dlp_options', {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True
    })

    # Sidebar for configuration settings
    with st.sidebar:
        st.title("Configuration Settings")
        st.subheader("Proxy Settings")
        proxy_input = st.text_input("Proxy URL", proxy, key="proxy_input")
        if proxy_input != proxy:
            update_config('proxy_list', [proxy_input])
            st.success("Proxy updated in config.yaml")
            config = load_config()  # Reload config

        st.subheader("Download Directory")
        download_dir_input = st.text_input("Download Directory", download_dir, key="download_dir_input")
        if download_dir_input != download_dir:
            update_config('download_directory', download_dir_input)
            st.success("Download directory updated in config.yaml")
            config = load_config()  # Reload config

        st.subheader("yt-dlp Options")
        format_option = st.text_input("yt-dlp Format Options", str(ydl_opts), key="format_option")
        if format_option != str(ydl_opts):
            try:
                new_ydl_opts = eval(format_option)
                update_config('yt_dlp_options', new_ydl_opts)
                st.success("yt-dlp options updated in config.yaml")
                config = load_config()  # Reload config
            except:
                st.error("Invalid yt-dlp options format. Please enter a valid Python dictionary.")

    # Main content for URL input

    # Your app content goes here
    st.title("YTDLP GUI Downloader")
    st.write("This app allows you to download videos from YouTube and TikTok.")

    url = st.text_input("Enter the video URL", "")  # Increased height to 300px

    selected_format = None

    download_type = "Video"
    if url:
        platform = is_valid_url(url)
        if platform:
            st.write(f"Fetching video information for {platform}...")

            formats, title, description = get_video_formats(url, proxy_input, ydl_opts)

            # if debug output formats to debug.js
            with open('debug.js', 'w') as f:
                f.write(str(formats))

            if formats:
                st.subheader("Video Title")
                st.write(title)

                st.subheader("Video Description")
                st.write(description)

                st.write("Available formats:")

                video_formats = filter_formats(formats, platform, video=True)
                audio_formats = filter_formats(formats, platform, video=False)

                # video_format_options = [
                #     get_format_details(f, is_video=True)
                #     for f in video_formats
                # ]

                # audio_format_options = [
                #     get_format_details(f, is_video=False)
                #     for f in audio_formats
                # ]
                format_options = [
                    get_format_details(f, is_video=True) for f in video_formats
                ] + [
                    get_format_details(f, is_video=False) for f in audio_formats
                ]
                selected_format = st.radio("Select the download", format_options)

                # download_type = st.radio("Select download type", ("Video", "Audio"), index=0)

                # if download_type == "Video":
                #     selected_format = st.radio("Select the download", format_options)
                # elif download_type == "Audio":
                #     if not audio_formats:
                #         st.error("No audio formats available for this platform.")
                #     else:
                #         selected_format = st.selectbox("Select the audio quality", audio_format_options)
                # else:
                #     selected_format = st.radio("Select the video quality", video_format_options)
                if selected_format:
                    selected_format_code = selected_format.split(" - ")[0]
                    selected_format_ext = selected_format.split(" - ")[1].split(",")[0].lower()

                    if st.button("Download"):
                        st.write(f"Downloading {download_type.lower()} with format {selected_format_code}...")

                        try:
                            download_video(url, title, selected_format_ext, selected_format_code, proxy_input, download_dir_input, ydl_opts)
                            st.success(f"{download_type} downloaded successfully to {download_dir_input}!")
                        except Exception as e:
                            st.error(f"Error downloading {download_type.lower()}: {e}")
                else:
                    st.warning("Please select a format before downloading.")
            else:
                st.error("No formats available for the provided URL.")
        else:
            st.error("Invalid URL. Please enter a valid YouTube or TikTok URL.")

if __name__ == "__main__":
    main()


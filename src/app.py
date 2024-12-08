import streamlit as st
import tempfile
import os
from src.config import get_config, update_config
from src.utils import is_valid_url, get_format_details, filter_formats
from src.downloader import Downloader
from src.merger import merge_video_audio
from src.components.textareaCopy import input_copy, textarea_copy
import zhconv


def main():
  st.set_page_config(page_title='YTDLP GUI Downloader', page_icon='🎥', layout='wide')

  # st.markdown(
  #   """
  #     <style>
  #         /* Hide the Streamlit top-right menu (hamburger menu) */
  #         .stAppToolbar {
  #             visibility: hidden;
  #             display: none;
  #         }
  #     </style>
  #   """,
  #   unsafe_allow_html=True,
  # )

  # Initialize session state
  if 'config' not in st.session_state:
    st.session_state.config = get_config()

  if 'selected_video_formats' not in st.session_state:
    st.session_state.selected_video_formats = []

  if 'selected_audio_formats' not in st.session_state:
    st.session_state.selected_audio_formats = []

  if 'video_info' not in st.session_state:
    st.session_state.video_info = None

  config = st.session_state.config

  st.title('YTDLP GUI Downloader')
  st.write('This app allows you to download videos from YouTube and TikTok.')

  with st.sidebar:
    st.title('Configuration Settings')
    st.subheader('Proxy Settings')
    proxy_input = st.text_input('Proxy URL', config['proxy'], key='proxy_input')
    if proxy_input != config['proxy']:
      update_config('proxy', proxy_input)
      st.session_state.config['proxy'] = proxy_input
      st.success('Proxy updated in config.yaml')

    st.subheader('Download Directory')
    download_dir_input = st.text_input('Download Directory', config['download_dir'], key='download_dir_input')
    if download_dir_input != config['download_dir']:
      update_config('download_directory', download_dir_input)
      st.session_state.config['download_dir'] = download_dir_input
      st.success('Download directory updated in config.yaml')

    st.subheader('yt-dlp Options')
    format_option = st.text_input('yt-dlp Format', str(config['ydl_opts']['format']), key='format_option')
    if format_option != str(config['ydl_opts']['format']):
      update_config('yt_dlp_options.format', format_option)
      st.session_state.config['ydl_opts']['format'] = format_option
      st.success('yt-dlp format updated in config.yaml')

    noplaylist_option = st.checkbox('noplaylist', config['ydl_opts']['noplaylist'], key='noplaylist_option')
    if noplaylist_option != config['ydl_opts']['noplaylist']:
      update_config('yt_dlp_options.noplaylist', noplaylist_option)
      st.session_state.config['ydl_opts']['noplaylist'] = noplaylist_option
      st.success('yt-dlp noplaylist updated in config.yaml')

    quiet_option = st.checkbox('quiet', config['ydl_opts']['quiet'], key='quiet_option')
    if quiet_option != config['ydl_opts']['quiet']:
      update_config('yt_dlp_options.quiet', quiet_option)
      st.session_state.config['ydl_opts']['quiet'] = quiet_option
      st.success('yt-dlp quiet updated in config.yaml')

  url = st.text_input('Enter the video URL', '', key='url_input')

  if url:
    if 'url_processed' not in st.session_state or st.session_state.url_processed != url:
      platform = is_valid_url(url)
      if platform:
        st.write(f'Fetching video information for {platform}...')
        downloader = Downloader(url, config['proxy'], config['download_dir'], config['ydl_opts'])
        formats, title, description = downloader.get_video_formats()

        if formats:
          st.session_state.video_info = {
            'formats': formats,
            'title': title,
            'description': description,
            'platform': platform,
          }
          st.session_state.url_processed = url
        else:
          st.error('No formats available for the provided URL.')
      else:
        st.error('Invalid URL. Please enter a valid YouTube or TikTok URL.')

  if st.session_state.video_info:
    video_info = st.session_state.video_info
    st.subheader('Video Title')
    title = video_info['title']
    if config['langconvert'] == 'zh-cn':
      title = zhconv.convert(title, 'zh-cn')
    # st.write(title)
    input_copy(title)

    st.subheader('Video Description')
    description = video_info['description']
    if config['langconvert'] == 'zh-cn':
      description = zhconv.convert(description, 'zh-cn')
    # st.write(description)
    textarea_copy(description)

    st.subheader('Available Formats')
    formats = video_info['formats']
    video_formats = filter_formats(formats, video_info['platform'], video=True)
    audio_formats = filter_formats(formats, video_info['platform'], video=False)

    st.write('Video Formats:')
    video_format_options = [get_format_details(f) for f in video_formats]
    selected_video_formats = []
    for f in video_format_options:
      if st.checkbox(f, key=f):
        selected_video_formats.append(f)

    st.write('Audio Formats:')
    audio_format_options = [get_format_details(f) for f in audio_formats]
    selected_audio_formats = []
    for f in audio_format_options:
      if st.checkbox(f, key=f):
        selected_audio_formats.append(f)

    st.session_state.selected_video_formats = selected_video_formats
    st.session_state.selected_audio_formats = selected_audio_formats

    if st.button('Download'):
      downloader = Downloader(url, config['proxy'], config['download_dir'], config['ydl_opts'])
      for selected_format in st.session_state.selected_video_formats:
        format_code = selected_format.split(' - ')[0]
        format_ext = selected_format.split(' - ')[1].split(',')[0].lower()
        downloader.download_video(video_info['title'], format_ext, format_code)

      for selected_format in st.session_state.selected_audio_formats:
        format_code = selected_format.split(' - ')[0]
        format_ext = selected_format.split(' - ')[1].split(',')[0].lower()
        downloader.download_video(video_info['title'], format_ext, format_code)

    if st.button('Download and Merge'):
      if st.session_state.selected_video_formats and st.session_state.selected_audio_formats:
        video_format_code = st.session_state.selected_video_formats[0].split(' - ')[0]
        audio_format_code = st.session_state.selected_audio_formats[0].split(' - ')[0]

        # Create downloader object only when ready
        try:
          with tempfile.TemporaryDirectory() as temp_dir:
            downloader = Downloader(url, config['proxy'], config['download_dir'], config['ydl_opts'])

            # Download video and audio
            video_path = downloader.download_video(video_info['title'], 'mp4', video_format_code)
            audio_path = downloader.download_video(video_info['title'], 'm4a', audio_format_code)

            if video_path and audio_path:
              merged_title = f'{video_info["title"]}_merged.mp4'
              output_path = os.path.join(config['download_dir'], merged_title)
              if merge_video_audio(video_path, audio_path, output_path):
                st.success(f'Video and audio merged successfully: {output_path}')
              else:
                st.error('Failed to merge video and audio.')
        except Exception as e:
          st.error(f'Error downloading and merging: {e}')
      else:
        st.error('Please select both a video and audio format to merge.')


if __name__ == '__main__':
  main()

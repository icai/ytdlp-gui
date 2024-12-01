# YTDLP GUI Downloader

A simple Streamlit app that allows users to download videos from **YouTube** and **TikTok** using **yt-dlp**.

## Features
- **Download Videos and Audio** from YouTube and TikTok
- Select the video quality (e.g., 480p, 720p, 1080p)
- Choose between video and audio formats
- Proxy support for downloading
- Configurable download directory and options
- Progress bar for download status

## Requirements

To run this app locally, you need to have Python 3.x installed, along with the required dependencies.

### Dependencies



You can install these dependencies by running:

```bash
pipenv install
```




## Setup and Configuration

### Step 1: Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/icai/ytdlp-gui.git
cd ytdlp-gui
```

### Step 2: Configure the App

The app uses a configuration file `config.yaml` to manage settings such as the download directory, proxy list, and yt-dlp options.

A sample `config.yaml` looks like this:

```yaml
# config.yaml
download_directory: 'downloads'  # Directory where videos will be saved
proxy_list:  # List of proxy URLs for downloading
  - 'http://127.0.0.1:7890'
yt_dlp_options:  # Custom yt-dlp options
  format: 'bestaudio/best'
  noplaylist: True
  quiet: True
```

If the `config.yaml` file is missing, the app will generate it on the first run with default values.

### Step 3: Running the App

Once everything is configured, run the app using the following command:

```bash
pipenv run start
```

This will launch the app in your browser (typically at `http://localhost:8501`).

### Step 4: Using the App

1. **Enter Video URL**: Enter the URL of a video from YouTube or TikTok.
2. **Choose Format**: Select the format (video or audio) and quality (e.g., 720p, 1080p, etc.).
3. **Download**: Click the "Download" button to start the download process.
4. **Progress Bar**: A progress bar will show the download status, including speed and ETA.

## Example Usage

1. **YouTube**:
   - Enter a YouTube video URL like `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
2. **TikTok**:
   - Enter a TikTok video URL like `https://www.tiktok.com/@exampleuser/video/1234567890123456789`

## Customization

- You can adjust the download directory by changing the `download_directory` in `config.yaml`.
- You can add or update proxy URLs in the `proxy_list` to handle geo-restricted downloads.
- You can modify the `yt_dlp_options` section to set custom download settings (e.g., preferred formats, quality, etc.).

## Troubleshooting

- **Missing `config.yaml`**: If the `config.yaml` file is missing, the app will automatically generate a new one with default settings. Ensure the file is located in the same directory as the script.
- **Slow Download Speeds**: If you're experiencing slow download speeds, try adding proxies to the `proxy_list` section in `config.yaml`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

If you'd like to contribute to this project, feel free to open an issue or submit a pull request. We welcome contributions, bug fixes, and improvements!

---

Enjoy downloading videos with ease! 🎥📥
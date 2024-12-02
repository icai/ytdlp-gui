import os
import yt_dlp
import streamlit as st
from yt_dlp.utils import DownloadError
from .utils import cut_title, get_next_serial_number, format_size


class Downloader:
  def __init__(self, url, proxy, download_dir, ydl_opts):
    self.url = url
    self.proxy = proxy
    self.download_dir = download_dir
    self.ydl_opts = ydl_opts
    self.progress_bar = None
    self.status_text = None

  def get_video_formats(self):
    with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
      try:
        info_dict = ydl.extract_info(self.url, download=False)
        formats = info_dict.get('formats', [])
        title = info_dict.get('title', 'No title available')
        description = info_dict.get('description', 'No description available')
        return formats, title, description
      except DownloadError as e:
        st.error(f'Error extracting video formats: {str(e)}')
        return [], None, None

  def get_title(self, title):
    serial_number = get_next_serial_number(self.download_dir)
    filename = f'{serial_number}_{cut_title(title)}'
    return filename

  def progress_hook(self, d):
    if d['status'] == 'downloading':
      total_bytes = d.get('total_bytes', 1)
      downloaded_bytes = d.get('downloaded_bytes', 0)
      download_percent = max(0.0, min(downloaded_bytes / total_bytes, 1.0))
      speed = d.get('speed', 0)
      eta = d.get('eta', 0)
      download_tip = (
        f'Downloaded: {format_size(downloaded_bytes)}, Speed: {format_size(speed)}/s, ETA: {format_size(eta)}'
      )
      self.progress_bar.progress(download_percent)
      self.status_text.text(download_tip)

  def download_video(self, title, ext, format_code):
    if not os.path.exists(self.download_dir):
      os.makedirs(self.download_dir)

    filename = f'{self.get_title(title)}.{ext}'
    self.progress_bar = st.progress(0, text='Starting download...')
    self.status_text = st.text('Starting download...')

    ydl_opts = {
      **self.ydl_opts,
      'outtmpl': os.path.join(self.download_dir, filename),
      'proxy': self.proxy,
      'progress_hooks': [self.progress_hook],
      'format': format_code,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      try:
        st.write(f'Downloading video to {self.download_dir}...')
        ydl.download([self.url])
        self.progress_bar.empty()
        self.status_text.text(f'Download completed: {filename}')
        return os.path.join(self.download_dir, filename)
      except DownloadError as e:
        st.error(f'Error downloading video: {str(e)}')
      except Exception as e:
        st.error(f'Unexpected error: {str(e)}')
    return None

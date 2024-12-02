import os
import re
import hashlib


def is_valid_url(url):
  youtube_pattern = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+'
  tiktok_pattern = r'https?://(?:www\.)?tiktok\.com/.*'

  if re.match(youtube_pattern, url):
    return 'YouTube'
  elif re.match(tiktok_pattern, url):
    return 'TikTok'
  else:
    return None


def format_size(size):
  if size is None or size == 0:
    return 'Size unknown'
  for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
    if size < 1024.0:
      return f'{size:.2f} {unit}'
    size /= 1024.0
  return size


def truncate_filename(filename, max_length=200):
  if len(filename) <= max_length:
    return filename

  name, ext = os.path.splitext(filename)
  hash_length = 8
  truncated_length = max_length - len(ext) - hash_length - 1

  hashed = hashlib.md5(name.encode()).hexdigest()[:hash_length]
  return f'{name[:truncated_length]}_{hashed}{ext}'


def cut_title(title, max_length=20):
  return title[:max_length].replace(' ', '_').replace(':', '').replace('/', '')


def get_next_serial_number(download_dir):
  files = os.listdir(download_dir)
  numbers = []
  for f in files:
    parts = f.split('_', 1)
    if len(parts) > 1 and parts[0].isdigit():
      try:
        numbers.append(int(parts[0]))
      except ValueError:
        continue
  return max(numbers, default=0) + 1


def get_format_details(f):
  is_video = 'vcodec' in f and f.get('ext') == 'mp4'
  ext = f.get('ext', 'unknown').upper()
  format_id = f.get('format_id', 'N/A')
  filesize = f.get('filesize', None) or f.get('downloader_options', {}).get('http_chunk_size', 0)
  height = f.get('height', 'N/A') if is_video else None
  #  if is video, return format_id - ext, height, filesize
  # if is audio, return format_id - ext, filesize
  return (
    f'{format_id} - {ext}, {height}p, {format_size(filesize)}'
    if is_video
    else f'{format_id} - {ext}, {format_size(filesize)}'
  )


def filter_formats(formats, platform, video=True):
  def youtube_video_filter(f):
    return (
      'height' in f
      and f['height'] in [480, 720, 1080]
      and 'vcodec' in f
      and f.get('ext') == 'mp4'
      and (f.get('filesize', 0) > 0 or f.get('downloader_options', {}).get('http_chunk_size', 0) > 0)
    )

  def youtube_audio_filter(f):
    return 'acodec' in f and f.get('ext') == 'm4a' and f.get('filesize', 0) > 0

  def tiktok_video_filter(f):
    return 'vcodec' in f and f.get('ext') == 'mp4' and f.get('filesize', 0) > 0

  filters = {
    'YouTube': {True: youtube_video_filter, False: youtube_audio_filter},
    'TikTok': {
      True: tiktok_video_filter,
      False: lambda f: False,  # TikTok doesn't support audio-only downloads
    },
  }

  platform_filters = filters.get(platform, {})
  filter_func = platform_filters.get(video, lambda f: False)

  return list(filter(filter_func, formats))

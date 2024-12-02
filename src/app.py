import streamlit as st
import tempfile
import os
from src.config import get_config, update_config
from src.utils import is_valid_url, get_format_details, filter_formats
from src.downloader import Downloader
from src.merger import merge_video_audio
import zhconv


def main():
  st.set_page_config(page_title='YTDLP GUI Downloader', page_icon='🎥', layout='wide')

  config = get_config()

  st.title('YTDLP GUI Downloader')
  st.write('This app allows you to download videos from YouTube and TikTok.')

  with st.sidebar:
    st.title('Configuration Settings')

    st.subheader('Proxy Settings')
    proxy_input = st.text_input('Proxy URL', config['proxy'], key='proxy_input')
    if proxy_input != config['proxy']:
      update_config('proxy_list', [proxy_input])
      st.success('Proxy updated in config.yaml')

    st.subheader('Download Directory')
    download_dir_input = st.text_input('Download Directory', config['download_dir'], key='download_dir_input')
    if download_dir_input != config['download_dir']:
      update_config('download_directory', download_dir_input)
      st.success('Download directory updated in config.yaml')

    st.subheader('yt-dlp Options')
    format_option = st.text_input('yt-dlp Format Options', str(config['ydl_opts']), key='format_option')
    if format_option != str(config['ydl_opts']):
      try:
        new_ydl_opts = eval(format_option)
        update_config('yt_dlp_options', new_ydl_opts)
        st.success('yt-dlp options updated in config.yaml')
      except BaseException:
        st.error('Invalid yt-dlp options format. Please enter a valid Python dictionary.')

  url = st.text_input('Enter the video URL', '')

  if url:
    platform = is_valid_url(url)
    if platform:
      st.write(f'Fetching video information for {platform}...')

      downloader = Downloader(url, config['proxy'], config['download_dir'], config['ydl_opts'])
      formats, title, description = downloader.get_video_formats()

      if formats:
        st.subheader('Video Title')
        #  if config langconvert == zh-cn

        if config['langconvert'] == 'zh-cn':
          title = zhconv.convert(title, 'zh-cn')
          st.write(title)
        else:
          st.write(title)

        st.subheader('Video Description')
        if config['langconvert'] == 'zh-cn':
          description = zhconv.convert(description, 'zh-cn')
          st.write(description)
        else:
          st.write(description)
        st.write('Available formats:')

        # Use filter_formats here
        video_formats = filter_formats(formats, platform, video=True)
        audio_formats = filter_formats(formats, platform, video=False)

        st.write('Video Formats:')
        video_format_options = [get_format_details(f) for f in video_formats]
        video_selections = {f: st.checkbox(f, key=f) for f in video_format_options}

        st.write('Audio Formats:')
        audio_format_options = [get_format_details(f) for f in audio_formats]
        audio_selections = {f: st.checkbox(f, key=f) for f in audio_format_options}

        if any(video_selections.values()) or any(audio_selections.values()):
          st.write('You can download the selected formats by clicking the Download button.')
          st.write(
            'You can also download and merge the selected video and audio formats by clicking the Download and Merge button.'
          )

        # make buttons inline

        c = st.container()
        if c.button('Download', key='download_button'):
          for selected_format, is_selected in video_selections.items():
            if is_selected:
              format_code = selected_format.split(' - ')[0]
              format_ext = selected_format.split(' - ')[1].split(',')[0].lower()
              downloader.download_video(title, format_ext, format_code)

          for selected_format, is_selected in audio_selections.items():
            if is_selected:
              format_code = selected_format.split(' - ')[0]
              format_ext = selected_format.split(' - ')[1].split(',')[0].lower()
              downloader.download_video(title, format_ext, format_code)

        # Check if both video and audio are selected for merging
        selected_video_format = next((f for f in video_selections if video_selections[f]), None)
        selected_audio_format = next((f for f in audio_selections if audio_selections[f]), None)
        if c.button('Download and Merge', key='merge_button'):
          if selected_video_format and selected_audio_format:
            video_format_code = selected_video_format.split(' - ')[0]
            audio_format_code = selected_audio_format.split(' - ')[0]
            try:
              with tempfile.TemporaryDirectory() as temp_dir:
                video_path = downloader.download_video(title, 'mp4', video_format_code)
                audio_path = downloader.download_video(title, 'm4a', audio_format_code)

                if video_path and audio_path:
                  merged_title = f'{downloader.get_title(title)}_merged.mp4'
                  output_path = os.path.join(config['download_dir'], merged_title)
                  if merge_video_audio(video_path, audio_path, output_path):
                    st.success(f'Video and audio merged successfully: {output_path}')
                  else:
                    st.error('Failed to merge video and audio.')
                else:
                  st.error('Failed to download video or audio.')
            except Exception as e:
              st.error(f'Error downloading and merging: {e}')
          else:
            st.error('Please select both a video and audio format to merge.')
            return

      else:
        st.error('No formats available for the provided URL.')
    else:
      st.error('Invalid URL. Please enter a valid YouTube or TikTok URL.')


if __name__ == '__main__':
  main()

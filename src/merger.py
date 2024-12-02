import subprocess
import streamlit as st


def merge_video_audio(video_path, audio_path, output_path):
  try:
    command = [
      'ffmpeg',
      '-i',
      video_path,
      '-i',
      audio_path,
      '-c:v',
      'copy',
      '-c:a',
      'aac',
      '-strict',
      'experimental',
      output_path,
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)
    return True
  except subprocess.CalledProcessError as e:
    st.error(f'Error merging video and audio: {e.stderr}')
    return False

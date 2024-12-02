import os
import yaml
import streamlit as st


def load_config():
  config_file = 'config.yaml'
  if os.path.exists(config_file):
    with open(config_file, 'r') as f:
      return yaml.safe_load(f)
  else:
    st.error(f'Config file {config_file} not found.')
    return {}


def update_config(key, value):
  config_file = 'config.yaml'
  config = load_config()
  config[key] = value
  with open(config_file, 'w') as f:
    yaml.dump(config, f)


def get_config():
  config = load_config()
  return {
    'proxy': config.get('proxy_list', ['http://127.0.0.1:7890'])[0],
    'download_dir': config.get('download_directory', 'output'),
    'langconvert': config.get('langconvert', 'zh-cn'),
    'ydl_opts': config.get('yt_dlp_options', {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True}),
  }

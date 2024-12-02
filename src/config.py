import os
import yaml
import streamlit as st

CONFIG_FILE = 'config.yaml'


def load_config():
  """Load the configuration from the YAML file."""
  if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
      return yaml.safe_load(f) or {}
  else:
    st.error(f'Config file {CONFIG_FILE} not found.')
    return {}


def save_config(config):
  """Save the configuration back to the YAML file."""
  with open(CONFIG_FILE, 'w') as f:
    yaml.dump(config, f, default_flow_style=False)


def get_nested_value(d, keys):
  """Get a value from a nested dictionary using a list of keys."""
  for key in keys:
    if not isinstance(d, dict) or key not in d:
      return None
    d = d[key]
  return d


def set_nested_value(d, keys, value):
  """Set a value in a nested dictionary using a list of keys."""
  for key in keys[:-1]:
    if key not in d or not isinstance(d[key], dict):
      d[key] = {}
    d = d[key]
  d[keys[-1]] = value


def update_config(key, value):
  """Update a specific key in the configuration."""
  config = load_config()
  keys = key.split('.')
  set_nested_value(config, keys, value)
  save_config(config)


def get_config():
  """Get the processed configuration with default values."""
  config = load_config()
  return {
    'proxy': get_nested_value(config, ['proxy']) or 'http://127.0.0.1:7890',
    'download_dir': get_nested_value(config, ['download_directory']) or 'output',
    'langconvert': get_nested_value(config, ['langconvert']) or 'zh-cn',
    'ydl_opts': get_nested_value(config, ['yt_dlp_options'])
    or {'format': 'bestvideo+bestaudio/best', 'noplaylist': True, 'quiet': True},
  }

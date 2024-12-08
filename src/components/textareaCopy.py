import streamlit as st
import random

def textarea_copy(text: str):
  # Define the HTML and CSS for the floating copy button and textarea
  st.text_area("", text, height=200)

def input_copy(text: str):
  # Define the HTML and CSS for the floating copy button and input
  st.text_input("", text)

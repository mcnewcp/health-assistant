import os
import streamlit as st

# initialize env vars if local
if os.getenv("ENV", "local") != "streamlit_cloud":
    from dotenv import load_dotenv
    load_dotenv()


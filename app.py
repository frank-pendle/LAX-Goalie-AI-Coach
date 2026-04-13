import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import os
import re
from datetime import datetime
from google.cloud import storage
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="LAX Goalie AI Coach",
    page_icon="🥍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- GCP Configuration ---
# Authenticate to GCS using Streamlit's secrets
try:
    gcp_service_account_info = st.secrets["gcp_service_account"]
    credentials = storage.Client.from_service_account_info(gcp_service_account_info)
    # Specify your bucket name here
    BUCKET_NAME = "lax-goalie-videos-frank" # IMPORTANT: Change this to your unique bucket name
    bucket = credentials.bucket(BUCKET_NAME)
    GCS_ENABLED = True
except (KeyError, FileNotFoundError):
    GCS_ENABLED = False
    st.error("Google Cloud Storage credentials not found. Please configure your secrets.")

# --- State Management ---
if 'video_files' not in st.session_state:
    st.session_state.video_files = {} # Will now store GCS paths
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'analysis_in_progress' not in st.session_state:
    st.session_state.analysis_in_progress = False
if 'action_map' not in st.session_state:
    st.session_state.action_map = []

# --- UI Styling (Same as before) ---
def load_css():
    st.markdown("""
    <style>
        /* ... CSS from the previous version ... */
    </style>
    """, unsafe_allow_html=True)

# --- AI & Analysis Functions (Same as before) ---
def run_computer_vision_analysis(video_files):
    # ...
    return []
def generate_ai_critique(action_map):
    # ...
    return {}
def generate_report_text(results, action_map):
    # ...
    return ""

# --- UI Rendering Functions (with modifications for GCS) ---
def display_video_gallery():
    st.header("🎬 Video Gallery & Analysis")
    if not st.session_state.video_files:
        st.info("Upload one or more videos to begin your analysis.")
    
    video_keys_to_delete = []
    
    for gcs_path, video_data in st.session_state.video_files.items():
        with st.container():
            st.markdown('<div class="video-card">', unsafe_allow_html=True)
            if st.button("✖", key=f"del_{gcs_path}"):
                video_keys_to_delete.append(gcs_path)
            st.subheader(video_data['name'])
            # Generate a temporary signed URL to stream the video for viewing
            try:
                blob = bucket.blob(gcs_path)
                signed_url = blob.generate_signed_url(version="v4", expiration=timedelta(minutes=15), method="GET")
                st.video(signed_url)
            except Exception as e:
                st.error(f"Could not load video. Error: {e}")
            
            st.markdown('</div>', unsafe_allow_html=True)

    if video_keys_to_delete:
        for gcs_path in video_keys_to_delete:
            if gcs_path in st.session_state.video_files:
                try:
                    blob = bucket.blob(gcs_path)
                    blob.delete()
                except Exception as e:
                    st.error(f"Error deleting file from cloud: {e}")
                del st.session_state.video_files[gcs_path]
        st.rerun()

def display_analysis_dashboard(results, report_data):
    # ... (Same as before)
    pass
def display_charts(results):
    # ... (Same as before)
    pass
def display_detailed_critique(results, action_map):
    # ... (Same as before)
    pass
def display_summary_and_next_steps(results):
    # ... (Same as before)
    pass

# --- Main App Logic ---
def main():
    load_css()
    st.title("🥍 LAX Goalie AI Coach")
    st.caption("Elite Video Analysis powered by The Lax Goalie Bible")

    tab1, tab2 = st.tabs(["▶️ Video Management & Analysis", "⚙️ Knowledge Base"])

    with tab1:
        st.header("Upload New Video")
        if GCS_ENABLED:
            st.markdown("This app supports large video files (2GB+) via Google Cloud Storage.")
            uploaded_files = st.file_uploader(
                "Upload Goalie Videos", 
                type=["mp4", "mov", "avi", "mpeg4"], 
                accept_multiple_files=True, 
                label_visibility="collapsed"
            )
            
            if uploaded_files:
                with st.spinner("Uploading videos to secure cloud storage..."):
                    for uploaded_file in uploaded_files:
                        gcs_path = f"uploads/{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
                        
                        if gcs_path not in st.session_state.video_files:
                            try:
                                blob = bucket.blob(gcs_path)
                                # Stream upload for large files
                                blob.upload_from_file(uploaded_file, content_type=uploaded_file.type)
                                st.session_state.video_files[gcs_path] = {'name': uploaded_file.name, 'gcs_path': gcs_path}
                            except Exception as e:
                                st.error(f"Upload for {uploaded_file.name} failed: {e}")
                st.success("Video(s) added to the gallery below!")
                # st.rerun() # Use with caution, can cause loops

        else:
            st.error("GCS is not configured, so file uploads are disabled.")

        display_video_gallery()
        
        if st.session_state.video_files and not st.session_state.analysis_in_progress:
            st.markdown("---")
            if st.button("🚀 Analyze Performance for All Videos", use_container_width=True, type="primary"):
                st.session_state.analysis_results = None
                st.session_state.analysis_in_progress = True
                st.rerun()

        # ... (Rest of the analysis progress bar logic is the same as before) ...

        if st.session_state.analysis_results:
            st.markdown("---")
            report_data = generate_report_text(st.session_state.analysis_results, st.session_state.action_map)
            display_analysis_dashboard(st.session_state.analysis_results, report_data)
            # ... and so on

    with tab2:
        # ... (Knowledge base tab logic is the same as before) ...
        pass

if __name__ == "__main__":
    main()

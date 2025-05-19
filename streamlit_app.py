import streamlit as st
import os
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
from utils.preprocess import preprocess_fingerprint
from utils.extract_features import extract_features
from utils.match_fingerprint import match_fingerprint

# Configure page
st.set_page_config(
    page_title="Fingerprint Matching System",
    page_icon="👆",
    layout="wide"
)

# Create necessary directories
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
RESULTS_FOLDER = os.path.join(BASE_DIR, 'results')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Constants
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Main app
st.title("👆 Fingerprint Matching System")

# File upload section
st.header("Upload Fingerprints")
col1, col2 = st.columns(2)

with col1:
    st.subheader("First Fingerprint")
    file1 = st.file_uploader("Upload first fingerprint", type=list(ALLOWED_EXTENSIONS), key="fp1")
    if file1:
        st.image(file1, caption="First Fingerprint Preview", use_container_width=True)

with col2:
    st.subheader("Second Fingerprint")
    file2 = st.file_uploader("Upload second fingerprint", type=list(ALLOWED_EXTENSIONS), key="fp2")
    if file2:
        st.image(file2, caption="Second Fingerprint Preview", use_container_width=True)

# Process button
if st.button("Compare Fingerprints", type="primary"):
    if file1 and file2:
        try:
            # Generate unique filenames
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            
            filename1 = f"{timestamp}_{unique_id}_1_{secure_filename(file1.name)}"
            filename2 = f"{timestamp}_{unique_id}_2_{secure_filename(file2.name)}"
            
            # Save files
            file1_path = os.path.join(UPLOAD_FOLDER, filename1)
            file2_path = os.path.join(UPLOAD_FOLDER, filename2)
            
            with open(file1_path, "wb") as f:
                f.write(file1.getbuffer())
            with open(file2_path, "wb") as f:
                f.write(file2.getbuffer())
            
            # Process fingerprints
            with st.spinner("Processing fingerprints..."):
                match_score, kp1_count, kp2_count, good_matches_count, match_filename, minutiae1_filename, minutiae2_filename, sourceafis_score = match_fingerprint(
                    file1_path, file2_path, RESULTS_FOLDER
                )
            
            # Display results
            st.header("Results")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Match Score", f"{match_score:.2f}%")
                st.metric("SourceAFIS Score", f"{sourceafis_score:.2f}%")
            
            with col2:
                st.metric("Keypoints in First Image", kp1_count)
                st.metric("Keypoints in Second Image", kp2_count)
                st.metric("Good Matches", good_matches_count)
            
            # Display result images
            if match_filename and minutiae1_filename and minutiae2_filename:
                st.header("Visualization")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.image(os.path.join(RESULTS_FOLDER, minutiae1_filename), 
                            caption="First Fingerprint Features", use_container_width=True)
                with col2:
                    st.image(os.path.join(RESULTS_FOLDER, match_filename), 
                            caption="Matching Results", use_container_width=True)
                with col3:
                    st.image(os.path.join(RESULTS_FOLDER, minutiae2_filename), 
                            caption="Second Fingerprint Features", use_container_width=True)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please upload both fingerprint images to proceed.")

# Add footer
st.markdown("---")
st.markdown("### About")
st.markdown("""
This application uses advanced image processing and machine learning techniques to compare and match fingerprints.
The system analyzes key features and patterns in the fingerprints to determine the match score.
""") 
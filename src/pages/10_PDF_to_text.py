import streamlit as st
import os


class Config:
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

def ensure_upload_dir():
    if not os.path.exists(Config.UPLOAD_DIR):
        os.makedirs(Config.UPLOAD_DIR)

def save_file(uploaded_file, file_path):
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

def file_uploader_change():
    st.session_state["files_processed"] = False

def upload_pdf():
    ensure_upload_dir()
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        on_change=file_uploader_change, 
        accept_multiple_files=True
    )

    if uploaded_files and not st.session_state.get("files_processed"):
        files_saved = False
        for uploaded_file in uploaded_files:
            file_path = os.path.join(Config.UPLOAD_DIR, uploaded_file.name)
            save_file(uploaded_file, file_path)
        st.session_state["files_processed"] = True
        st.rerun()

def manage_pdf():
    ensure_upload_dir()
    with st.sidebar:
        st.title("Manage files")
        files = os.listdir(Config.UPLOAD_DIR)

        if not files:
            st.write("No files found")
            return

        select_all = st.checkbox("Select all files")
        file_dict = {file: st.checkbox(file, value=select_all, key=file) for file in files}

        if st.button("Remove selected files"):
            for file, is_checked in file_dict.items():
                if is_checked:
                    os.remove(os.path.join(Config.UPLOAD_DIR, file))
                    st.success(f"Removed: {file}")

            st.rerun()

if __name__ == "__main__":
    if "files_processed" not in st.session_state:
        st.session_state["files_processed"] = False
    manage_pdf()
    upload_pdf()


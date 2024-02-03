import streamlit as st
import os
from PyPDF2 import PdfReader


class Config:
    UPLOAD_EXTENSIONS = "pdf"
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    TEXT_DIR = os.getenv("TEXT_DIR", UPLOAD_DIR + "/extracted_text")


def upload_pdf():
    ensure_upload_dir()
    with st.form("upload", clear_on_submit=True):
        files = st.file_uploader(
            "Choose PDF files",
            type=Config.UPLOAD_EXTENSIONS,
            accept_multiple_files=True,
        )

        upload = st.form_submit_button("Upload")
        if upload:
            if files:
                for uploaded_file in files:
                    pdf_file = os.path.join(Config.UPLOAD_DIR, uploaded_file.name)
                    save_pdf_file(uploaded_file, pdf_file)
            else:
                st.error("No files to upload")


def ensure_upload_dir():
    if not os.path.exists(Config.UPLOAD_DIR):
        os.makedirs(Config.UPLOAD_DIR)
    if not os.path.exists(Config.TEXT_DIR):
        os.makedirs(Config.TEXT_DIR)


def save_pdf_file(uploaded_file, file_path):
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())


def manage_pdf():
    with st.sidebar:
        st.title("Manage files")

        if "select_all" not in st.session_state:
            st.session_state["select_all"] = False

        files = get_files_by_extension()
        if not files:
            st.write("No files found")
            return

        with st.form("manage_files", clear_on_submit=True):
            file_dict = {
                file: st.checkbox(file, value=st.session_state["select_all"], key=file)
                for file in files
            }

            delete = st.form_submit_button("Delete")
            if delete:
                delete_files(file_dict)

        st.checkbox(
            "Select all files",
            key="select_all_toggle",
            on_change=lambda: st.session_state.update(
                select_all=not st.session_state["select_all"]
            ),
        )


def get_files_by_extension():
    all_files = os.listdir(Config.UPLOAD_DIR)
    return [
        file for file in all_files if file.lower().endswith(Config.UPLOAD_EXTENSIONS)
    ]


def delete_files(file_dict):
    for file, is_checked in file_dict.items():
        if is_checked:
            os.remove(os.path.join(Config.UPLOAD_DIR, file))
    st.session_state["select_all"] = False
    st.rerun()


if __name__ == "__main__":
    upload_pdf()
    manage_pdf()

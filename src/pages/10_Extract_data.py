import streamlit as st
from PIL import Image
from Config import Config
from components.reader.save_text import (
    ensure_data_dir,
    extracted_text_already_exists,
    save_file_to_text,
    get_text_file_path,
    delete_extracted_text,
    get_extracted_data,
    delete_extracted_text_dict,
)
from components.reader.extract_text import extract_text

image = Image.open(Config.logo_small_path)
st.set_page_config(
    page_title="Read text from uploads",
    page_icon=image,
    layout="wide",
    initial_sidebar_state="auto",
)


def upload_files():
    ensure_data_dir()
    with st.form("upload", clear_on_submit=True):
        files = st.file_uploader(
            "Select files",
            type=Config.UPLOAD_EXTENSIONS,
            accept_multiple_files=True,
            disabled=st.session_state.get("upload_disabled", False),
        )

        upload = st.form_submit_button(
            "Upload",
            on_click=lambda: st.session_state.update(upload_disabled=True),
            disabled=st.session_state.get("upload_disabled", False),
        )

        if upload:
            if not files:
                st.error("No files to upload")
                return

            for uploaded_file in files:
                if extracted_text_already_exists(uploaded_file.name):
                    st.warning(
                        f"Skipped: '{uploaded_file.name}'. Extract already exist."
                    )
                    continue
                try:
                    with st.spinner(text=f"Extracting text from {uploaded_file.name}"):
                        text = extract_text(uploaded_file)
                    save_file_to_text(text, get_text_file_path(uploaded_file.name))
                    st.info(f"Done: '{uploaded_file.name}'")
                except Exception as e:
                    delete_extracted_text(uploaded_file.name)
                    st.error(f"Failed to process: '{uploaded_file.name}'. Error: {e}")

    if st.session_state.get("upload_disabled", False):
        if st.button("Clear"):
            st.session_state["upload_disabled"] = False
            st.rerun()


def manage_extracted_text():
    with st.sidebar:
        st.title("Manage extracted data")

        files = get_extracted_data()
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
                delete_extracted_text_dict(file_dict)
                st.session_state["select_all"] = False
                st.session_state["upload_disabled"] = False
                st.rerun()

        st.checkbox(
            "Select all files",
            key="select_all_toggle",
            on_change=lambda: st.session_state.update(
                select_all=not st.session_state["select_all"]
            ),
        )


if __name__ == "__main__":
    if "select_all" not in st.session_state:
        st.session_state["select_all"] = False
    if "upload_disabled" not in st.session_state:
        st.session_state["upload_disabled"] = False

    upload_files()
    manage_extracted_text()

import streamlit as st
from PIL import Image
from Config import Config
from Extract_text import (
    ensure_upload_dir,
    file_already_exists,
    save_pdf_file,
    extract_text,
    save_text_file,
    get_pdf_file_path,
    get_text_file_path,
    delete_file_and_extracted_text,
    get_files_upload_dir_by_extension,
    delete_files,
)

image = Image.open(Config.logo_small_path)
st.set_page_config(
    page_title="Extract text from uploads",
    page_icon=image,
    layout="wide",
    initial_sidebar_state="auto",
)


def upload_pdfs():
    ensure_upload_dir()
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
                if file_already_exists(uploaded_file.name):
                    st.warning(
                        f"Skipped: '{uploaded_file.name}'. A file already exists in some format."
                    )
                    continue
                pdf_file_path = get_pdf_file_path(uploaded_file.name)
                save_pdf_file(uploaded_file, pdf_file_path)
                try:
                    with st.spinner(text=f"Extracting text from {uploaded_file.name}"):
                        text = extract_text(uploaded_file)
                    save_text_file(text, get_text_file_path(uploaded_file.name))
                    st.info(f"Done: '{uploaded_file.name}'")
                except Exception as e:
                    delete_file_and_extracted_text(uploaded_file.name, True)
                    st.error(f"Failed to process: '{uploaded_file.name}'. Error: {e}")

    if st.session_state.get("upload_disabled", False):
        if st.button("Clear"):
            st.session_state["upload_disabled"] = False
            st.rerun()


def manage_pdfs():
    with st.sidebar:
        st.title("Manage files")

        files = get_files_upload_dir_by_extension()
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
                delete_files(
                    file_dict, st.session_state.get("delete_extracted_text", False)
                )
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

        st.checkbox(
            "Also delete extracted text",
            key="delete_tekst",
            value=st.session_state["delete_extracted_text"],
            on_change=lambda: st.session_state.update(
                delete_extracted_text=not st.session_state["delete_extracted_text"]
            ),
        )


if __name__ == "__main__":
    if "select_all" not in st.session_state:
        st.session_state["select_all"] = False
    if "delete_extracted_text" not in st.session_state:
        st.session_state["delete_extracted_text"] = False
    if "upload_disabled" not in st.session_state:
        st.session_state["upload_disabled"] = False

    upload_pdfs()
    manage_pdfs()

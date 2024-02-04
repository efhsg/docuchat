import streamlit as st
import os
from Config import Config
from PyPDF2 import PdfReader


def upload_pdfs():
    ensure_upload_dir()
    with st.form("upload", clear_on_submit=True):
        files = st.file_uploader(
            "Select files",
            type=Config.UPLOAD_EXTENSIONS,
            accept_multiple_files=True,
            disabled=st.session_state["upload_disabled"],
        )

        upload = st.form_submit_button(
            "Upload",
            on_click=lambda: st.session_state.update(upload_disabled=True),
            disabled=st.session_state["upload_disabled"],
        )

        if upload:
            if not files:
                st.error("No files to upload")
                return

            for uploaded_file in files:
                if file_already_exists(uploaded_file.name):
                    st.warning(
                        f"Skipped: '{uploaded_file.name}'. A file already exists in some format"
                    )
                    continue
                pdf_file_path = get_pdf_file_path(uploaded_file.name)
                save_pdf_file(uploaded_file, pdf_file_path)
                success, text = extract_text(uploaded_file)
                if not success:
                    delete_file_and_extracted_text(uploaded_file.name, True)
                    continue
                save_text_file(text, get_text_file_path(uploaded_file.name))

    if st.session_state["upload_disabled"]:
        if st.button("Clear"):
            st.session_state["upload_disabled"] = False
            st.rerun()


def file_already_exists(file_name):
    base_name = os.path.splitext(file_name)[0]
    return any(f.startswith(base_name) for f in get_files_upload_dir_by_extension())


def ensure_upload_dir():
    if not os.path.exists(Config.UPLOAD_DIR):
        os.makedirs(Config.UPLOAD_DIR)
    if not os.path.exists(Config.TEXT_DIR):
        os.makedirs(Config.TEXT_DIR)


def save_pdf_file(uploaded_file, file_path):
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())


def extract_text(uploaded_file):
    file_extension = uploaded_file.name.split(".")[-1].lower()
    extractors = {
        "pdf": extract_text_from_pdf,
        "txt": extract_text_from_txt,
    }

    if file_extension in extractors:
        try:
            with st.spinner(text=f"Extracting text from {uploaded_file.name}"):
                text = extractors[file_extension](uploaded_file)
                st.info(f"Done: '{uploaded_file.name}'")
                return True, text
        except Exception as e:
            st.error(f"Failed to process: '{uploaded_file.name}'. Error: {e}")
            return False, ""
    else:
        st.warning(f"File type '{file_extension}' is not supported.")
        return False, ""


def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "".join(page.extract_text() or "" for page in reader.pages)


def extract_text_from_txt(uploaded_file):
    return uploaded_file.getvalue().decode("utf-8")


def save_text_file(text, file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)


def get_pdf_file_path(file_name):
    return os.path.join(Config.UPLOAD_DIR, file_name)


def get_text_file_path(file_name):
    file_name_without_extension = file_name.rsplit(".", 1)[0]
    return os.path.join(Config.TEXT_DIR, file_name_without_extension + ".txt")


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
                delete_files(file_dict)

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


def get_files_upload_dir_by_extension():
    all_files = os.listdir(Config.UPLOAD_DIR)
    return [
        file for file in all_files if file.lower().endswith(Config.UPLOAD_EXTENSIONS)
    ]


def delete_files(file_dict):
    for file, is_checked in file_dict.items():
        if is_checked:
            delete_file_and_extracted_text(
                file, st.session_state.get("delete_extracted_text", False)
            )
    st.session_state["select_all"] = False
    st.rerun()


def delete_file_and_extracted_text(file_name, delete_text):
    try:
        os.remove(os.path.join(Config.UPLOAD_DIR, file_name))
    except FileNotFoundError:
        pass

    if delete_text:
        try:
            os.remove(get_text_file_path(file_name))
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    if "select_all" not in st.session_state:
        st.session_state["select_all"] = False
    if "delete_extracted_text" not in st.session_state:
        st.session_state["delete_extracted_text"] = False
    if "upload_disabled" not in st.session_state:
        st.session_state["upload_disabled"] = False

    upload_pdfs()
    manage_pdfs()

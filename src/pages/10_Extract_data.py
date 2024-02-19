import streamlit as st
from PIL import Image
from config import Config
from injector import get_reader_repository, get_text_extractor

config = Config()
reader_repository = get_reader_repository()
text_extractor = get_text_extractor()

image = Image.open(config.logo_small_path)
st.set_page_config(
    page_title="Read text from uploads",
    page_icon=image,
    layout="wide",
    initial_sidebar_state="auto",
)

if "select_all" not in st.session_state:
    st.session_state["select_all"] = False
if "uploading" not in st.session_state:
    st.session_state["uploading"] = False


selected_domain = st.sidebar.radio(
    "Select Domain",
    options=[config.default_domain_name]
    + reader_repository.list_domains_without_default(),
    index=0,
    on_change=lambda: st.session_state.update(select_all=False),
    disabled=st.session_state.get("uploading", False),
)


with st.sidebar:
    st.title("Extracted to domain")
    files = reader_repository.list_text_names_by_domain(selected_domain)
    if not files:
        st.write("No files found")
    else:
        with st.form("manage_files", clear_on_submit=True):
            file_dict = {
                file: st.checkbox(
                    file,
                    value=st.session_state["select_all"],
                    key=file,
                    disabled=st.session_state.get("uploading", False),
                )
                for file in files
            }
            delete = st.form_submit_button(
                "Delete", disabled=st.session_state.get("uploading", False)
            )
            if delete:
                texts_to_delete = [
                    file_name
                    for file_name, is_checked in file_dict.items()
                    if is_checked
                ]
                if texts_to_delete:
                    reader_repository.delete_texts(texts_to_delete)
                    for text in texts_to_delete:
                        if text in st.session_state:
                            del st.session_state[text]
                    st.rerun()

        st.checkbox(
            "Select all files",
            key="select_all_toggle",
            on_change=lambda: st.session_state.update(
                select_all=not st.session_state["select_all"]
            ),
            value=st.session_state["select_all"],
            disabled=st.session_state.get("uploading", False),
        )


with st.form("upload", clear_on_submit=True):
    st.subheader(selected_domain)

    files = st.file_uploader(
        "Select files",
        type=config.upload_extensions,
        accept_multiple_files=True,
        disabled=st.session_state.get("uploading", False),
    )
    upload = st.form_submit_button(
        "Upload",
        on_click=lambda: st.session_state.update(uploading=True),
        disabled=st.session_state.get("uploading", False),
    )
    if upload:
        if not files:
            st.session_state["uploading"] = False
            st.rerun()
        for uploaded_file in files:
            if reader_repository.text_exists(uploaded_file.name, selected_domain):
                st.warning(
                    f"Skipped: '{uploaded_file.name}'. Extracted text already exist."
                )
                continue
            try:
                with st.spinner(text=f"Extracting text from {uploaded_file.name}"):
                    text = text_extractor.extract_text(uploaded_file)
                reader_repository.save_text(text, uploaded_file.name, selected_domain)
                st.info(f"Done: '{uploaded_file.name}'")
            except Exception as e:
                st.error(f"Failed to process: '{uploaded_file.name}'. Error: {e}")

if st.session_state.get("uploading", False):
    if st.button("Ok"):
        st.session_state["uploading"] = False
        st.rerun()

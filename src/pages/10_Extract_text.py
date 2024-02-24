import streamlit as st
from injector import get_config, get_reader_repository, get_text_extractor, get_logger
from pages.utils.extracted_data import manage_extracted_data
from pages.utils.utils import set_default_state, setup_page

config = get_config()
reader_repository = get_reader_repository()
text_extractor = get_text_extractor()
logger = get_logger()


def setup_session_state() -> None:
    set_default_state("select_all", False)
    set_default_state("uploading", False)
    set_default_state("messages", [])
    set_default_state("message_counts", {})
    set_default_state("total_files", 0)
    set_default_state("show_details", False)


def add_message(message, message_type):
    st.session_state["messages"].append({"text": message, "type": message_type})
    if message_type in st.session_state["message_counts"]:
        st.session_state["message_counts"][message_type] += 1
    else:
        st.session_state["message_counts"][message_type] = 1
    if message_type == "error":
        st.error(message)
    elif message_type == "warning":
        st.warning(message)
    elif message_type == "info":
        st.info(message)


def display_summary():
    extracted = st.session_state["message_counts"].get("info", 0)
    warnings = st.session_state["message_counts"].get("warning", 0)
    errors = st.session_state["message_counts"].get("error", 0)
    total = st.session_state["total_files"]
    st.write(
        f"Total files: {total}, Files extracted: {extracted}, Warnings: {warnings}, Errors: {errors}"
    )

    col1, col2 = st.columns([1, 12])
    with col1:
        if st.button("Clear"):
            clear_messages()
            st.rerun()
    with col2:
        if not st.session_state.get("show_details"):
            if st.button("Show details"):
                st.session_state["show_details"] = True
                st.rerun()

    if st.session_state.get("show_details", False):
        display_messages(st.session_state["messages"])


def display_messages(messages):
    ordered_messages = sorted(
        messages, key=lambda x: {"error": 0, "warning": 1, "info": 2}[x["type"]]
    )
    for message in ordered_messages:
        if message["type"] == "error":
            st.error(message["text"])
        elif message["type"] == "warning":
            st.warning(message["text"])
        elif message["type"] == "info":
            st.info(message["text"])


def clear_messages():
    st.session_state["messages"] = []
    st.session_state["message_counts"] = {"info": 0, "warning": 0, "error": 0}
    st.session_state["total_files"] = 0
    st.session_state["show_details"] = False


def get_domains():
    return reader_repository.list_domains()


def select_domain():
    selected_domain = st.sidebar.selectbox(
        "Select Domain",
        get_domains(),
        index=0,
        disabled=st.session_state.get("uploading", False),
    )

    if selected_domain and selected_domain != st.session_state.get(
        "last_selected_domain"
    ):
        st.session_state.update(select_all=False, last_selected_domain=selected_domain)
        st.rerun()
    return selected_domain


def extracted_data(selected_domain):
    with st.sidebar:
        manage_extracted_data(
            reader_repository,
            selected_domain,
            uploading=st.session_state.get("uploading", False),
        )


def upload_files(selected_domain):
    with st.form("upload", clear_on_submit=True):
        st.subheader(selected_domain)
        files = st.file_uploader(
            "Select files",
            type=config.upload_extensions,
            accept_multiple_files=True,
            disabled=st.session_state.get("uploading", False)
            or st.session_state["total_files"] > 0,
        )
        upload = st.form_submit_button(
            "Upload",
            on_click=lambda: st.session_state.update(uploading=True),
            disabled=st.session_state.get("uploading", False)
            or st.session_state["total_files"] > 0,
        )
        if upload:
            clear_messages()
            upload_progress = st.progress(0)
            if not files:
                st.session_state["uploading"] = False
                st.rerun()
            total_files = len(files)
            st.session_state["total_files"] = total_files
            for i, uploaded_file in enumerate(files):
                upload_progress.progress((i + 1) / total_files)
                if reader_repository.text_exists(uploaded_file.name, selected_domain):
                    add_message(
                        f"Skipped: '{uploaded_file.name}'. Extracted text already exists.",
                        "warning",
                    )
                    continue
                with st.spinner(text=f"Extracting text from {uploaded_file.name}"):
                    try:
                        text = text_extractor.extract_text(uploaded_file)
                        reader_repository.save_text(
                            text, uploaded_file.name, selected_domain
                        )
                        add_message(f"Done: '{uploaded_file.name}'", "info")
                    except Exception as e:
                        add_message(
                            f"Failed to process: '{uploaded_file.name}'. Error: {e}",
                            "error",
                        )
            st.session_state["select_all"] = False
            st.session_state["uploading"] = False
            st.rerun()


def show_summary():
    if not st.session_state.uploading and st.session_state.total_files > 0:
        display_summary()


def main():
    setup_page()
    setup_session_state()
    selected_domain = select_domain()
    extracted_data(selected_domain)
    upload_files(selected_domain)
    show_summary()


if __name__ == "__main__":
    main()

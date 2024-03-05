from typing import List
from urllib.parse import urlparse
import streamlit as st
from injector import (
    get_config,
    get_reader_repository,
    get_text_extractor,
    get_logger,
    get_web_extractor,
)
from pages.utils.extracted_data import manage_extracted_data
from pages.utils.utils import (
    get_index,
    set_default_state,
    setup_page,
    split_filename,
    select_domain,
    url_to_name_and_extension,
)

config = get_config()
reader_repository = get_reader_repository()
text_extractor = get_text_extractor()
web_extractor = get_web_extractor()
logger = get_logger()


def main():
    setup_page()
    setup_session_state()
    selected_domain = select_domain(reader_repository.list_domains())
    if selected_domain is None:
        st.info("First add a domain")
        return
    manage_extracted(selected_domain)
    extract(selected_domain)


def setup_session_state() -> None:
    DEFAULT_SESSION_STATES = [
        ("context_domain", None),
        ("context_source_type", None),
        ("select_all_texts", False),
        ("uploading", False),
        ("messages", []),
        ("message_counts", {}),
        ("total_files", 0),
        ("show_details", False),
    ]

    for state_name, default_value in DEFAULT_SESSION_STATES:
        set_default_state(state_name, default_value)


def manage_extracted(selected_domain):
    with st.sidebar:
        manage_extracted_data(
            reader_repository,
            selected_domain,
            uploading=st.session_state.get("uploading", False),
        )


def upload_files(selected_domain: str) -> None:
    files = upload_form(selected_domain)
    show_summary()
    if st.session_state.get("uploading", False):
        upload_progress = st.progress(0)
        if not files:
            st.session_state["uploading"] = False
            st.rerun()

        total_files = len(files)
        st.session_state["total_files"] = total_files

        for i, uploaded_file in enumerate(files):
            file_name, file_extension = split_filename(uploaded_file)
            upload_progress.progress((i + 1) / total_files)

            if reader_repository.text_exists(
                selected_domain, file_name, file_extension
            ):
                add_message(
                    f"Skipped: '{uploaded_file.name}'. Extracted text already exists.",
                    "warning",
                )
                continue

            with st.spinner(f"Extracting text from {uploaded_file.name}"):
                try:
                    text = text_extractor.extract_text(uploaded_file)
                    reader_repository.save_text(
                        selected_domain,
                        file_name,
                        file_extension,
                        uploaded_file.name,
                        text,
                    )
                    add_message(f"Done: '{uploaded_file.name}'", "info")
                except Exception as e:
                    add_message(
                        f"Failed to process: '{uploaded_file.name}'. Error: {e}",
                        "error",
                    )

        st.session_state["select_all_texts"] = False
        st.session_state["uploading"] = False
        st.rerun()


def upload_form(selected_domain: str) -> List:
    with st.form("upload", clear_on_submit=True):
        st.subheader(selected_domain)

        def on_upload_click():
            clear_messages()
            st.session_state.update(uploading=True)

        files = st.file_uploader(
            "Select files",
            type=config.upload_extensions,
            accept_multiple_files=True,
            disabled=st.session_state.get("uploading", False),
        )
        st.form_submit_button(
            "Upload",
            on_click=on_upload_click,
            disabled=st.session_state.get("uploading", False),
        )

        return files


def scrape_website(selected_domain):
    url = scrape_website_form(selected_domain)
    show_summary()
    if st.session_state.get("uploading", False):
        with st.spinner(text=f"Scraping website {url}"):
            st.session_state["total_files"] = 1
            try:
                text = web_extractor.extract_text(url)
                if text:
                    file_name, file_extension = url_to_name_and_extension(url)
                    if reader_repository.text_exists(
                        selected_domain, file_name, file_extension
                    ):
                        add_message(
                            f"Skipped: '{file_name}.{file_extension}'. Extracted text already exists.",
                            "warning",
                        )
                    else:
                        try:
                            reader_repository.save_text(
                                selected_domain, file_name, file_extension, url, text
                            )
                            add_message(f"Done: '{file_name}'", "info")
                        except Exception as e:
                            add_message(
                                f"Failed to process: '{file_name}'. Error: {e}", "error"
                            )
                else:
                    add_message(f"Failed to scrape text from: '{url}'", "error")
            except Exception as e:
                add_message(f"Failed to scrape text from: '{url}'. Error: {e}", "error")
        st.session_state["uploading"] = False
        st.rerun()


def scrape_website_form(selected_domain):
    with st.form("scrape_website", clear_on_submit=True):
        st.subheader(selected_domain)

        def on_scrape_click():
            clear_messages()
            st.session_state.update(uploading=True)

        url = st.text_input(
            label="Enter the website",
            value="",
            disabled=st.session_state.get("uploading", False),
        )
        st.form_submit_button(
            label="Scrape",
            on_click=on_scrape_click,
            disabled=st.session_state.get("uploading", False),
        )

    return url


def extract(selected_domain):

    source_type_options = ("Upload Files", "Scrape Website")
    source_type = st.selectbox(
        label="Select action:",
        options=source_type_options,
        key="source_type",
        index=get_index(source_type_options, "context_source_type"),
        on_change=lambda: st.session_state.update(
            context_source_type=st.session_state["source_type"]
        ),
        disabled=st.session_state.get("uploading", False),
    )
    if source_type == "Upload Files":
        upload_files(selected_domain)
    elif source_type == "Scrape Website":
        scrape_website(selected_domain)


def add_message(message, message_type):
    st.session_state["messages"].append({"text": message, "type": message_type})
    st.session_state["message_counts"][message_type] = (
        st.session_state["message_counts"].get(message_type, 0) + 1
    )

    display_message(message, message_type)


def display_message(message: str, message_type: str) -> None:
    message_functions = {
        "error": st.error,
        "warning": st.warning,
        "info": st.info,
    }
    message_functions.get(message_type.lower(), st.write)(message)


def display_summary():
    with st.container(border=True):
        extracted = st.session_state["message_counts"].get("info", 0)
        warnings = st.session_state["message_counts"].get("warning", 0)
        errors = st.session_state["message_counts"].get("error", 0)
        total = st.session_state["total_files"]
        st.write(
            f"Total: {total}, Extracted: {extracted}, Warnings: {warnings}, Errors: {errors}"
        )

        col1, col2 = st.columns([1, 12])
        with col1:
            if st.button("OK"):
                clear_messages()
                st.rerun()
        with col2:
            if not st.session_state.get("show_details"):
                if st.button("Show details"):
                    st.session_state["show_details"] = True
                    st.rerun()

        if st.session_state.get("show_details", False):
            display_messages(st.session_state["messages"])
        else:
            display_errors(st.session_state["messages"])


def display_errors(messages):
    error_messages = filter(lambda x: x["type"] == "error", messages)
    for message in error_messages:
        display_message(message["text"], message["type"])


def display_messages(messages):
    ordered_messages = sorted(
        messages, key=lambda x: {"error": 0, "warning": 1, "info": 2}[x["type"]]
    )
    for message in ordered_messages:
        display_message(message["text"], message["type"])


def clear_messages():
    st.session_state["messages"] = []
    st.session_state["message_counts"] = {"info": 0, "warning": 0, "error": 0}
    st.session_state["total_files"] = 0
    st.session_state["show_details"] = False


def show_summary():
    if (
        not st.session_state.get("uploading", False)
        and st.session_state.total_files > 0
    ):
        display_summary()


if __name__ == "__main__":
    main()

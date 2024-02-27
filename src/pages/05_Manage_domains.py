import re
import streamlit as st
from components.database.models import Domain
from injector import get_logger, get_reader_repository
from pages.utils.extracted_data import manage_extracted_data
from pages.utils.utils import (
    set_default_state,
    setup_page,
    extracted_text_to_label,
    select_domain,
    filename_extension_to_label,
    show_messages,
)

reader_repository = get_reader_repository()
logger = get_logger()


def main():
    setup_page()
    setup_session_state()
    show_domains()
    with st.sidebar:
        show_messages()
    domain_creation_form()

    selected_domain = select_domain(reader_repository.list_domains())

    if selected_domain:
        domain_management_form(selected_domain)
        extracted_data(selected_domain)

    move_texts_between_domains()


def setup_session_state() -> None:

    DEFAULT_SESSION_STATES = [
        ("context_domain", None),
        ("show_domains", None),
        ("message", None),
        ("message_type", None),
        ("select_all_texts", False),
        ("source_domain", None),
        ("target_domain", None),
    ]
    for state_name, default_value in DEFAULT_SESSION_STATES:
        set_default_state(state_name, default_value)


def show_domains():
    with st.sidebar:
        with st.container(border=True):
            button_label = (
                "Hide Domains"
                if st.session_state.get("show_domains", False)
                else "Show Domains"
            )
            if st.button(label=button_label):
                st.session_state["show_domains"] = not st.session_state["show_domains"]
                st.rerun()

            if st.session_state.get("show_domains", False):
                existing_domains = get_existing_domains()
                if existing_domains:
                    with st.container(border=True):
                        for domain in existing_domains:
                            st.write(domain)
                else:
                    st.write("No domains available.")


def domain_creation_form():
    with st.sidebar:
        with st.form("create_domain_form", clear_on_submit=True):
            new_domain_name = st.text_input("Domain Name", key="create_domain_input")
            create_domain_button = st.form_submit_button("Create Domain")
            if create_domain_button:
                try:
                    reader_repository.create_domain(new_domain_name)
                    st.session_state["message"] = (
                        f"Domain '{new_domain_name}' created successfully!"
                    )
                    st.session_state["message_type"] = "success"
                    st.session_state["context_domain"] = new_domain_name
                except Exception as e:
                    st.session_state["message"] = str(e)
                    st.session_state["message_type"] = "error"
                st.rerun()


def get_existing_domains():
    return reader_repository.list_domains()


def domain_management_form(selected_domain):
    with st.sidebar.form("manage_domain_form", clear_on_submit=True):
        new_domain_name = st.text_input("New Domain Name ", key="update_domain_input")
        col1, col2 = st.columns([1, 2])
        with col1:
            update_domain_button = st.form_submit_button("Update")
        with col2:
            delete_domain_button = st.form_submit_button(label="🗑️ Delete")

    if delete_domain_button and selected_domain:
        try:
            reader_repository.delete_domain(selected_domain)
            st.session_state["message"] = (
                f"Domain '{selected_domain}' deleted successfully!"
            )
            st.session_state["message_type"] = "success"
            st.session_state["context_domain"] = None
            st.session_state["select_all_texts"] = False
        except Exception as e:
            st.session_state["message"] = str(e)
            st.session_state["message_type"] = "error"
        st.rerun()

    if update_domain_button and selected_domain and new_domain_name:
        try:
            reader_repository.update_domain(selected_domain, new_domain_name)
            st.session_state["message"] = f"Domain '{selected_domain}' updated to '{new_domain_name}' successfully!"
            st.session_state["message_type"] = "success"
            st.session_state["context_domain"] = new_domain_name
        except Exception as e:
            st.session_state["message"] = str(e)
            st.session_state["message_type"] = "error"
        st.rerun()


def extracted_data(selected_domain):
    if selected_domain:
        with st.sidebar:
            manage_extracted_data(
                reader_repository,
                selected_domain,
                uploading=st.session_state.get("uploading", False),
            )


def select_domain_texts(source_domain_texts, domain):
    return [
        (extracted_text.name, extracted_text.type)
        for extracted_text in source_domain_texts
        if st.checkbox(
            extracted_text_to_label(extracted_text),
            key=f"{domain}_{extracted_text_to_label(extracted_text)}",
        )
    ]


def display_domain_texts(domain):
    if domain:
        with st.container(border=True):
            extracted_texts = reader_repository.list_texts_by_domain(domain)
            for text in extracted_texts:
                st.text(extracted_text_to_label(text))


def move_texts(source_domain, target_domain, selected_texts):
    try:
        skipped_texts = reader_repository.move_text(
            source_domain, target_domain, selected_texts
        )
        if skipped_texts:
            st.session_state["skipped_texts"] = skipped_texts
        st.rerun()
    except Exception as e:
        st.error(f"Failed to move texts: {str(e)}")


def update_source_domain():
    st.session_state["source_domain"] = st.session_state["source_domain_selection"]


def update_target_domain():
    st.session_state["target_domain"] = st.session_state["target_domain_selection"]


def move_texts_between_domains():

    st.title("Move texts between domains")

    source_domain_options = reader_repository.list_domains_with_extracted_texts()

    if len(reader_repository.list_domains()) == 0:
        st.info("You can add domains in the side menu.")
        return

    if len(source_domain_options) == 0:
        st.info("You can 'Extract text' with the option in the side menu.")
        return

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            source_domain_index = (
                0
                if st.session_state["source_domain"] not in source_domain_options
                else source_domain_options.index(st.session_state["source_domain"])
            )
            st.session_state["source_domain"] = source_domain_options[
                source_domain_index
            ]
            source_domain_selection = st.selectbox(
                label="Select source domain",
                options=source_domain_options,
                key="source_domain_selection",
                index=source_domain_index,
                on_change=update_source_domain,
            )
            source_domain_texts = reader_repository.list_texts_by_domain(
                source_domain_selection
            )
            if len(source_domain_texts) > 0:
                selected_source_texts = select_domain_texts(
                    source_domain_texts, source_domain_selection
                )

        target_domain_options = [
            domain
            for domain in get_existing_domains()
            if domain != source_domain_selection
        ]

        with col2:
            target_domain_index = (
                0
                if st.session_state["target_domain"] not in target_domain_options
                else target_domain_options.index(st.session_state["target_domain"])
            )

            st.selectbox(
                "Select target domain",
                target_domain_options,
                index=target_domain_index,
                key="target_domain_selection",
                on_change=update_target_domain,
            )
            if target_domain_options:
                display_domain_texts(target_domain_options[target_domain_index])

        if len(source_domain_texts) > 0:
            if st.button("Move Selected Texts"):
                if not selected_source_texts:
                    st.error("Please select at least one text to move.")
                else:
                    move_texts(
                        source_domain_options[source_domain_index],
                        target_domain_options[target_domain_index],
                        selected_source_texts,
                    )

        if "skipped_texts" in st.session_state and st.session_state["skipped_texts"]:
            st.warning(
                "To move the following texts, delete them first from the target domain:"
            )
            skipped_list = "\n".join(
                f"- {filename_extension_to_label(text,extension)}"
                for text, extension in st.session_state["skipped_texts"]
            )
            st.markdown(skipped_list)
            del st.session_state["skipped_texts"]


if __name__ == "__main__":
    main()

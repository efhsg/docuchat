import re
from PIL import Image
import streamlit as st
from config import Config
from injector import get_logger, get_reader_repository, get_config
from pages.utils.extracted_data import manage_extracted_data
from pages.utils.utils import set_default_state, setup_page

config = get_config()
reader_repository = get_reader_repository()
logger = get_logger()


def setup_session_state() -> None:
    set_default_state("message", None)
    set_default_state("message_type", None)
    set_default_state("last_selected_domain", None)
    set_default_state("select_all", False)
    set_default_state("selected_domain", None)
    set_default_state("source_domain", None)
    set_default_state("target_domain", None)


def validate_domain_name(domain_name):
    if not domain_name.strip():
        return "Please enter a domain name.", "error"
    elif len(domain_name) > config.max_domain_name_length:
        return (
            f"Domain name must be {config.max_domain_name_length} characters or fewer.",
            "error",
        )
    elif not re.match(config.domain_name_pattern, domain_name):
        return (
            "Invalid domain name. Only letters, digits, spaces, and special characters (.@#$%^&*()_+?![]/{}<->) are allowed.",
            "error",
        )
    return None, "success"


def create_domain(domain_name):
    message, message_type = validate_domain_name(domain_name)
    if message_type == "error":
        return message, message_type
    try:
        reader_repository.create_domain(domain_name)
        return f"Domain '{domain_name}' created successfully!", "success"
    except Exception as e:
        return str(e), "error"


def update_domain(selected_domain, new_domain_name):
    message, message_type = validate_domain_name(new_domain_name)
    if message_type == "error":
        return message, message_type
    try:
        reader_repository.update_domain(selected_domain, new_domain_name)
        return (
            f"Domain '{selected_domain}' updated to '{new_domain_name}' successfully!",
            "success",
        )
    except Exception as e:
        return str(e), "error"


def show_messages():
    if st.session_state["message"]:
        if st.session_state["message_type"] == "success":
            st.sidebar.success(st.session_state["message"])
        elif st.session_state["message_type"] == "error":
            st.sidebar.error(st.session_state["message"])
        st.session_state["message"] = None


def domain_creation_form():
    with st.sidebar:
        with st.form("create_domain_form", clear_on_submit=True):
            new_domain_name = st.text_input("Domain Name", key="create_domain_input")
            create_domain_button = st.form_submit_button("Create Domain")
            if create_domain_button:
                message, message_type = create_domain(new_domain_name)
                st.session_state["message"] = message
                st.session_state["message_type"] = message_type
                if message_type == "success":
                    st.session_state["last_selected_domain"] = new_domain_name
                st.rerun()


def get_existing_domains():
    return reader_repository.list_domains()


def get_last_selected_index(existing_domains):
    last_selected_index = 0
    if st.session_state["last_selected_domain"] in existing_domains:
        last_selected_index = existing_domains.index(
            st.session_state["last_selected_domain"]
        )

    return last_selected_index


def select_domain(existing_domains, last_selected_index):
    with st.sidebar:
        selected_domain = st.selectbox(
            "Select Domain",
            existing_domains,
            index=last_selected_index,
            key="select_domain",
        )

    return selected_domain


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
            st.session_state["last_selected_domain"] = None
            st.session_state["select_all"] = False
        except Exception as e:
            st.session_state["message"] = str(e)
            st.session_state["message_type"] = "error"
        st.rerun()

    if update_domain_button and selected_domain and new_domain_name:
        message, message_type = update_domain(selected_domain, new_domain_name)
        st.session_state["message"] = message
        st.session_state["message_type"] = message_type
        if message_type == "success":
            st.session_state["last_selected_domain"] = new_domain_name
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
    with st.container(border=True):
        selected_texts = {
            text: st.checkbox(text, key=f"{domain}_{text}")
            for text in source_domain_texts
        }
        return [text for text, selected in selected_texts.items() if selected]


def move_texts(source_domain, target_domain, texts):
    try:
        skipped_texts = reader_repository.move_text(source_domain, target_domain, texts)
        st.session_state["skipped_texts"] = skipped_texts
        st.rerun()
    except Exception as e:
        st.error(f"Failed to move texts: {str(e)}")


def display_domain_texts(domain):
    if domain:
        with st.container(border=True):
            extracted_texts = reader_repository.list_text_names_by_domain(domain)
            for text in extracted_texts:
                st.text(text)


def update_source_domain():
    st.session_state["source_domain"] = st.session_state["source_domain_selection"]


def update_target_domain():
    st.session_state["target_domain"] = st.session_state["target_domain_selection"]


def domain_text_management():

    source_domain_options = reader_repository.list_domains_with_extracted_texts()

    if len(reader_repository.list_domains_without_default()) == 0:
        st.info("You can add domains in the side menu.")
        return

    if len(source_domain_options) == 0:
        st.info("You can 'Extract text' with the option in the side menu.")
        return

    st.title("Move Texts")

    col1, col2 = st.columns(2)
    with col1:
        source_domain_index = (
            0
            if st.session_state["source_domain"] not in source_domain_options
            else source_domain_options.index(st.session_state["source_domain"])
        )
        st.session_state["source_domain"] = source_domain_options[source_domain_index]
        source_domain_selection = st.selectbox(
            "Select source domain",
            source_domain_options,
            key="source_domain_selection",
            index=source_domain_index,
            on_change=update_source_domain,
        )
        source_domain_texts = reader_repository.list_text_names_by_domain(
            source_domain_selection
        )
        if len(source_domain_texts) > 0:
            selected_source_texts = select_domain_texts(
                source_domain_texts, source_domain_selection
            )
        else:
            if len(source_domain_options) > 0:
                st.warning("No texts found")

    target_domain_options = [
        domain for domain in get_existing_domains() if domain != source_domain_selection
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
            f"- {text}" for text in st.session_state["skipped_texts"]
        )
        st.markdown(skipped_list)
        del st.session_state["skipped_texts"]


def main():
    setup_page()
    setup_session_state()
    show_messages()

    domain_creation_form()

    existing_domains = get_existing_domains()
    last_selected_index = get_last_selected_index(existing_domains)
    selected_domain = select_domain(existing_domains, last_selected_index)

    domain_management_form(selected_domain)

    extracted_data(selected_domain)

    domain_text_management()


if __name__ == "__main__":
    main()

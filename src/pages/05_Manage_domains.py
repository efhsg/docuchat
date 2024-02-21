import re
import streamlit as st
from config import Config
from injector import get_reader_repository
from pages.utils.extracted_data import manage_extracted_data

config = Config()
reader_repository = get_reader_repository()


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


def setup_session_state():
    for key in [
        "message",
        "message_type",
        "last_selected_domain",
        "select_all",
        "selected_domain",
    ]:
        if key not in st.session_state:
            st.session_state[key] = None if key != "select_all" else False


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


def get_existing_domains(config, reader_repository):
    existing_domains = [
        config.default_domain_name
    ] + reader_repository.list_domains_without_default()

    return existing_domains


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


def main():
    st.sidebar.title("Manage Domains")
    st.title("Manage Extracted Text")

    setup_session_state()
    show_messages()

    domain_creation_form()

    existing_domains = get_existing_domains(config, reader_repository)
    last_selected_index = get_last_selected_index(existing_domains)
    selected_domain = select_domain(existing_domains, last_selected_index)

    domain_management_form(selected_domain)

    extracted_data(selected_domain)


if __name__ == "__main__":
    main()

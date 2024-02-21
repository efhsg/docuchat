import streamlit as st
from config import Config
from injector import get_reader_repository
from pages.utils.extracted_data import manage_extracted_data

config = Config()
reader_repository = get_reader_repository()

st.sidebar.title("Manage Domains")

if "message" not in st.session_state:
    st.session_state["message"] = None
if "message_type" not in st.session_state:
    st.session_state["message_type"] = None
if "last_selected_domain" not in st.session_state:
    st.session_state["last_selected_domain"] = None
if "select_all" not in st.session_state:
    st.session_state["select_all"] = False
if "selected_domain" not in st.session_state:
    st.session_state["selected_domain"] = None

if st.session_state["message"]:
    if st.session_state["message_type"] == "success":
        st.sidebar.success(st.session_state["message"])
    elif st.session_state["message_type"] == "error":
        st.sidebar.error(st.session_state["message"])
    st.session_state["message"] = None

with st.sidebar:
    with st.form("create_domain_form", clear_on_submit=True):
        new_domain_name = st.text_input("Domain Name", key="create_domain_input")
        create_domain_button = st.form_submit_button("Create Domain")
        if create_domain_button and new_domain_name:
            try:
                reader_repository.create_domain(new_domain_name)
                st.session_state["message"] = (
                    f"Domain '{new_domain_name}' created successfully!"
                )
                st.session_state["message_type"] = "success"
                st.session_state["last_selected_domain"] = new_domain_name
            except Exception as e:
                st.session_state["message"] = str(e)
                st.session_state["message_type"] = "error"
            st.rerun()

existing_domains = [
    config.default_domain_name
] + reader_repository.list_domains_without_default()
last_selected_index = 0
if st.session_state["last_selected_domain"] in existing_domains:
    last_selected_index = existing_domains.index(
        st.session_state["last_selected_domain"]
    )

selected_domain = st.sidebar.selectbox(
    "Select Domain", existing_domains, index=last_selected_index, key="select_domain"
)

if selected_domain != st.session_state["selected_domain"]:
    st.session_state["selected_domain"] = selected_domain
    st.rerun()

with st.sidebar.form("manage_domain_form", clear_on_submit=True):
    new_domain_name = st.text_input(
        "New Domain Name for Update", key="update_domain_input"
    )
    col1, col2 = st.columns(2)
    with col1:
        delete_domain_button = st.form_submit_button("Delete Domain")
    with col2:
        update_domain_button = st.form_submit_button("Update Domain")

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
    try:
        reader_repository.update_domain(selected_domain, new_domain_name)
        st.session_state["message"] = (
            f"Domain '{selected_domain}' updated to '{new_domain_name}' successfully!"
        )
        st.session_state["message_type"] = "success"
        st.session_state["last_selected_domain"] = new_domain_name
    except Exception as e:
        st.session_state["message"] = str(e)
        st.session_state["message_type"] = "error"
    st.rerun()

if selected_domain:
    with st.sidebar:
        manage_extracted_data(
            reader_repository,
            selected_domain,
            uploading=st.session_state.get("uploading", False),
        )

st.title("Manage Extracted Text")

import streamlit as st
from config import Config
from injector import get_reader_repository

reader_repository = get_reader_repository()


def manage_domains():
    st.sidebar.title("Manage Domains")

    # Initialize session state variables for messages
    if "message" not in st.session_state:
        st.session_state["message"] = None
    if "message_type" not in st.session_state:
        st.session_state["message_type"] = None

    # Display message if exists
    if st.session_state["message"]:
        if st.session_state["message_type"] == "success":
            st.sidebar.success(st.session_state["message"])
        elif st.session_state["message_type"] == "error":
            st.sidebar.error(st.session_state["message"])
        # Clear the message after displaying it
        st.session_state["message"] = None

    with st.sidebar:
        with st.form("create_domain_form"):
            new_domain_name = st.text_input("Domain Name", key="create_domain_input")
            create_domain_button = st.form_submit_button("Create Domain")
            if create_domain_button and new_domain_name:
                try:
                    reader_repository.create_domain(new_domain_name)
                    st.session_state["message"] = (
                        f"Domain '{new_domain_name}' created successfully!"
                    )
                    st.session_state["message_type"] = "success"
                except Exception as e:
                    st.session_state["message"] = f"Failed to create domain. Error: {e}"
                    st.session_state["message_type"] = "error"
                st.rerun()

    existing_domains = [domain[0] for domain in reader_repository.list_domains()]

    with st.sidebar.form("manage_domain_form"):
        domain_name_to_delete_or_update = st.selectbox(
            "Select Domain to Delete or Update",
            existing_domains,
            index=0,
            key="select_domain",
        )
        new_domain_name = st.text_input(
            "New Domain Name for Update", key="update_domain_input"
        )
        col1, col2 = st.columns(2)
        with col1:
            delete_domain_button = st.form_submit_button("Delete Domain")
        with col2:
            update_domain_button = st.form_submit_button("Update Domain")

        if delete_domain_button and domain_name_to_delete_or_update:
            try:
                reader_repository.delete_domain(domain_name_to_delete_or_update)
                st.session_state["message"] = (
                    f"Domain '{domain_name_to_delete_or_update}' deleted successfully!"
                )
                st.session_state["message_type"] = "success"
            except Exception as e:
                st.session_state["message"] = f"Failed to delete domain. Error: {e}"
                st.session_state["message_type"] = "error"
            st.rerun()

        if update_domain_button and domain_name_to_delete_or_update and new_domain_name:
            try:
                reader_repository.update_domain(
                    domain_name_to_delete_or_update, new_domain_name
                )
                st.session_state["message"] = (
                    f"Domain '{domain_name_to_delete_or_update}' updated to '{new_domain_name}' successfully!"
                )
                st.session_state["message_type"] = "success"
            except Exception as e:
                st.session_state["message"] = f"Failed to update domain. Error: {e}"
                st.session_state["message_type"] = "error"
            st.rerun()

    st.title("Manage Extracted Text")


if __name__ == "__main__":
    manage_domains()

import streamlit as st
from config import Config
from injector import get_reader_repository

reader_repository = get_reader_repository()


def manage_domains():
    with st.container():
        st.title("Manage Domains")

        # Domain creation
        with st.form("create_domain"):
            new_domain_name = st.text_input("Domain Name")
            create_domain_button = st.form_submit_button("Create Domain")
            if create_domain_button and new_domain_name:
                try:
                    reader_repository.create_domain(new_domain_name)
                    st.success(f"Domain '{new_domain_name}' created successfully!")
                except Exception as e:
                    st.error(f"Failed to create domain. Error: {e}")

        # Domain listing
        st.write("### Existing Domains")
        domains = reader_repository.list_domains()
        if not domains:
            st.write("No domains found.")
        else:
            for domain in domains:
                st.write(domain[0])

        # Domain deletion and update
        with st.form("manage_domain"):
            existing_domains = [
                domain[0] for domain in reader_repository.list_domains()
            ]
            domain_name_to_delete_or_update = st.selectbox(
                "Select Domain to Delete or Update", existing_domains, index=0
            )
            new_domain_name = st.text_input("New Domain Name for Update")
            delete_domain_button = st.form_submit_button("Delete Domain")
            update_domain_button = st.form_submit_button("Update Domain")

            if delete_domain_button and domain_name_to_delete_or_update:
                try:
                    reader_repository.delete_domain(domain_name_to_delete_or_update)
                    st.success(
                        f"Domain '{domain_name_to_delete_or_update}' deleted successfully!"
                    )
                except Exception as e:
                    st.error(f"Failed to delete domain. Error: {e}")

            if (
                update_domain_button
                and domain_name_to_delete_or_update
                and new_domain_name
            ):
                try:
                    reader_repository.update_domain(
                        domain_name_to_delete_or_update, new_domain_name
                    )
                    st.success(
                        f"Domain '{domain_name_to_delete_or_update}' updated to '{new_domain_name}' successfully!"
                    )
                except Exception as e:
                    st.error(f"Failed to update domain. Error: {e}")


if __name__ == "__main__":
    manage_domains()

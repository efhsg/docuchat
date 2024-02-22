import streamlit as st

from components.reader.interfaces.reader_repository import ReaderRepository


def manage_extracted_data(
    reader_repository: ReaderRepository, selected_domain: str, uploading: bool
) -> None:
    st.title(f"Texts in {selected_domain}")

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
                    disabled=uploading,
                )
                for file in files
            }
            delete = st.form_submit_button("Delete", disabled=uploading)
            if delete:
                texts_to_delete = [
                    file_name
                    for file_name, is_checked in file_dict.items()
                    if is_checked
                ]
                if texts_to_delete:
                    reader_repository.delete_texts(texts_to_delete, selected_domain)
                    for text in texts_to_delete:
                        if text in st.session_state:
                            del st.session_state[text]
                    st.experimental_rerun()

        st.checkbox(
            "Select all texts",
            key="select_all_toggle",
            on_change=lambda: st.session_state.update(
                select_all=not st.session_state["select_all"]
            ),
            value=st.session_state["select_all"],
            disabled=uploading,
        )

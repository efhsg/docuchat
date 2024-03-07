import streamlit as st
from components.database.models import ExtractedText
from injector import get_logger
from components.reader.interfaces.reader_repository import ReaderRepository
import pages.utils.utils as utils

logger = get_logger()


def manage_extracted_text(
    reader_repository: ReaderRepository, selected_domain: str, uploading: bool
) -> None:
    st.title(f"Texts in {selected_domain}")

    extracted_texts = reader_repository.list_texts_by_domain(selected_domain)

    if not extracted_texts:
        st.write("No files found")
    else:
        with st.form("manage_files", clear_on_submit=True):
            extracted_dict = {
                extracted_text: st.checkbox(
                    label=utils.extracted_text_to_label(extracted_text),
                    value=st.session_state["select_all_texts"],
                    key=f"{extracted_text.name}.{extracted_text.type}",
                    disabled=uploading,
                )
                for extracted_text in extracted_texts
            }
            delete = st.form_submit_button("Delete", disabled=uploading)
            if delete:
                texts_to_delete = [
                    (extracted_text.name, extracted_text.type)
                    for extracted_text, is_checked in extracted_dict.items()
                    if is_checked
                ]

                if texts_to_delete:
                    reader_repository.delete_texts(selected_domain, texts_to_delete)
                    st.session_state["select_all_texts"] = False
                    for text in texts_to_delete:
                        if text in st.session_state:
                            del st.session_state[text]
                st.rerun()

        st.checkbox(
            "Select all texts",
            key="select_all_texts_toggle",
            on_change=lambda: st.session_state.update(
                select_all_texts=not st.session_state["select_all_texts"]
            ),
            value=st.session_state["select_all_texts"],
            disabled=uploading,
        )

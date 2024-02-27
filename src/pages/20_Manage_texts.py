import base64
from typing import List
import streamlit as st
from components.database.models import ExtractedText
from injector import get_config, get_logger, get_reader_repository, get_compressor
from pages.utils.utils import get_index, set_default_state
from pages.utils.utils import (
    setup_page,
    select_domain,
    extracted_text_to_label,
)

config = get_config()
reader_repository = get_reader_repository()
logger = get_logger()
compressor = get_compressor()


def main():
    setup_page()
    setup_session_state()
    manage_texts(select_domain(reader_repository.list_domains_with_extracted_texts()))


def setup_session_state() -> None:
    default_session_states = [
        ("context_domain", None),
        ("context_text", None),
        ("show_text", False),
        ("edit_text", False),
    ]

    for state_name, default_value in default_session_states:
        set_default_state(state_name, default_value)


def manage_texts(selected_domain):
    st.title(f"Texts in {selected_domain}")

    selected_text = select_text(reader_repository.list_texts_by_domain(selected_domain))

    if selected_text:
        handle_text_rename(selected_domain, selected_text)

        col1, col2, col3, col4 = st.columns([1, 1, 6, 1])

        with col1:
            if st.button("Show"):
                st.session_state["show_text"] = not st.session_state.get(
                    "show_text", False
                )
                st.session_state["edit_text"] = False

        with col2:
            if st.button("Edit"):
                st.session_state["edit_text"] = not st.session_state.get(
                    "edit_text", False
                )
                st.session_state["show_text"] = False

        with col3:
            text_content = compressor.decompress(selected_text.text)
            if text_content:
                filename = f"{selected_text.name}.txt"  # Filename using the text's name
                st.download_button(
                    label="Download",
                    data=text_content,
                    file_name=filename,
                    mime="text/plain",
                )

        with col4:
            if st.button("🗑️ Delete"):
                reader_repository.delete_texts(
                    selected_domain, [(selected_text.name, selected_text.type)]
                )
                st.rerun()

        if st.session_state.get("show_text"):
            handle_text_content(selected_domain, selected_text, edit_mode=False)

        if st.session_state.get("edit_text"):
            handle_text_content(selected_domain, selected_text, edit_mode=True)


def select_domain(domain_options):
    return st.sidebar.selectbox(
        label="Select Domain",
        options=domain_options,
        key="selected_domain",
        index=get_index(domain_options, "context_domain"),
        on_change=lambda: st.session_state.update(
            context_domain=st.session_state["selected_domain"], select_all_texts=False
        ),
    )


def select_text(text_options: List[ExtractedText]) -> ExtractedText:
    options_dict = {f"{extracted_text_to_label(text)}": text for text in text_options}

    selected_label = st.selectbox(
        label="Select a text",
        options=list(options_dict.keys()),
        key="selected_text",
        index=get_index(list(options_dict.keys()), "context_text"),
        on_change=lambda: st.session_state.update(
            context_text=st.session_state["selected_text"]
        ),
    )

    for text in text_options:
        if extracted_text_to_label(text) == selected_label:
            return text

    raise ValueError("Selected text not found.")


def handle_text_rename(selected_domain: str, selected_text: ExtractedText):

    with st.form("Rename_text", clear_on_submit=False):
        new_name = st.text_input("Rename text", value=selected_text.name)
        st.write(f"Original name: {selected_text.original_name}")
        save_text_name = st.form_submit_button(label="Save")

    if save_text_name:
        success = reader_repository.update_text_name(
            domain_name=selected_domain,
            old_name=selected_text.name,
            new_name=new_name,
            text_type=selected_text.type,
        )

        if success:
            selected_text.name = new_name
            st.session_state.update(context_text=extracted_text_to_label(selected_text))
            st.experimental_rerun()


def handle_text_content(selected_domain, selected_text: ExtractedText, edit_mode):
    try:
        text_content = compressor.decompress(selected_text.text)
        if text_content is not None:
            if edit_mode:
                edited_text = st.text_area(
                    "Edit content", value=text_content, height=400
                )
                if st.button("Save changes"):
                    reader_repository.save_text(
                        selected_domain,
                        selected_text.name,
                        selected_text.type,
                        selected_text.original_name,
                        edited_text,
                    )
                    st.session_state["edit_text"] = False
                    st.session_state["show_text"] = True
                    st.rerun()
            else:
                st.text_area("content", value=text_content, height=400, disabled=True)
        else:
            st.error("Text content not found.")
    except Exception as e:
        logger.error(
            f"An error occurred while displaying or editing the text content: {e}"
        )
        st.error(f"An error occurred while displaying or editing the text content: {e}")


if __name__ == "__main__":
    main()

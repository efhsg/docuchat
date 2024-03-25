import streamlit as st
from components.database.models import ExtractedText
from injector import get_config, get_logger, get_reader_repository, get_compressor
from pages.utils.utils import (
    get_index,
    select_texts,
    set_default_state,
    setup_session_state_vars,
    show_messages,
)
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


def manage_texts(selected_domain):

    if selected_domain is None:
        st.info("First extract texts")
        return

    st.title(f"Texts in {selected_domain}")

    selected_text = select_texts(
        reader_repository.list_texts_by_domain(selected_domain)
    )

    show_messages()

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
    handle_add_text(selected_domain)


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


def handle_text_rename(selected_domain: str, selected_text: ExtractedText):

    with st.form("Rename_text", clear_on_submit=False):
        new_name = st.text_input("Rename text", value=selected_text.name)
        st.write(f"Original name: {(selected_text.original_name)}")
        save_text_name = st.form_submit_button(label="Save")

    if save_text_name:
        try:
            reader_repository.update_text_name(
                domain_name=selected_domain,
                old_name=selected_text.name,
                new_name=new_name,
                text_type=selected_text.type,
            )
            st.session_state["message"] = (
                f"Text name '{selected_text.name}' updated to '{new_name}' successfully!",
                "success",
            )
            selected_text.name = new_name
            st.session_state.update(context_text=extracted_text_to_label(selected_text))
        except Exception as e:
            st.session_state["message"] = (str(e), "error")
        st.rerun()


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


def handle_add_text(selected_domain):
    with st.container(border=True):
        if st.button("Add new text"):
            st.session_state["add_new_text"] = not st.session_state["add_new_text"]

        if st.session_state.get("add_new_text"):
            with st.form("add_text_form", clear_on_submit=True):
                title = st.text_input("Title")
                new_text = st.text_area("Paste your text here", height=200)
                submit_button = st.form_submit_button(label="Save")

            if submit_button:
                try:
                    if not title or not new_text:
                        raise ValueError(
                            "Please provide a title and fill in the text area before saving."
                        )
                    reader_repository.save_text(
                        domain_name=selected_domain,
                        text_name=title,
                        text=new_text,
                        text_type="freeform",
                        original_name=title,
                    )
                    st.success(f"Text '{title}' added successfully!")
                    st.session_state["message"] = (
                        f"Text '{title}' added successfully!",
                        "success",
                    )
                    st.session_state["add_new_text"] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add text '{title}': {str(e)}")
                    st.session_state["message"] = (
                        f"Failed to add text '{title}': {str(e)}",
                        "error",
                    )


def setup_session_state():
    setup_session_state_vars(
        [
            ("message", (None, None)),
            ("context_domain", None),
            ("context_text", None),
            ("show_text", False),
            ("edit_text", False),
            ("add_new_text", False),
        ]
    )


if __name__ == "__main__":
    main()

import streamlit as st
from injector import get_config, get_logger, get_reader_repository
from pages.utils.utils import get_index, set_default_state
from pages.utils.utils import setup_page

config = get_config()
reader_repository = get_reader_repository()
logger = get_logger()


def setup_session_state() -> None:
    set_default_state("context_domain", None)
    set_default_state("context_text", None)
    set_default_state("show_text", False)
    set_default_state("edit_text", False)


def select_domain():
    domain_options = reader_repository.list_domains_with_extracted_texts()
    return st.sidebar.selectbox(
        label="Select Domain",
        options=domain_options,
        key="selected_domain",
        index=get_index(domain_options, "context_domain"),
        on_change=lambda: st.session_state.update(
            context_domain=st.session_state["selected_domain"]
        ),
    )


def manage_texts(selected_domain):
    st.title(selected_domain)
    selected_text = select_text(
        reader_repository.list_text_names_by_domain(selected_domain)
    )
    if selected_text:
        handle_text_renaming(selected_domain, selected_text)

        col1, col2 = st.columns([1, 5])

        with col1:
            if st.button("Show text"):
                st.session_state["show_text"] = not st.session_state["show_text"]
                st.session_state["edit_text"] = False

        with col2:
            if st.button("Edit text"):
                st.session_state["edit_text"] = not st.session_state["edit_text"]
                st.session_state["show_text"] = False

        if st.session_state.get("show_text"):
            handle_text_content(selected_domain, selected_text, edit_mode=False)

        if st.session_state.get("edit_text"):
            handle_text_content(selected_domain, selected_text, edit_mode=True)


def select_text(text_options):
    selected_text = st.selectbox(
        label="Select a text",
        options=text_options,
        key="selected_text",
        index=get_index(text_options, "context_text"),
        on_change=lambda: st.session_state.update(
            context_text=st.session_state["selected_text"]
        ),
    )

    return selected_text


def handle_text_renaming(selected_domain, selected_text):
    with st.form("Rename_text", clear_on_submit=False):
        new_name = st.text_input("Rename text", value=selected_text)
        save_text_name = st.form_submit_button(
            label="Save",
        )

    if save_text_name:
        if reader_repository.update_text_name(selected_text, new_name, selected_domain):
            st.session_state.update(context_text=new_name)
            st.rerun()


def handle_text_content(selected_domain, selected_text, edit_mode):
    try:
        text_content = reader_repository.get_text_by_name(
            selected_text, selected_domain
        )
        if text_content is not None:
            if edit_mode:
                edited_text = st.text_area(
                    "Edit content", value=text_content, height=400
                )
                if st.button("Save changes"):
                    reader_repository.save_text(
                        edited_text, selected_text, selected_domain
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


def main():
    setup_page()
    setup_session_state()
    manage_texts(select_domain())


if __name__ == "__main__":
    main()

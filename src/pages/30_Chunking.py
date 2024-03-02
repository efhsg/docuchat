from datetime import datetime
import streamlit as st
from components.chunker.interfaces.chunker import Chunker
from components.chunker.interfaces.chunker_repository import ChunkerRepository
from components.reader.interfaces.reader_repository import ReaderRepository
from components.reader.interfaces.text_compressor import TextCompressor
from logging import Logger
from injector import (
    get_chunker_config,
    get_chunker_repository,
    get_config,
    get_logger,
    get_reader_repository,
    get_compressor,
)
from pages.utils.streamlit_form import StreamlitForm
from pages.utils.utils import (
    get_index,
    select_text,
    set_default_state,
    select_domain,
    setup_page,
)

config = get_config()
chunker_config = get_chunker_config()
logger: Logger = get_logger()
compressor: TextCompressor = get_compressor()
reader_repository: ReaderRepository = get_reader_repository()
chunker_repository: ChunkerRepository = get_chunker_repository()


def main():
    setup_page()
    setup_session_state()
    selected_domain = select_domain(
        reader_repository.list_domains_with_extracted_texts()
    )
    st.title(f"{selected_domain}")
    text_options = reader_repository.list_texts_by_domain(selected_domain)
    if not text_options:
        return ()

    selected_text = select_text(text_options)
    create_chunk_processes(selected_text)
    manage_chunk_processes(selected_text)


def setup_session_state():
    default_session_states = [
        ("message", (None, None)),
        ("context_domain", None),
        ("context_text", None),
        ("context_chunk_method", None),
        ("context_chunk_size", 1000),
        ("context_chunk_overlap", 100),
    ]
    for state_name, default_value in default_session_states:
        set_default_state(state_name, default_value)


def create_chunk_processes(selected_text):
    if selected_text is None:
        st.info("Please select a text.")
        return

    chunker_options = chunker_config.chunker_options
    method = select_method(list(chunker_options.keys()))

    chunker_details = chunker_options[method]
    chunker_class: Chunker = chunker_details["class"]

    form_config = {
        "params": chunker_details["params"],
        "validations": chunker_details.get("validations", []),
        "constants": chunker_details["constants"],
    }
    form = StreamlitForm(form_config)
    submitted, updated_form_values = form.generate_form(
        init_form_values(chunker_details["params"].items()),
        "chunk_process",
        "Start chunking",
    )
    if submitted:
        if form.validate_form_values(updated_form_values):
            try:
                save_form_values_to_context(updated_form_values)
                process_text_to_chunks(
                    selected_text, method, chunker_class, updated_form_values
                )
            except Exception as e:
                st.error(f"Failed to validate or process chunks: {e}")


def init_form_values(fields):
    return {
        param: st.session_state.get(f"context_{param}", details["default"])
        for param, details in fields
    }


def save_form_values_to_context(values):
    for value in values:
        st.session_state[f"context_{value}"] = values[value]


def process_text_to_chunks(selected_text, method, chunker_class, values):
    try:
        with st.spinner("Chunking..."):
            chunker_instance = chunker_class(**values)

            values["name"] = generate_default_name()
            chunk_process_id = chunker_repository.create_chunk_process(
                extracted_text_id=selected_text.id,
                method=method,
                parameters=values,
            )

            text_content = compressor.decompress(selected_text.text)
            chunks = chunker_instance.chunk(text_content)

            chunk_data_for_db = [(index, chunk) for index, chunk in enumerate(chunks)]
            chunker_repository.save_chunks(chunk_process_id, chunk_data_for_db)
            st.rerun()
    except Exception as e:
        st.error(f"Failed to create chunk process or save chunks: {e}")


def select_method(method_options):
    method = st.selectbox(
        label="Select chunking method",
        options=method_options,
        key="chunk_method",
        index=get_index(method_options, "context_chunk_method"),
        on_change=lambda: st.session_state.update(
            context_chunk_method=st.session_state["chunk_method"]
        ),
    )

    return method


def generate_default_name() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def manage_chunk_processes(selected_text):
    if selected_text is None:
        return

    chunk_sessions = chunker_repository.list_chunk_processes_by_text(selected_text.id)
    if not chunk_sessions:
        st.write("No chunk sessions found for this text.")
        return

    for session in chunk_sessions:
        with st.container(border=True):
            col1, col2, col3 = st.columns([8, 1, 1])
            with col1:
                show_process_header(session)
            with col2:
                st.button(
                    label="Rename",
                    key=f"rename_{session.id}",
                    on_click=lambda session_id=session.id: st.session_state.update(
                        {f"renaming_{session_id}": True}
                    ),
                )
            with col3:
                delete_button = st.button(label="🗑️ Delete", key=f"delete_{session.id}")

            if delete_button:
                delete_process(session)
            if st.session_state.get(f"renaming_{session.id}", False):
                rename_session(session)

            show_chunks(session)


def rename_session(session):
    new_name = st.text_input(
        "New name:",
        key=f"new_name_{session.id}",
        value=session.parameters["name"],
    )
    col1, col2 = st.columns([1, 9])
    with col1:
        if st.button("Save", key=f"save_{session.id}"):
            try:
                session.parameters["name"] = new_name
                chunker_repository.update_chunk_process(session)
                st.session_state[f"renaming_{session.id}"] = False
                st.rerun()
            except Exception as e:
                st.error(f"Failed to rename chunk process: {e}")
    with col2:
        if st.button("Cancel", key=f"cancel_{session.id}"):
            st.session_state[f"renaming_{session.id}"] = False
            st.rerun()


def delete_process(session):
    try:
        chunker_repository.delete_chunks_by_process(session.id)
        chunker_repository.delete_chunk_process(session.id)
        st.rerun()
    except Exception as e:
        st.error(f"Failed to create chunk process or save chunks: {e}")


def show_process_header(session):
    method_display = f"{session.method} ({session.parameters['name']})"
    chunker_options = chunker_config.chunker_options[session.method]
    params_order = chunker_options.get("order", [])
    params_display = ", ".join(
        [
            f"{key}: {session.parameters[key]}"
            for key in params_order
            if key in session.parameters
        ]
    )
    st.markdown(f"**{method_display}**, {params_display}")


def show_chunks(session):
    with st.expander(f"Chunks:"):
        chunks = chunker_repository.list_chunks_by_process(session.id)
        if chunks:
            page_number = st.session_state.get(f"page_{session.id}", 0)
            page_size = 5
            total_pages = (len(chunks) - 1) // page_size + 1
            start_index = page_number * page_size
            end_index = start_index + page_size
            displayed_chunks = chunks[start_index:end_index]

            chunks_page_nav(session, page_number, total_pages, "top")
            for chunk in displayed_chunks:
                with st.container(border=True):
                    text_content = compressor.decompress(chunk.chunk)
                    st.text_area(
                        label=f"Chunk: {chunk.index + 1}",
                        value=text_content,
                        key=f"chunk_{session.id}_{chunk.index}",
                        height=200,
                        disabled=True,
                    )
            chunks_page_nav(session, page_number, total_pages, "bottom")

        else:
            st.write("No chunks found for this session.")


def chunks_page_nav(session, page_number, total_pages, position):
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        prev_button = st.button(
            "Previous", key=f"prev_{session.id}_{position}", disabled=page_number <= 0
        )
        if prev_button:
            st.session_state[f"page_{session.id}"] = page_number - 1
            st.rerun()
    with col2:
        next_button = st.button(
            "&nbsp;&nbsp;&nbsp;&nbsp;Next&nbsp;&nbsp;&nbsp;&nbsp;",
            key=f"next_{session.id}_{position}",
            disabled=(page_number + 1 >= total_pages),
        )
        if next_button:
            st.session_state[f"page_{session.id}"] = page_number + 1
            st.rerun()
    with col3:
        page_select = st.selectbox(
            label="Select page",
            options=range(1, total_pages + 1),
            index=page_number,
            key=f"select_{session.id}_{position}",
        )
        if page_select != page_number + 1:
            st.session_state[f"page_{session.id}"] = page_select - 1
            st.rerun()


if __name__ == "__main__":
    main()

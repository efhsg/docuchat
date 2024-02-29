from typing import Type
import streamlit as st
from components.chunker.chunker_config import ChunkerConfig
from components.chunker.interfaces.chunker import Chunker
from injector import (
    get_chunker_repository,
    get_config,
    get_logger,
    get_reader_repository,
    get_compressor,
)
from pages.utils.utils import (
    get_index,
    select_text,
    set_default_state,
    select_domain,
    setup_page,
)

config = get_config()
logger = get_logger()
compressor = get_compressor()
reader_repository = get_reader_repository()
chunker_repository = get_chunker_repository()
chunker_config = ChunkerConfig()


def main():
    setup_page()
    setup_session_state()
    selected_domain = select_domain(
        reader_repository.list_domains_with_extracted_texts()
    )
    st.title(f"Chunking text in {selected_domain}")
    selected_text = select_text(reader_repository.list_texts_by_domain(selected_domain))
    manage_chunks(selected_text)
    manage_chunks_sessions(selected_text)


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


def manage_chunks(selected_text):
    if selected_text is None:
        st.info("Please select a text.")
        return

    chunker_options = chunker_config.chunker_options
    method = st.selectbox(
        label="Select chunking method",
        options=list(chunker_options.keys()),
        key="selected_chunk_method",
        index=get_index(list(chunker_options.keys()), "context_chunk_method"),
        on_change=lambda: st.session_state.update(
            context_chunk_method=st.session_state["selected_chunk_method"]
        ),
    )
    chunker_details = chunker_options[method]
    chunker_class: Type[Chunker] = chunker_details["class"]

    with st.form(key="chunk_process_form"):
        params = {}
        for param, details in chunker_details["params"].items():
            if details["type"] == "number":
                params[param] = st.number_input(
                    label=details["label"],
                    min_value=details.get("min_value", 0),
                    value=st.session_state.get(f"context_{param}", details["default"]),
                )
            elif details["type"] == "select":
                params[param] = st.selectbox(
                    label=details["label"],
                    options=details["options"],
                    index=details["options"].index(
                        st.session_state.get(f"context_{param}", details["default"])
                    ),
                )
            elif details["type"] == "checkbox":
                params[param] = st.checkbox(
                    label=details["label"],
                    value=st.session_state.get(f"context_{param}", details["default"]),
                )
        submit_button = st.form_submit_button(label="Chunk")

    if submit_button:
        for param in chunker_class.get_init_params():
            st.session_state[f"context_{param}"] = params[f"{param}"]
        with st.spinner("Chunking..."):
            try:
                chunk_process_id = chunker_repository.create_chunk_process(
                    extracted_text_id=selected_text.id,
                    method=method,
                    parameters=params,
                )

                chunker_instance = chunker_class(**params)

                text_content = compressor.decompress(selected_text.text)
                chunks = chunker_instance.chunk(text_content)

                chunk_data_for_db = [
                    (index, chunk) for index, chunk in enumerate(chunks)
                ]

                chunker_repository.save_chunks(chunk_process_id, chunk_data_for_db)

                st.rerun()
            except Exception as e:
                st.error(f"Failed to create chunk process or save chunks: {e}")


def manage_chunks_sessions(selected_text):
    if selected_text is None:
        return

    chunk_sessions = chunker_repository.list_chunk_processes_by_text(selected_text.id)
    if not chunk_sessions:
        st.write("No chunk sessions found for this text.")
        return

    for session in chunk_sessions:
        with st.container(border=True):
            col1, col2 = st.columns([10, 1])
            with col1:
                st.write(f"{session.method}, {session.parameters}")
            with col2:
                delete_button = st.button(label="🗑️ Delete", key=f"delete_{session.id}")

            if delete_button:
                chunker_repository.delete_chunks_by_process(session.id)
                chunker_repository.delete_chunk_process(session.id)
                st.experimental_rerun()

            with st.expander(f"Chunks:"):
                chunks = chunker_repository.list_chunks_by_process(session.id)
                if chunks:
                    page_number = st.session_state.get(f"page_{session.id}", 0)
                    page_size = 5
                    total_pages = (len(chunks) - 1) // page_size + 1
                    start_index = page_number * page_size
                    end_index = start_index + page_size
                    displayed_chunks = chunks[start_index:end_index]

                    chunks_page_nav(
                        session, chunks, page_number, end_index, total_pages, "top"
                    )
                    for chunk in displayed_chunks:
                        st.write(f"{chunk.index + 1}")
                        with st.container(border=True):
                            st.text(compressor.decompress(chunk.chunk))
                    chunks_page_nav(
                        session, chunks, page_number, end_index, total_pages, "bottom"
                    )

                else:
                    st.write("No chunks found for this session.")


def chunks_page_nav(session, chunks, page_number, end_index, total_pages, position):
    col1, col2, col3 = st.columns([1, 9, 1])
    with col1:
        prev_button = st.button(
            "Previous", key=f"prev_{session.id}_{position}", disabled=page_number == 0
        )
        if prev_button:
            st.session_state[f"page_{session.id}"] = page_number - 1
            st.rerun()
    with col2:
        next_button = st.button(
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Next&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;",
            key=f"next_{session.id}_{position}",
            disabled=(page_number + 1 == total_pages),
        )
        if next_button:
            st.session_state[f"page_{session.id}"] = page_number + 1
            st.rerun()
    with col3:
        st.write(f"Page {page_number + 1} of {total_pages}")


if __name__ == "__main__":
    main()

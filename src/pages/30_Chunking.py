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
    chunker_class: Type[Chunker] = chunker_options[method]

    with st.form(key="chunk_process_form"):
        params = {}
        for param in chunker_class.get_init_params():
            if param == "chunk_size":
                params["chunk_size"] = st.number_input(
                    "Chunk size",
                    min_value=1,
                    value=st.session_state["context_chunk_size"],
                )
            elif param == "overlap":
                params["overlap"] = st.number_input(
                    label="Overlap size",
                    min_value=0,
                    value=st.session_state["context_chunk_overlap"],
                )
        submit_button = st.form_submit_button(label="Chunk")

    if submit_button:
        for param in chunker_class.get_init_params():
            if param == "chunk_size":
                st.session_state["context_chunk_size"] = params["chunk_size"]
            elif param == "overlap":
                st.session_state["context_chunk_overlap"] = params["overlap"]
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

                st.success("Chunk process created and chunks saved successfully.")
            except Exception as e:
                st.error(f"Failed to create chunk process or save chunks: {e}")


if __name__ == "__main__":
    main()

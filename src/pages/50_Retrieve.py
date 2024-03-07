import pickle
import streamlit as st
from components.embedder.interfaces.embedder import Embedder
from components.embedder.interfaces.embedder_factory import EmbedderFactory
from components.retriever.interfaces.retriever import Retriever
from components.retriever.interfaces.retriever_factory import RetrieverFactory
from components.reader.interfaces.text_compressor import TextCompressor
from logging import Logger
from components.retriever.interfaces.retriever_repository import RetrieverRepository
from injector import (
    get_config,
    get_embedder_config,
    get_embedder_factory,
    get_logger,
    get_compressor,
    get_retriever_config,
    get_retriever_factory,
    get_retriever_repository,
)
from pages.utils.streamlit_form import StreamlitForm
from pages.utils.utils import (
    extracted_text_to_label,
    init_form_values,
    save_form_values_to_context,
    select_domain_instance,
    set_default_state,
    setup_page,
)

config = get_config()
logger: Logger = get_logger()
retriever_factory: RetrieverFactory = get_retriever_factory()
retriever_repository: RetrieverRepository = get_retriever_repository()
retriever_config = get_retriever_config()
embedder_config = get_embedder_config()
embedder_factory: EmbedderFactory = get_embedder_factory()
compressor: TextCompressor = get_compressor()


def main():
    setup_page()
    setup_session_state()

    selected_domain = select_domain_instance(
        retriever_repository.list_domains_with_embeddings()
    )

    if selected_domain is None:
        st.info("First embed some texts")
        return

    st.title(f"{selected_domain.name}")

    if st.session_state.get("context_embedder", None):
        embedder: Embedder = st.session_state.get("context_embedder")
        display_embedder(embedder)
        if st.session_state.get("context_retriever", None):
            retriever: Retriever = st.session_state.get("context_retriever")
            display_retriever(retriever)
            query(selected_domain.id, embedder, retriever)
        else:
            select_retriever()
    else:
        select_embedder()


def select_embedder():
    embedder_options = embedder_config.embedder_options
    method = st.selectbox("Select an embedder method:", list(embedder_options.keys()))
    embedder_details = embedder_options[method]
    form_config = {
        "fields": embedder_details["fields"],
        "validations": embedder_details.get("validations", []),
        "constants": embedder_details.get("constants", {}),
    }
    form = StreamlitForm(form_config)
    updated_form_values = form.generate_form(
        init_form_values(embedder_details["fields"].items()),
        "embed_process",
        "Configure Embedder",
    )
    with st.spinner("Getting embedder"):
        if updated_form_values:
            embedder: Embedder = embedder_factory.create_embedder(
                method, **updated_form_values
            )
            save_form_values_to_context(updated_form_values)
            st.session_state["context_embedder"] = embedder
            st.rerun()


def display_embedder(embedder):
    with st.container(border=True):
        config = embedder.get_configuration()
        method_display = f"{config['method']}"
        params = config.get("params", {})
        fields_display = ", ".join([f"{key}: {value}" for key, value in params.items()])
        st.markdown(f"**{method_display}**, {fields_display}")
        if st.button("Change embedder"):
            st.session_state["context_embedder"] = None
            st.rerun()


def select_retriever():
    retriever_options = retriever_config.retriever_options
    method = st.selectbox("Select a retriever method:", list(retriever_options.keys()))
    retriever_details = retriever_options[method]

    form_config = {
        "fields": retriever_details.get("fields", {}),
        "validations": retriever_details.get("validations", []),
        "constants": retriever_details.get("constants", {}),
    }

    form = StreamlitForm(form_config)
    updated_form_values = form.generate_form(
        init_form_values(retriever_details["fields"].items()),
        "retriever_process",
        "Configure Retriever",
    )
    if updated_form_values:
        retriever = retriever_factory.create_retriever(method, **updated_form_values)
        st.session_state["context_retriever"] = retriever
        st.rerun()


def display_retriever(retriever):
    with st.container(border=True):
        config = retriever.get_configuration()
        method_display = f"{config['method']}"
        params = config.get("params", {})
        fields_display = ", ".join([f"{key}: {value}" for key, value in params.items()])
        st.markdown(f"**{method_display}**, {fields_display}")
        if st.button("Change retriever"):
            st.session_state["context_retriever"] = None
            st.rerun()


def query(domain_id: int, embedder, retriever):
    query_text = st.text_input("Enter your query:")
    if query_text:
        try:
            serialized_query_vector = convert_query_to_vector(query_text, embedder)[0][
                1
            ]
            query_vector = pickle.loads(serialized_query_vector)
            embeddings = retriever.retrieve(
                domain_id=domain_id, query_vector=query_vector
            )
            display_embeddings(embeddings)
        except RuntimeError as e:
            st.error(f"Error retrieving embeddings: {e}")


def convert_query_to_vector(query: str, embedder: Embedder) -> list:
    return embedder.embed([(0, query)])


def display_embeddings(embeddings: list):
    if embeddings:
        for embedding_id, score in embeddings:
            with st.container(border=True):
                chunk_with_filename = (
                    retriever_repository.get_chunk_by_embedding_id_with_filename(
                        embedding_id
                    )
                )
                if chunk_with_filename:
                    chunk, text_file_name = chunk_with_filename
                    text_content = compressor.decompress(chunk.chunk)
                    chunk_size = len(text_content)
                    st.write(
                        f"Score: {score:.4f}, {extracted_text_to_label(text_file_name)}"
                    )
                    st.text_area(
                        label=f"Chunk: {chunk.index + 1} (Size: {chunk_size} characters)",
                        value=text_content,
                        key=f"chunk_{chunk.id}_{chunk.index}",
                        height=200,
                        disabled=True,
                    )
                else:
                    st.write(
                        f"Embedding ID: {embedding_id}, Score: {score}, but chunk not found."
                    )
    else:
        st.info("No relevant embeddings found for your query.")


def setup_session_state():
    default_session_states = [
        ("context_domain", None),
        ("context_embedder", None),
        ("context_retriever", None),
    ]
    for state_name, default_value in default_session_states:
        set_default_state(state_name, default_value)


def list_domain_names_with_embeddings():
    domain_options = [
        (domain.name) for domain in retriever_repository.list_domains_with_embeddings()
    ]
    return domain_options


if __name__ == "__main__":
    main()

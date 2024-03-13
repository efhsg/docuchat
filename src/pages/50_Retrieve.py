import pickle
import streamlit as st
from components.embedder.interfaces.embedder import Embedder
from components.embedder.interfaces.embedder_factory import EmbedderFactory
from components.embedder.interfaces.embedder_repository import EmbedderRepository
from components.retriever.interfaces.retriever import Retriever
from components.retriever.interfaces.retriever_factory import RetrieverFactory
from components.reader.interfaces.text_compressor import TextCompressor
from logging import Logger
from components.retriever.interfaces.retriever_repository import RetrieverRepository
from injector import (
    get_config,
    get_embedder_config,
    get_embedder_factory,
    get_embedder_repository,
    get_logger,
    get_compressor,
    get_retriever_config,
    get_retriever_factory,
    get_retriever_repository,
)
from pages.utils.embedder_retriever import (
    convert_query_to_vector,
    create_retriever,
    display_embedder,
    display_retriever,
    extracted_data,
    select_embedder,
    select_retriever,
)
from pages.utils.utils import (
    extracted_text_to_label,
    setup_session_state_vars,
    select_domain_instance,
    setup_page,
)

config = get_config()
logger: Logger = get_logger()
embedder_repository: EmbedderRepository = get_embedder_repository()
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
    else:
        extracted_data(selected_domain)

    st.title(f"{selected_domain.name}")

    setup_retriever(selected_domain)


def setup_retriever(selected_domain):
    if st.session_state.get("context_embedder", False) and not st.session_state.get(
        "change_embedder", None
    ):
        embedder: Embedder = st.session_state.get("context_embedder")
        display_embedder(embedder)
        if (
            st.session_state.get("context_retriever", None)
            and st.session_state.get("context_retriever_values", None)
            and not st.session_state.get("change_retriever", None)
        ):
            retriever: Retriever = create_retriever(selected_domain.id, embedder)
            display_retriever(retriever)
            query(embedder, retriever)
        else:
            st.session_state["change_retriever"] = True
            select_retriever()
    else:
        st.session_state["change_embedder"] = True
        select_embedder()


def query(embedder: Embedder, retriever: Retriever):
    query_text = st.text_input(
        label="Enter your query:",
        value=st.session_state.get("context_query_text", ""),
        key="query_text",
        on_change=lambda: st.session_state.update(
            context_query_text=st.session_state["query_text"]
        ),
    )
    if st.button("Submit query") or query_text:
        _run_query(query_text, embedder, retriever)


def _run_query(query_text, embedder, retriever):
    if query_text:
        kwargs = {
            "query_vector": pickle.loads(
                convert_query_to_vector(query_text, embedder)[0][1]
            ),
        }
        try:
            display_embeddings(retriever.retrieve(**kwargs))
        except AssertionError as e:
            st.error(e)
        except RuntimeError as e:
            st.error(f"Error retrieving embeddings: {e}")


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
    setup_session_state_vars(
        [
            ("context_domain", None),
            ("context_embedder", None),
            ("context_retriever", None),
            ("texts_to_use", {}),
            ("only_chosen_embedder", True),
        ]
    )


if __name__ == "__main__":
    main()

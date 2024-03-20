import pickle
import streamlit as st
from components.database.models import Domain
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
    cleanup_texts_to_use,
    convert_query_to_vector,
    count_selected_texts,
    create_retriever,
    display_embedder,
    display_retriever,
    select_embedder,
    select_retriever,
    setup_texts_to_use,
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


def extracted_data(selected_domain: Domain = None):

    extracted_texts = get_extracted_texts(selected_domain)
    setup_texts_to_use(selected_domain, extracted_texts)
    num_texts = count_selected_texts(extracted_texts)

    with st.sidebar.popover(f"Texts ({num_texts})"):
        with st.container(border=True):
            st.session_state["texts_to_use"] = {}
            for extracted_text in extracted_texts:
                checkbox_key = f"{extracted_text.name}.{extracted_text.type}"
                st.session_state["texts_to_use"][extracted_text] = st.checkbox(
                    label=extracted_text_to_label(extracted_text),
                    key=checkbox_key,
                    value=st.session_state.get(f"context_{checkbox_key}", False),
                    on_change=lambda key=checkbox_key: st.session_state.update(
                        {f"context_{key}": st.session_state.get(f"{key}", False)}
                    ),
                )
        if len(extracted_texts) > 0:
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("Select all", key="select_all_texts_toggle"):
                    st.session_state["select_all_texts_button"] = True
                    st.rerun()
            with col2:
                if st.button("Deselect all", key="deselect_all_texts_toggle"):
                    st.session_state["deselect_all_texts_button"] = True
                    st.rerun()

        st.checkbox(
            "Only shows texts that match the chosen embedder",
            key="only_chosen_embedder_toggle",
            on_change=lambda: st.session_state.update(
                only_chosen_embedder=not st.session_state["only_chosen_embedder"]
            ),
            value=st.session_state["only_chosen_embedder"],
        )


def get_extracted_texts(selected_domain):
    if st.session_state.get("only_chosen_embedder", False) and st.session_state.get(
        "context_embedder", False
    ):
        embedder: Embedder = st.session_state["context_embedder"]
        embedder_config = (
            embedder.get_configuration().get("params", {}).get("model", None)
        )
        if embedder_config:
            extracted_texts = retriever_repository.list_texts_by_domain_and_embedder(
                selected_domain.name, embedder_config
            )
            cleanup_texts_to_use(extracted_texts)
        else:
            st.warning("Embedder model name not found. Showing all texts.")
            extracted_texts = embedder_repository.list_embedded_texts_by_domain(
                selected_domain.name
            )
    else:
        extracted_texts = embedder_repository.list_embedded_texts_by_domain(
            selected_domain.name
        )

    return extracted_texts


def setup_retriever(selected_domain):
    if st.session_state.get("context_embedder", False) and not st.session_state.get(
        "change_embedder", None
    ):
        embedder: Embedder = st.session_state.get("context_embedder")
        with st.container(border=True):
            st.subheader(f"{embedder.get_configuration()['method']}")
            display_embedder(embedder, False)
        if (
            st.session_state.get("context_retriever", None)
            and st.session_state.get("context_retriever_values", None)
            and not st.session_state.get("change_retriever", None)
        ):
            retriever: Retriever = create_retriever(selected_domain.id, embedder)
            with st.container(border=True):
                st.subheader(f"{retriever.get_configuration()['method']}")
                display_retriever(retriever, False)
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


def _run_query(query_text: str, embedder: Embedder, retriever: Retriever) -> None:
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

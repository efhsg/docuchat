from typing import List
import streamlit as st
from components.database.models import ExtractedText
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
from pages.utils.streamlit_form import StreamlitForm
from pages.utils.utils import (
    get_index,
    init_form_values,
    save_form_values_to_context,
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


def setup_texts_to_use(selected_domain, extracted_texts):
    cleanup_texts_to_use(extracted_texts)
    if (
        st.session_state.get("context_text_domain_id", False)
        and st.session_state.get("context_text_domain_id") == selected_domain.id
    ):
        if st.session_state.get("select_all_texts_button", False):
            set_all_texts_to_selected(extracted_texts)
            del st.session_state["select_all_texts_button"]
        elif st.session_state.get("deselect_all_texts_button", False):
            del st.session_state["deselect_all_texts_button"]
            set_all_texts_to_deselected(extracted_texts)
    else:
        st.session_state["context_text_domain_id"] = selected_domain.id
        set_all_texts_to_selected(extracted_texts)


def count_selected_texts(extracted_texts: List[ExtractedText]) -> int:
    num_selected_texts = 0
    for extracted_text in extracted_texts:
        checkbox_key = f"{extracted_text.name}.{extracted_text.type}"
        if st.session_state.get(f"context_{checkbox_key}", False):
            num_selected_texts += 1
    return num_selected_texts


def is_extracted_text_present(
    extracted_text: ExtractedText, extracted_texts: List[ExtractedText]
) -> bool:
    return any(et.id == extracted_text.id for et in extracted_texts)


def cleanup_texts_to_use(extracted_texts: List[ExtractedText] = []):
    remove_deleted_texts_from_texts_to_use(extracted_texts)
    add_new_texts_to_texts_to_use(extracted_texts)


def remove_deleted_texts_from_texts_to_use(extracted_texts: List[ExtractedText] = []):
    texts_to_use = st.session_state.get("texts_to_use", {})
    texts_to_use_keys = set(texts_to_use.keys())
    for key in texts_to_use_keys:
        if not any(
            key.name == et.name and key.type == et.type for et in extracted_texts
        ):
            if st.session_state.get(f"context_{key.name}.{key.type}", False):
                del st.session_state[f"context_{key.name}.{key.type}"]


def add_new_texts_to_texts_to_use(extracted_texts: List[ExtractedText] = []):
    texts_to_use_keys = set(
        f"context_{et.name}.{et.type}"
        for et in st.session_state.get("texts_to_use", {}).keys()
    )

    for et in extracted_texts:
        context_session_key = f"context_{et.name}.{et.type}"
        if context_session_key not in texts_to_use_keys:
            st.session_state[context_session_key] = True


def set_all_texts_to_selected(extracted_texts: List = []):
    for extracted_text in extracted_texts:
        st.session_state[f"{extracted_text.name}.{extracted_text.type}"] = True
        st.session_state[f"context_{extracted_text.name}.{extracted_text.type}"] = True


def set_all_texts_to_deselected(extracted_texts: List = []):
    for extracted_text in extracted_texts:
        st.session_state[f"{extracted_text.name}.{extracted_text.type}"] = False
        st.session_state[f"context_{extracted_text.name}.{extracted_text.type}"] = False


def select_embedder():
    embedder_options = embedder_config.embedder_options
    method_options = list(embedder_options.keys())
    embed_method = st.selectbox(
        label="Select an embedder method to use for the query text:",
        key="embed_method",
        options=method_options,
        index=get_index(method_options, "context_embedder"),
        on_change=lambda: st.session_state.update(
            context_embedder=st.session_state["embed_method"]
        ),
    )
    embedder_details = embedder_options[embed_method]
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
                embed_method, **updated_form_values
            )
            save_form_values_to_context(updated_form_values)
            st.session_state["context_embedder"] = embedder
            st.session_state["change_embedder"] = False
            st.rerun()


def display_embedder(embedder: Embedder = None, expanded: bool = True):
    params = embedder.get_configuration().get("params", {})

    with st.expander("Parameters", expanded=expanded):
        markdown_table = "Parameter | Value\n:- | -\n"
        for key, value in params.items():
            markdown_table += f"{key} | {value}\n"
        st.markdown(markdown_table, unsafe_allow_html=True)
        st.write("")

    if st.button("🔄 Change embedder"):
        st.session_state["change_embedder"] = True
        st.rerun()


def select_retriever():

    retriever_options = retriever_config.retriever_options
    method = st.selectbox(
        label="Select a retriever method:",
        options=list(retriever_options.keys()),
        key="retriever_method",
        index=get_index(list(retriever_options.keys()), "context_retriever"),
        on_change=lambda: st.session_state.update(
            context_retriever=st.session_state["retriever_method"]
        ),
    )
    retriever_details = retriever_options[method]

    form_config = {
        "fields": retriever_details.get("fields", {}),
        "validations": retriever_details.get("validations", []),
        "constants": retriever_details.get("constants", {}),
    }

    initial_form_values = get_initial_form_values(retriever_details, form_config)

    form = StreamlitForm(form_config)
    updated_form_values = form.generate_form(
        initial_form_values,
        "retriever_process",
        "Configure Retriever",
    )
    if updated_form_values:
        if form.validate_form_values(updated_form_values):
            save_form_values_to_context(updated_form_values)
            st.session_state["context_retriever"] = method
            st.session_state["context_retriever_values"] = updated_form_values
            st.session_state["change_retriever"] = False
            st.rerun()


def get_initial_form_values(retriever_details, form_config):
    initial_form_values = init_form_values(retriever_details["fields"].items())
    if (
        st.session_state.get("context_embedder")
        and "embedding_dim" in form_config["fields"]
    ):
        embedder: Embedder = st.session_state["context_embedder"]
        embedder_params = embedder.get_params()
        embedding_dim = embedder_params.get("embedding_dimension")
        if embedding_dim:
            form_config["fields"]["embedding_dim"]["default"] = embedding_dim
            initial_form_values["embedding_dim"] = embedding_dim
    return initial_form_values


def create_retriever(domain_id: int, embedder: Embedder = None) -> Retriever:
    kwargs = {
        "domain_id": domain_id,
        "text_ids": st.session_state["texts_to_use"],
        **st.session_state["context_retriever_values"],
    }
    if st.session_state.get("only_chosen_embedder", False):
        kwargs["embedder_config"] = embedder.get_configuration()

    kwargs["text_ids"] = [
        int(extracted_text.id)
        for extracted_text, is_checked in st.session_state["texts_to_use"].items()
        if is_checked
    ]
    return retriever_factory.create_retriever(
        st.session_state["context_retriever"],
        **kwargs,
    )


def display_retriever(retriever, expanded: bool = True):
    params = retriever.get_configuration().get("params", {})

    with st.expander("Parameters", expanded=expanded):
        markdown_table = "Parameter | Value\n:- | -\n"
        for key, value in params.items():
            markdown_table += f"{key} | {value}\n"
        st.markdown(markdown_table, unsafe_allow_html=True)
        st.write("")

    if st.button("🔄 Change retriever"):
        st.session_state["change_retriever"] = True
        st.rerun()


def convert_query_to_vector(query: str, embedder: Embedder) -> list:
    return embedder.embed_chunks([(0, query)])

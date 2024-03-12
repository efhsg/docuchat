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
from pages.utils.streamlit_form import StreamlitForm
from pages.utils.utils import (
    extracted_text_to_label,
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


def extracted_data(selected_domain):
    with st.sidebar:
        st.title(f"Texts to use")

        if st.session_state.get("only_chosen_embedder", False) and st.session_state.get(
            "context_embedder", False
        ):
            embedder: Embedder = st.session_state["context_embedder"]
            embedder_model_name = (
                embedder.get_configuration().get("params", {}).get("model", None)
            )
            if embedder_model_name:
                extracted_texts = (
                    retriever_repository.list_texts_by_domain_and_embedder(
                        selected_domain.name, embedder_model_name
                    )
                )
            else:
                st.warning("Embedder model name not found. Showing all texts.")
                extracted_texts = embedder_repository.list_embedded_texts_by_domain(
                    selected_domain.name
                )
        else:
            extracted_texts = embedder_repository.list_embedded_texts_by_domain(
                selected_domain.name
            )

        with st.container(border=True):
            st.session_state["texts_to_use"] = {
                extracted_text: st.checkbox(
                    label=extracted_text_to_label(extracted_text),
                    value=st.session_state["use_all_texts"],
                    key=f"{extracted_text.name}.{extracted_text.type}",
                )
                for extracted_text in extracted_texts
            }

        st.checkbox(
            "Select all texts",
            key="select_all_texts_toggle",
            on_change=lambda: st.session_state.update(
                use_all_texts=not st.session_state["use_all_texts"]
            ),
            value=st.session_state["use_all_texts"],
        )

        st.checkbox(
            "Same embedder as your query",
            key="only_chosen_embedder_toggle",
            on_change=lambda: st.session_state.update(
                only_chosen_embedder=not st.session_state["only_chosen_embedder"]
            ),
            value=st.session_state["only_chosen_embedder"],
        )


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


def display_embedder(embedder):
    with st.container(border=True):
        config = embedder.get_configuration()
        method_display = f"{config['method']}"
        params = config.get("params", {})
        fields_display = ", ".join([f"{key}: {value}" for key, value in params.items()])
        st.markdown(f"**{method_display}**, {fields_display}")
        if st.button("Change embedder"):
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


def display_retriever(retriever):
    with st.container(border=True):
        config = retriever.get_configuration()
        method_display = f"{config['method']}"
        params = config.get("params", {})
        fields_display = ", ".join([f"{key}: {value}" for key, value in params.items()])
        st.markdown(f"**{method_display}**, {fields_display}")
        if st.button("Change retriever"):
            st.session_state["change_retriever"] = True
            st.rerun()


def convert_query_to_vector(query: str, embedder: Embedder) -> list:
    return embedder.embed([(0, query)])

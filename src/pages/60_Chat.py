import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from components.chatter.chatter_config import ModelOptionsFetchError
from components.chatter.interfaces.chatter import Chatter
from components.chatter.interfaces.chatter_factory import ChatterFactory
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
    get_chatter_config,
    get_chatter_factory,
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
    count_selected_texts,
    create_retriever,
    display_embedder,
    display_retriever,
    get_initial_form_values,
    select_embedder,
    select_retriever,
    setup_texts_to_use,
)
from pages.utils.streamlit_form import StreamlitForm
from pages.utils.utils import (
    extracted_text_to_label,
    get_index,
    save_form_values_to_context,
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
chatter_config = get_chatter_config()
chatter_factory: ChatterFactory = get_chatter_factory()


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

    setup_chatter(selected_domain)


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


def setup_chatter(selected_domain):
    if st.session_state.get("context_embedder", False) and not st.session_state.get(
        "change_embedder", None
    ):
        embedder: Embedder = st.session_state.get("context_embedder")
        with st.sidebar.popover("Embedder"):
            display_embedder(embedder)
        if (
            st.session_state.get("context_retriever", None)
            and st.session_state.get("context_retriever_values", None)
            and not st.session_state.get("change_retriever", None)
        ):
            retriever: Retriever = create_retriever(selected_domain.id, embedder)
            with st.sidebar.popover("Retriever"):
                display_retriever(retriever)
            if (
                st.session_state.get("context_chatter", None)
                and st.session_state.get("context_chatter_values", None)
                and not st.session_state.get("change_chatter", None)
            ):
                chatter: Chatter = create_chatter_instance(
                    selected_domain.id, embedder, retriever
                )
                with st.sidebar.popover("Chatter"):
                    display_chatter_instance(chatter)
                chat(selected_domain.id, embedder, retriever, chatter)
            else:
                st.session_state["change_chatter"] = True
                select_chatter()
        else:
            st.session_state["change_retriever"] = True
            select_retriever()
    else:
        st.session_state["change_embedder"] = True
        select_embedder()


def select_chatter():
    try:
        chatter_options = chatter_config.chatter_options
        # logger.info(chatter_options)
    except ModelOptionsFetchError as e:
        st.error(f"Getting options failed: {e}")
        chatter_options = {}

    method = st.selectbox(
        label="Select a chatter:",
        options=list(chatter_options.keys()),
        key="chatter_method",
        index=get_index(list(chatter_options.keys()), "context_chatter"),
        on_change=lambda: st.session_state.update(
            context_chatter=st.session_state["chatter_method"]
        ),
    )
    chatter_details = chatter_options[method]

    form_config = {
        "fields": chatter_details.get("fields", {}),
        "validations": chatter_details.get("validations", []),
        "constants": chatter_details.get("constants", {}),
    }

    initial_form_values = get_initial_form_values(chatter_details, form_config)

    form = StreamlitForm(form_config)
    updated_form_values = form.generate_form(
        initial_form_values,
        "chatter_process",
        "Configure Chatter",
    )
    if updated_form_values:
        if form.validate_form_values(updated_form_values):
            save_form_values_to_context(updated_form_values)
            st.session_state["context_chatter"] = method
            st.session_state["context_chatter_values"] = updated_form_values
            st.session_state["change_chatter"] = False
            st.rerun()


def create_chatter_instance(
    domain_id: int, embedder: Embedder = None, retriever: Retriever = None
) -> Chatter:
    kwargs = {
        **st.session_state["context_chatter_values"],
    }
    return chatter_factory.create_chatter(
        st.session_state["context_chatter"],
        **kwargs,
    )


def display_chatter_instance(chatter: Chatter):
    with st.container(border=True):
        config = chatter.get_configuration()
        method_display = f"{config['method']}"
        params = config.get("params", {})
        fields_display = ", ".join([f"{key}: {value}" for key, value in params.items()])
        st.markdown(f"**{method_display}**, {fields_display}")
        if st.button("Change chatter"):
            st.session_state["change_chatter"] = True
            st.rerun()


def chat(
    domain_id: int,
    embedder: Embedder = None,
    retriever: Retriever = None,
    chatter: Chatter = None,
):
    with st.container(border=True):
        user_query = st.chat_input("Start chatting here...")
        if user_query:
            try:
                st.session_state["chat_history"].append(
                    HumanMessage(content=user_query)
                )
                st.session_state["chat_history"].append(
                    AIMessage(content=query(user_query))
                )
            except Exception as e:
                st.error(f"Failed to chat: {e}")
        if st.button("Clear history"):
            st.session_state["chat_history"] = []
        display_messages()


def display_messages():
    for message in reversed(st.session_state["chat_history"]):
        if isinstance(message, AIMessage):
            with st.container(border=True):
                with st.chat_message("AI"):
                    st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.container(border=True):
                with st.chat_message("User"):
                    st.write(message.content)


def query(query: str = ""):
    return "Whitney"


def setup_session_state():
    setup_session_state_vars(
        [
            ("context_domain", None),
            ("context_embedder", None),
            ("context_retriever", None),
            ("context_chatter", None),
            ("only_chosen_embedder", True),
            ("texts_to_use", {}),
            ("chat_history", []),
        ]
    )


if __name__ == "__main__":
    main()

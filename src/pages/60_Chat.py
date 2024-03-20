from typing import Any, Tuple
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
from utils.env_utils import getenv

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
    if edit_embedder_condition():
        trigger_embedder_selection()
    else:
        embedder = setup_and_display_embedder()

        if edit_retriever_condition():
            trigger_retriever_selection()
        else:
            retriever = setup_and_display_retriever(selected_domain.id, embedder)

            if edit_chatter_condition():
                trigger_chatter_selection()
            else:
                setup_and_chat(selected_domain.id, embedder, retriever)


def setup_and_display_embedder():
    embedder: Embedder = st.session_state.get("context_embedder")
    with st.sidebar.popover(f"{embedder.get_configuration()['method']}"):
        display_embedder(embedder)
    return embedder


def setup_and_display_retriever(domain_id, embedder):
    retriever: Retriever = create_retriever(domain_id, embedder)
    with st.sidebar.popover(f"{retriever.get_configuration()['method']}"):
        display_retriever(retriever)
    return retriever


def setup_and_chat(domain_id, embedder, retriever):
    chatter: Chatter = create_chatter_instance(domain_id, embedder, retriever)
    with st.sidebar.popover(f"{chatter.get_configuration()['method']}"):
        display_chatter_instance(chatter)
    chat(domain_id, embedder, retriever, chatter)


def trigger_embedder_selection():
    st.session_state["change_embedder"] = True
    select_embedder()


def trigger_retriever_selection():
    st.session_state["change_retriever"] = True
    select_retriever()


def trigger_chatter_selection():
    st.session_state["change_chatter"] = True
    select_chatter()


def edit_embedder_condition():
    return not st.session_state.get("context_embedder", False) or st.session_state.get(
        "change_embedder", None
    )


def edit_retriever_condition():
    return (
        not st.session_state.get("context_retriever", None)
        or not st.session_state.get("context_retriever_values", None)
        or st.session_state.get("change_retriever", None)
    )


def edit_chatter_condition():
    return (
        not st.session_state.get("context_chatter", None)
        and not st.session_state.get("context_chatter_values", None)
        or st.session_state.get("change_chatter", None)
    )


def select_chatter():
    chatter_options = chatter_config.chatter_options
    for chatter_name, chatter_data in chatter_options.items():
        model_key = next(
            (key for key in chatter_data["fields"] if key.endswith("_model")), None
        )
        if model_key:
            model_data = chatter_data["fields"][model_key]
            if not model_data["options"]:
                st.error(
                    f"Getting model options for {chatter_name} failed. Please check your API_KEY in .env"
                )

    method_options = list(chatter_options.keys())
    method = st.selectbox(
        label="Select a chatter:",
        options=method_options,
        key="chatter_method",
        index=get_index(
            method_options,
            "context_chatter",
            default=(
                method_options.index(getenv("CHATTER_DEFAULT"))
                if getenv("CHATTER_DEFAULT") in method_options
                else 0
            ),
        ),
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


def display_chatter_instance(chatter):
    params = chatter.get_configuration().get("params", {})

    with st.expander("Parameters", expanded=True):
        markdown_table = "Parameter | Value\n:- | -\n"
        for key, value in params.items():
            markdown_table += f"{key} | {value}\n"
        st.markdown(markdown_table, unsafe_allow_html=True)
        st.write("")

    if st.button("🔄 Change chatter"):
        st.session_state["change_chatter"] = True
        st.rerun()


def chat(
    domain_id: int,
    embedder: Embedder,
    retriever: Retriever,
    chatter: Chatter,
):
    stream = chatter.get_params().get("stream", False)
    with st.container(border=True):
        user_query = st.chat_input("Start chatting here...")
        current_chat_placeholder = display_messages()
    if user_query:
        with current_chat_placeholder.container(border=True):
            with st.chat_message("AI"):
                ai_placeholder = st.empty()
            with st.chat_message("User"):
                st.write(user_query)

        st.session_state["chat_history"].append(HumanMessage(content=user_query))
        if stream:
            chat_with_streaming_on(
                domain_id,
                embedder,
                retriever,
                chatter,
                ai_placeholder=ai_placeholder,
            )
        else:
            chat_with_streaming_off(
                domain_id,
                embedder,
                retriever,
                chatter,
                ai_placeholder=ai_placeholder,
            )
    manage_history(chatter)


def chat_with_streaming_on(
    domain_id,
    embedder,
    retriever,
    chatter: Chatter,
    ai_placeholder,
):
    try:
        original_generator = chatter.chat(parse_chat_history_for_LLM(), {})
        wrapped_generator = generator_wrapper(original_generator)
        with ai_placeholder:
            st.write_stream(wrapped_generator)
    except Exception as e:
        st.error(f"Failed to chat: {e}")


def generator_wrapper(chat_stream_generator):
    streamed_responses = ""
    for response_part in chat_stream_generator:

        streamed_responses += response_part
        yield response_part

    st.session_state["chat_history"].append(AIMessage(content=streamed_responses))


def chat_with_streaming_off(
    domain_id,
    embedder,
    retriever,
    chatter: Chatter,
    ai_placeholder,
):
    try:
        response = chatter.chat(parse_chat_history_for_LLM(), {})
        with ai_placeholder:
            st.write(response)
        st.session_state["chat_history"].append(AIMessage(content=response))
    except Exception as e:
        st.error(f"Failed to chat: {e}")


def parse_chat_history_for_LLM():
    history = [
        {
            "role": "user" if isinstance(message, HumanMessage) else "system",
            "content": message.content,
        }
        for message in st.session_state.get("chat_history", [])
    ]

    if st.session_state.get("use_history", False):
        return history
    else:
        recent_user_message = next(
            (msg for msg in reversed(history) if msg["role"] == "user"), None
        )
        return [recent_user_message] if recent_user_message else []


def display_messages():
    current_chat_placeholder = st.empty()
    with st.container(border=True):
        for message in reversed(st.session_state["chat_history"]):
            if isinstance(message, HumanMessage):
                with st.chat_message("User"):
                    st.write(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("AI"):
                    st.write(message.content)
    return current_chat_placeholder


def manage_history(chatter: Chatter):
    with st.sidebar.container(border=True):
        if st.session_state.get("context_use_history", False):
            try:
                display_context_info(chatter)
            except Exception as e:
                logger.error(e)
                st.error("Tokens left: not available due to an error")
        st.checkbox(
            "Use history",
            key="use_history",
            on_change=lambda: st.session_state.update(
                context_use_history=st.session_state["use_history"]
            ),
            value=st.session_state["context_use_history"],
        )
        if st.session_state.get("use_history") and st.session_state["chat_history"]:
            if st.button("Clear history"):
                st.session_state["chat_history"] = []
                st.rerun()


def display_context_info(chatter: Chatter):
    try:
        history = (
            parse_chat_history_for_LLM()
            if st.session_state.get("context_use_history", False)
            else []
        )
        num_messages = len(history)
        tokens_left_info = "Tokens left: Not available due to an error"

        if history:
            truncation_count = chatter.history_truncated_by()
            messages_info = f"History: {num_messages - truncation_count} messages" + (
                f" ({truncation_count} truncated)" if truncation_count > 0 else ""
            )
            context_window = chatter.get_params().get("context_window", 0)
            tokens_left = chatter.get_num_tokens_left(parse_chat_history_for_LLM())

            st.info(messages_info)
            if isinstance(tokens_left, int):
                st.metric(
                    label="Tokens Left",
                    value=tokens_left,
                    delta=f"Out of {context_window}",
                )
            else:
                st.warning(tokens_left_info)
        else:
            st.info("No chat history to display.")

    except Exception as e:
        logger.error(f"Error calculating tokens left: {e}")
        st.error(
            "Sorry, we encountered an issue calculating tokens left. Please try refreshing or contact support for assistance."
        )


def log_last_two_messages():

    last_two_messages = st.session_state.get("chat_history")[-2:]

    readable_messages = []
    for message in last_two_messages:
        if isinstance(message, HumanMessage):
            prefix = "User: "
        elif isinstance(message, AIMessage):
            prefix = "AI: "
        else:
            prefix = "Unknown: "
        readable_messages.append(f"{prefix}{message.content}")

    readable_last_2_messages = "\n".join(readable_messages)

    if readable_last_2_messages:
        logger.info(f"Last 2 messages:\n{readable_last_2_messages}")
    else:
        logger.info("No messages to display.")


def setup_session_state():
    setup_session_state_vars(
        [
            ("context_domain", None),
            ("context_embedder", None),
            ("context_retriever", None),
            ("context_chatter", None),
            ("only_chosen_embedder", True),
            ("texts_to_use", {}),
            ("context_use_history", True),
            ("chat_history", []),
        ]
    )


if __name__ == "__main__":
    main()

import streamlit as st
from components.embedder.interfaces.embedder import Embedder
from components.embedder.interfaces.embedder_factory import EmbedderFactory
from components.embedder.interfaces.embedder_repository import EmbedderRepository
from components.reader.interfaces.text_compressor import TextCompressor
from logging import Logger
from injector import (
    get_config,
    get_embedder_config,
    get_embedder_factory,
    get_embedder_repository,
    get_logger,
    get_compressor,
)
from pages.utils.streamlit_form import StreamlitForm
from pages.utils.utils import (
    generate_default_name,
    get_index,
    init_form_values,
    save_form_values_to_context,
    select_texts,
    set_default_state,
    select_domain,
    setup_page,
)

config = get_config()
embedder_config = get_embedder_config()
logger: Logger = get_logger()
compressor: TextCompressor = get_compressor()
embedder_repository: EmbedderRepository = get_embedder_repository()
embedder_factory: EmbedderFactory = get_embedder_factory()


def main():
    setup_page()
    setup_session_state()
    selected_domain = select_domain(list_domain_names_with_chunks())
    if selected_domain is None:
        st.info("First chunk some texts")
        return
    st.title(f"{selected_domain}")
    with st.container(border=True):
        selected_text = select_texts(
            embedder_repository.list_extracted_texts_by_domain_with_chunks(
                selected_domain
            )
        )
        if selected_text:
            selected_chunk_process_id = select_chunk_process(
                embedder_repository.list_chunk_processes_by_text(selected_text.id)
            )
    if selected_chunk_process_id:
        create_embedding_processes(selected_text.id, selected_chunk_process_id)
    manage_embedding_processes(selected_text.id)


def setup_session_state():
    default_session_states = [
        ("message", (None, None)),
        ("context_domain", None),
        ("context_text", None),
        ("context_embed_method", None),
        ("context_chunk_process_id", None),
    ]
    for state_name, default_value in default_session_states:
        set_default_state(state_name, default_value)


def list_domain_names_with_chunks():
    domain_options = [
        (domain.name) for domain in embedder_repository.list_domains_with_chunks()
    ]

    return domain_options


def select_chunk_process(chunk_processes):

    if not chunk_processes:
        st.write("No chunk processes available.")
        return None

    chunk_process_options = {
        f"{cp.method} - {cp.parameters.get('name', 'Unnamed')} | {', '.join([f'{k}: {v}' for k, v in cp.parameters.items() if k != 'name'])}": cp.id
        for cp in chunk_processes
    }

    selected_label = st.selectbox(
        "Select a chunk process to embed:",
        options=list(chunk_process_options.keys()),
        index=get_index(
            list(chunk_process_options.values()), "context_chunk_process_id"
        ),
        key="selected_chunk_process",
        on_change=lambda: st.session_state.update(
            context_chunk_process_id=chunk_process_options[
                st.session_state["selected_chunk_process"]
            ]
        ),
    )

    return chunk_process_options[selected_label]


def create_embedding_processes(selected_text_id, selected_chunk_process_id):
    embedder_options = embedder_config.embedder_options

    with st.container(border=True):
        method = select_method(list(embedder_options.keys()))

        embedder_details = embedder_options[method]
        form_config = {
            "fields": embedder_details["fields"],
            "validations": embedder_details.get("validations", []),
            "constants": embedder_details["constants"],
        }

        form = StreamlitForm(form_config)
        updated_form_values = form.generate_form(
            init_form_values(embedder_details["fields"].items()),
            "embed_process",
            "Start Embedding",
        )

    if updated_form_values:
        if form.validate_form_values(updated_form_values):
            try:
                save_form_values_to_context(updated_form_values)
                process_chunks_to_embed(
                    selected_text_id,
                    selected_chunk_process_id,
                    method,
                    updated_form_values,
                )
            except Exception as e:
                st.error(f"Failed to validate or process chunks: {e}")


def select_method(method_options):
    method = st.selectbox(
        label="Select method",
        options=method_options,
        key="embed_method",
        index=get_index(method_options, "context_embed_method"),
        on_change=lambda: st.session_state.update(
            context_embed_method=st.session_state["embed_method"]
        ),
    )

    return method


def process_chunks_to_embed(
    selected_text_id, selected_chunk_process_id, method, values
):
    with st.spinner("Embedding..."):
        embedder: Embedder = embedder_factory.create_embedder(method, **values)

        values["name"] = generate_default_name()
        embedding_process_id = embedder_repository.create_embedding_process(
            extracted_text_id=selected_text_id,
            method=method,
            parameters=values,
        )

        chunks = embedder_repository.get_chunks_by_process_id(selected_chunk_process_id)

        total_chunks = len(chunks)
        progress_bar = st.progress(0)

        try:
            for i, chunk in enumerate(chunks):
                text = compressor.decompress(chunk.chunk)
                embedding = embedder.embed([(chunk.id, text)])[0][1]
                embedder_repository.save_embedding(
                    embedding_process_id, chunk.id, embedding
                )
                progress_percentage = int(((i + 1) / total_chunks) * 100)
                progress_bar.progress(progress_percentage)

                logger.debug(f"Chunk ID {chunk.id} embedded and saved successfully.")
        except Exception as e:
            st.error(
                f"Error embedding chunks for chunk process ID {selected_chunk_process_id}: {e}"
            )
        finally:
            progress_bar.empty()


def manage_embedding_processes(selected_text_id):
    if selected_text_id is None:
        return

    embedding_sessions = embedder_repository.list_embedding_processes_by_text(
        selected_text_id
    )
    if not embedding_sessions:
        st.write("No embedding sessions found for this text.")
        return

    st.subheader("Embeddings")
    for session in embedding_sessions:
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
                delete_embedding_process(session)
            if st.session_state.get(f"renaming_{session.id}", False):
                rename_embedding_session(session)


def show_process_header(session):
    method_display = f"{session.method} ({session.parameters['name']})"
    embedder_options = embedder_config.embedder_options[session.method]

    embeddings = embedder_repository.list_embeddings_by_process(session)
    embedding_count = 0 if embeddings is None else len(embeddings)

    fields_order = embedder_options.get(
        "order", list(embedder_options.get("fields").keys())
    )

    fields_display = ", ".join(
        [
            f"{key}: {session.parameters[key]}"
            for key in fields_order
            if key in session.parameters
        ]
    )

    st.markdown(
        f"**{method_display}**\n\n{fields_display} ({embedding_count} embeddings)"
    )


def rename_embedding_session(session):
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
                embedder_repository.update_embedding_process(session)
                st.session_state[f"renaming_{session.id}"] = False
                st.rerun()
            except Exception as e:
                st.error(f"Failed to rename embedding process: {e}")
    with col2:
        if st.button("Cancel", key=f"cancel_{session.id}"):
            st.session_state[f"renaming_{session.id}"] = False
            st.rerun()


def delete_embedding_process(session):
    try:
        embedder_repository.delete_embedding_process(session.id)
        st.rerun()
    except Exception as e:
        st.error(f"Failed to delete embedding process ID {session.id}: {e}")


if __name__ == "__main__":
    main()

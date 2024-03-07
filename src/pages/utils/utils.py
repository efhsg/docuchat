import os
import streamlit as st
from PIL import Image
from datetime import datetime
from datetime import datetime
from typing import Dict, List, Union, Any
from components.database.models import Domain, ExtractedText
from injector import get_config, get_logger
from operator import lt, le, gt, ge, eq, ne

config = get_config()
logger = get_logger()


def setup_page(page_title="Docuchat"):
    image = Image.open(config.logo_small_path)
    st.set_page_config(
        page_title=page_title,
        page_icon=image,
        layout="wide",
        initial_sidebar_state="auto",
    )


def show_messages():
    message, message_type = st.session_state["message"]
    if message:
        if message_type == "success":
            st.success(message)
        elif message_type == "error":
            st.error(message)
        st.session_state["message"] = (None, None)


def select_domain(domain_options: List[str]) -> str:
    return st.sidebar.selectbox(
        label="Select Domain",
        options=domain_options,
        key="selected_domain",
        index=get_index(domain_options, "context_domain"),
        on_change=lambda: st.session_state.update(
            context_domain=st.session_state["selected_domain"], select_all_texts=False
        ),
    )


def select_domain_instance(domain_options: List[Domain]) -> Domain:
    if not domain_options:
        return None

    domain_names = [domain.name for domain in domain_options]

    selected_domain_name = select_domain(domain_names)
    
    for domain in domain_options:
        if domain.name == selected_domain_name:
            return domain

    return None


def select_texts(text_options: List[ExtractedText]) -> ExtractedText:
    options_dict = {f"{extracted_text_to_label(text)}": text for text in text_options}

    selected_label = st.selectbox(
        label="Select a text",
        options=list(options_dict.keys()),
        key="selected_text",
        index=get_index(list(options_dict.keys()), "context_text"),
        on_change=lambda: st.session_state.update(
            context_text=st.session_state["selected_text"]
        ),
    )

    for text in text_options:
        if extracted_text_to_label(text) == selected_label:
            return text

    raise ValueError("Selected text not found.")


def set_default_state(
    key: str, default: Union[bool, List, Dict[str, int], int]
) -> None:
    if key not in st.session_state:
        st.session_state[key] = default


def get_index(options: List[str], context: str) -> int:
    return (
        0
        if st.session_state[context] not in options
        else options.index(st.session_state[context])
    )


def split_filename(file) -> tuple[str, str]:
    if "." in file.name:
        file_name, file_extension = file.name.rsplit(".", 1)
        file_extension = file_extension.lower()
    else:
        file_name = file.name
        file_extension = ""
    return file_name, file_extension


def join_filename(base_name: str, extension: str) -> str:
    if extension and not extension.startswith("."):
        extension = "." + extension
    return f"{base_name}{extension}"


def extracted_text_to_label(extracted_text: ExtractedText):
    return f"{extracted_text.name} ({extracted_text.type.lstrip('.')})"


def extracted_text_original_name_to_label(extracted_text: ExtractedText):
    base_filename, extension = os.path.splitext(extracted_text.original_name)
    if extension:
        return f"({base_filename} {extension.lstrip('.')})"
    else:
        return base_filename


def filename_extension_to_label(filename: str, extension: str) -> str:
    clean_extension = extension.lstrip(".")
    return f"{filename} ({clean_extension})"


def url_to_name_and_extension(url: str) -> tuple[str, str]:
    stripped_url = url.split("//")[-1].rstrip("/").lstrip("www.")
    current_date = datetime.utcnow().strftime("%Y%m%d")
    filename = f"{stripped_url}_{current_date}"
    extension = ".web"

    if len(filename) + len(extension) > 255:
        max_length = 255 - len(current_date) - len(extension) - 1
        stripped_url = stripped_url[:max_length]
        filename = f"{stripped_url}_{current_date}"

    return filename, extension


def init_form_values(fields):
    return {
        param: st.session_state.get(f"context_{param}", details["default"])
        for param, details in fields
    }


def save_form_values_to_context(values):
    for value in values:
        st.session_state[f"context_{value}"] = values[value]


def generate_default_name() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

import streamlit as st
from PIL import Image
from datetime import datetime
from datetime import datetime
from urllib.parse import quote
from typing import Dict, List, Union
from components.database.models import ExtractedText
from injector import get_config, get_logger

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


def select_domain(domain_options):
    return st.sidebar.selectbox(
        label="Select Domain",
        options=domain_options,
        key="selected_domain",
        index=get_index(domain_options, "context_domain"),
        on_change=lambda: st.session_state.update(
            context_domain=st.session_state["selected_domain"], select_all_texts=False
        ),
    )


from typing import Dict, Any, Union
import streamlit as st


from typing import Dict, Union, Callable, Any
import streamlit as st


def generate_form(
    form_config: Dict[str, Any],
    form_values: Dict[str, Union[str, int, bool]],
    name: str,
) -> bool:
    with st.form(key=f"{name}"):
        widget_mapping: Dict[str, Callable[..., Any]] = {
            "string": st.text_input,
            "number": st.number_input,
            "select": st.selectbox,
            "checkbox": st.checkbox,
        }

        for param, details in form_config["params"].items():
            widget_func = widget_mapping.get(details["type"])
            if widget_func:
                widget_args = {"label": details["label"], "key": f"{name}_{param}"}
                if details["type"] == "number":
                    widget_args["min_value"] = details.get("min_value", 0)
                    widget_args["value"] = form_values[param]
                elif details["type"] == "select":
                    widget_args["options"] = details["options"]
                    widget_args["index"] = (
                        details["options"].index(form_values[param])
                        if form_values[param] in details["options"]
                        else 0
                    )
                elif details["type"] in ["string", "checkbox"]:
                    widget_args["value"] = form_values[param]

                form_values[param] = widget_func(**widget_args)

        submit_button = st.form_submit_button(label="Chunk")
    return submit_button


def validate_form_values(
    form_values: Dict[str, Any], validations: List[Dict[str, Any]]
) -> bool:
    for validation in validations:
        rule = validation["rule"]
        field1, operator, field2 = rule

        value1 = form_values.get(field1)
        value2 = form_values.get(field2) if field2 in form_values else field2

        if not evaluate_rule(value1, operator, value2):
            st.error(validation["message"])
            return False
    return True


def evaluate_rule(value1: Any, operator: str, value2: Any) -> bool:
    if operator == "<=":
        return value1 <= value2
    elif operator == "<":
        return value1 < value2
    return True


def select_text(text_options: List[ExtractedText]) -> ExtractedText:
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
    return f"{extracted_text.name} ({extracted_text.type})"


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

import streamlit as st
from PIL import Image
from typing import Dict, List, Union
from injector import get_config

config = get_config()


def setup_page(page_title="Docuchat"):
    image = Image.open(config.logo_small_path)
    st.set_page_config(
        page_title=page_title,
        page_icon=image,
        layout="wide",
        initial_sidebar_state="auto",
    )


def set_default_state(
    key: str, default: Union[bool, List, Dict[str, int], int]
) -> None:
    if key not in st.session_state:
        st.session_state[key] = default


def get_index(options, context):
    return (
        0
        if st.session_state[context] not in options
        else options.index(st.session_state[context])
    )

import streamlit as st
from PIL import Image


def home_page():

    image = Image.open("./img/logo_small.png")
    st.set_page_config(
        page_title="Docuchat home",
        page_icon=image,
        layout="wide",
        initial_sidebar_state="auto",
    )

    st.image("./img/logo_small.png")

    st.title("DocuChat")
    st.write("Upload, embed and chat with multiple files")


if __name__ == "__main__":
    home_page()

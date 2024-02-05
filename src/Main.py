import sys
import streamlit as st


def home_page():
    st.set_page_config(page_title="DocuChat :books:", page_icon=":books:")
    st.title("DocuChat :books:")
    st.write("Upload, embed and chat with multiple files")
    st.write("Running Python " + sys.version)


if __name__ == "__main__":
    home_page()

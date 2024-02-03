import streamlit as st


def home_page():
    st.set_page_config(page_title="DocuChat", page_icon=":books:")
    st.title("DocuChat")
    st.write("Upload, embed and chat with multiple files :books:")


if __name__ == "__main__":
    home_page()

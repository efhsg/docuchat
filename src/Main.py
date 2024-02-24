import streamlit as st
from components.database.migration import Migration
from injector import get_config
from pages.utils.utils import setup_page

config = get_config()


def home_page():
    setup_page()
    col1, col2 = st.columns([1, 1])

    with col1:
        st.title("Welcome to DocuChat!")
        st.write(
            """
            DocuChat enhances your document collaboration experience.
            Upload, embed, and chat with multiple sources seamlessly.
            """
        )

    with col2:
        st.image(config.logo_small_path, width=175)

    st.markdown("---")
    st.header("How DocuChat Works")

    st.markdown(
        """
        **Step 1: Create a domain**
        - You can define as many domains as you like to organize your content

        **Step 2: Extract text**
        - You can upload multiple files.
        - DocuChat automatically extracts text from these files for processing.
        - We support: pdf, txt

        **Step 3: Select and combine extracted text**
        - Extracted text is then selected and combined into a knowledge base.
        - This process involves vector embedding to facilitate efficient information retrieval.

        **Step 4: Chat with your knowledge base**
        - Utilize your favorite Large Language Model (LLM) to chat with the created knowledge base.
        - Ask questions or seek information directly from the content of your uploaded documents.
        """
    )

    st.markdown("---")
    st.write(
        "Ready to get started? Upload your files and explore the capabilities of DocuChat."
    )


def check_db():
    db_manager = Migration(config=config)
    try:
        db_manager.check_and_apply_migrations()
    except Exception as e:
        st.error(f"Database setup failed: {e}")
        st.stop()


if __name__ == "__main__":
    check_db()
    home_page()

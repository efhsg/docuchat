import streamlit as st
from PIL import Image
from Config import Config


def home_page():

    image = Image.open(Config.logo_small_path)

    st.set_page_config(
        page_title="DocuChat Home",
        page_icon=image,
        layout="wide",
        initial_sidebar_state="auto",
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.title("Welcome to DocuChat!")
        st.write(
            """
            DocuChat enhances your document collaboration experience.
            Upload, embed, and chat with multiple files seamlessly.
            """
        )

    with col2:
        st.image(Config.logo_small_path, width=175)

    st.markdown("---")
    st.header("How DocuChat Works")

    st.markdown(
        """
        **Step 1: Upload Files and Extract Text**
        - You can upload multiple PDF files.
        - DocuChat automatically extracts text from these files for processing.

        **Step 2: Select and Combine Extracted Text**
        - Extracted text is then selected and combined into a knowledge base.
        - This process involves vector embedding to facilitate efficient information retrieval.

        **Step 3: Chat with Your Knowledge Base**
        - Utilize your favorite Large Language Model (LLM) to chat with the created knowledge base.
        - Ask questions or seek information directly from the content of your uploaded documents.
        """
    )

    st.markdown("---")
    st.write(
        "Ready to get started? Upload your files and explore the capabilities of DocuChat."
    )


if __name__ == "__main__":
    home_page()

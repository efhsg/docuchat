# DocuChat


<p align="center">
  <img width="200" height="200" src="https://github.com/efhsg/docuchat/blob/main/src/img/logo_small_v2.1_trans.png">
</p>

DocuChat is a cutting-edge application designed to streamline the way users interact with documents. It enables users to upload, embed, and engage in conversations within the context of multiple files simultaneously. This application is perfect for teams looking for an efficient way to collaborate on documents, share insights, and provide feedback in real time. Whether you're working on academic research, business reports, or any project that involves PDFs, DocuChat enhances your productivity by integrating document management with interactive chat functionality.

Built on Python and leveraging the power of Streamlit, DocuChat offers a user-friendly interface that makes document collaboration intuitive and accessible from anywhere. Follow the quick start guide below to get started with DocuChat and transform how you work with files.

## Quick start

- **Check out the repository**
  ```
  git clone <repository-url>
  ```
- **Navigate to your local project directory**
  ```
  cd <local project directory>
  ```  
- **Copy the environment variables example file**
  ```
  cp .env.example .env
  ```
- **Set your API keys in the `.env` file**


### Setup using Docker (recommended for ease of use):
  ```
  docker-compose up -d
  ```

### Setup using a virtual environment (for more control):
- Install Python 3.12.1 (we recommend using pyenv)
- Navigate to your local project directory
- Create a virtual environment and activate it
  ```
  python -m venv .venv
  source .venv/bin/activate
  ```
- Upgrade pip and install dependencies
  ```
  pip install --upgrade pip && pip install -r requirements.txt
  ```
- Set environment variables to avoid bytecode generation and to run unbuffered
  ```
  export PYTHONDONTWRITEBYTECODE=1 && export PYTHONUNBUFFERED=1
  ```
- Run the application
  ```
  cd src && streamlit run Main.py
  ```

### To view the app:
- Open your web browser and navigate to `http://localhost:8501/`

Enjoy collaborating on your documents with DocuChat!

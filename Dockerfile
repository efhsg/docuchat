FROM python:3.12.1-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /src
ARG USER_ID
ARG USER_NAME

RUN adduser --uid $USER_ID --disabled-password --gecos "" $USER_NAME && chown -R $USER_NAME /src
USER $USER_NAME

CMD ["streamlit", "run", "Main.py"]
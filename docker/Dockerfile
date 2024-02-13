FROM python:3.12.1-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Upgrade pip
RUN pip install --upgrade pip

# Copy the requirements file into the container
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Set the working directory for the application
WORKDIR /src

# Arguments to create a user with specific UID and username
ARG USER_ID
ARG USER_NAME

# Create a user, add /data directory for persisting files, and change ownership
RUN adduser --uid $USER_ID --disabled-password --gecos "" $USER_NAME \
    && mkdir /data \
    && chown -R $USER_NAME:$USER_NAME /src /data

# Change to the user
USER $USER_NAME

# Command to run the application
CMD ["streamlit", "run", "Main.py", "--server.port", "8502"]
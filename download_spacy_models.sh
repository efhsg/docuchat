#!/bin/bash

# Load .env file
if [ -f .env ]; then
    export $(cat .env | sed 's/#.*//g' | xargs)
fi

# Check if CHUNKER_NLP_MODEL_OPTIONS is set
if [[ -z "$CHUNKER_NLP_MODEL_OPTIONS" ]]; then
    echo "Error: CHUNKER_NLP_MODEL_OPTIONS environment variable is not set. Exiting."
    exit 0
fi

echo "Installing: $CHUNKER_NLP_MODEL_OPTIONS"

IFS=',' read -ra MODELS <<< "$CHUNKER_NLP_MODEL_OPTIONS"
for model in "${MODELS[@]}"; do
    echo "Downloading spaCy model: $model"
    python -m spacy download $model
done

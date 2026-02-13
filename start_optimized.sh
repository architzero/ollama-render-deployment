#!/bin/bash

echo "Starting Ollama service..."
ollama serve &

# Wait longer for startup on free tier
echo "Waiting for Ollama to initialize..."
sleep 30

# Check if model exists before pulling
if ollama list | grep -q "llama3.2:3b"; then
    echo "Model already exists, skipping download"
else
    echo "Downloading llama3.2:3b (this may take a while on first run)..."
    ollama pull llama3.2:3b
fi

# Preload the model
echo "Preloading model..."
ollama run llama3.2:3b "Hello" --verbose=false

echo "Ollama is ready!"
wait

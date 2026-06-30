#!/bin/bash

echo "Starting setup for RAG Backend..."

# Check Python
if command -v python3.12 &>/dev/null; then
    echo "Python 3.12 found."
elif command -v python3 &>/dev/null; then
    echo "Python 3 found."
else
    echo "Please install Python 3.12+"
    exit 1
fi

# Check Docker
if command -v docker &>/dev/null; then
    echo "Docker found."
else
    echo "Please install Docker."
    exit 1
fi

# Check Ollama
if command -v ollama &>/dev/null; then
    echo "Ollama found."
    echo "Ensuring qwen2.5:1.5b is available..."
    ollama pull qwen2.5:1.5b
else
    echo "========================================="
    echo "Ollama is missing!"
    echo "Please install Ollama from https://ollama.com/"
    echo "Then run: ollama run qwen2.5:1.5b"
    echo "========================================="
    exit 1
fi

# Create .env if missing
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

echo "Setup complete! Run 'docker compose up' to start the backend."
echo "Swagger URL: http://localhost:8000/docs"

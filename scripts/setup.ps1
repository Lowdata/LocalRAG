Write-Host "Starting setup for RAG Backend..."

# Check Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "Python found."
} else {
    Write-Host "Please install Python 3.12+"
    exit 1
}

# Check Docker
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Docker found."
} else {
    Write-Host "Please install Docker."
    exit 1
}

# Check Ollama
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Write-Host "Ollama found."
    Write-Host "Ensuring qwen2.5:1.5b is available..."
    ollama pull qwen2.5:1.5b
} else {
    Write-Host "========================================="
    Write-Host "Ollama is missing!"
    Write-Host "Please install Ollama from https://ollama.com/"
    Write-Host "Then run: ollama run qwen2.5:1.5b"
    Write-Host "========================================="
    exit 1
}

# Create .env if missing
if (-Not (Test-Path .env)) {
    Write-Host "Creating .env from .env.example..."
    Copy-Item .env.example .env
}

Write-Host "Setup complete! Run 'docker compose up' to start the backend."
Write-Host "Swagger URL: http://localhost:8000/docs"

if (Get-Command "docker-compose" -ErrorAction SilentlyContinue) {
    docker-compose up
} elseif (Get-Command "docker" -ErrorAction SilentlyContinue) {
    docker compose up
} else {
    Write-Host "Neither docker compose nor docker-compose found."
    exit 1
}

import time
import httpx
import numpy as np


def measure():
    url = "http://localhost:8000/api/v1/query"
    # We will measure just retrieval latency first (end-to-end is harder without hitting Ollama every time, actually the query endpoint hits ollama).
    # Wait, /api/v1/query hits Ollama and does end-to-end!
    # To get retrieval only, we can hit the vector store directly.
    pass


if __name__ == "__main__":
    measure()

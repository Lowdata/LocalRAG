import os
import lancedb
import httpx
import asyncio
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"


async def generate_qa_pair(chunk_text: str):
    prompt = f"""Given the following text chunk, generate a realistic user question that can be answered by this text. Also provide a concise 'gold answer'.
Return strictly in JSON format like this: {{"question": "the question", "gold_answer": "the answer"}}
Text chunk:
{chunk_text}
"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            res = await client.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
            )
            if res.status_code == 200:
                return json.loads(res.json().get("response", "{}"))
        except Exception as e:
            print(e)
            return None


async def main():
    # 1. Clear db
    if os.path.exists("data/lancedb"):
        os.system("rm -rf data/lancedb")

    # 2. Ingest docs
    doc_files = [f"docs/{d}" for d in os.listdir("docs") if d.endswith(".md")]
    async with httpx.AsyncClient(timeout=60.0) as client:
        for f in doc_files:
            print(f"Ingesting {f}...")
            with open(f, "rb") as fd:
                await client.post(
                    "http://localhost:8000/api/v1/ingest",
                    files={"file": (f, fd, "text/markdown")},
                )

    # 3. Read chunks from DB
    db = lancedb.connect("data/lancedb")
    table = db.open_table("chunks")
    chunks = (
        table.search([0.0] * 384).limit(100).to_list()
    )  # getting all since limit 100 > num chunks

    print(f"Total chunks: {len(chunks)}")

    dataset = []
    # 4. Generate 20 Q/A pairs
    count = 0
    for chunk in chunks:
        if len(chunk["text"].split()) < 20:
            continue  # skip small chunks
        if count >= 20:
            break

        print(f"Generating Q/A for chunk {chunk['chunk_id']}...")
        qa = await generate_qa_pair(chunk["text"])
        if qa and "question" in qa:
            dataset.append(
                {
                    "question": qa["question"],
                    "gold_answer": qa["gold_answer"],
                    "relevant_chunk_ids": [chunk["chunk_id"]],
                    "document_path": chunk["document_path"],
                }
            )
            count += 1

    with open("eval_dataset.json", "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"Generated {len(dataset)} questions in eval_dataset.json")


if __name__ == "__main__":
    asyncio.run(main())

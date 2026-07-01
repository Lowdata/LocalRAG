import os
import json
import httpx
import asyncio

async def fix_lancedb_and_dataset():
    # 1. Clear db
    if os.path.exists("data/lancedb"):
        os.system("rm -rf data/lancedb")
        
    # 2. Ingest correctly
    doc_files = [f"docs/{d}" for d in os.listdir("docs") if d.endswith(".md")]
    async with httpx.AsyncClient(timeout=60.0) as client:
        for f in doc_files:
            basename = os.path.basename(f)
            print(f"Ingesting {basename}...")
            with open(f, "rb") as fd:
                await client.post("http://localhost:8000/api/v1/ingest", files={"file": (basename, fd, "text/markdown")})
                
    # 3. Fix json dataset
    with open("eval_dataset.json", "r") as f:
        data = json.load(f)
        
    for item in data:
        if item["document_path"].startswith("docs/"):
            item["document_path"] = item["document_path"][5:]
        item["relevant_chunk_ids"] = [
            cid[5:] if cid.startswith("docs/") else cid for cid in item["relevant_chunk_ids"]
        ]
        
    with open("eval_dataset.json", "w") as f:
        json.dump(data, f, indent=2)
        
    print("Fixed database and dataset!")

if __name__ == "__main__":
    asyncio.run(fix_lancedb_and_dataset())

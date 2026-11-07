import pymupdf

doc = pymupdf.open("notes.pdf")
pages = []

for i, page in enumerate(doc):
    text = page.get_text()
    pages.append({"page": i + 1, "text": text})

print("Total pages:", len(pages))


def make_chunks(pages, chunk_size=1200, overlap=200):
    chunks = []
    for p in pages:
        text = p["text"]
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append({"page": p["page"], "text": text[start:end]})
            start = end - overlap
    return chunks


chunks = make_chunks(pages)
print("Total chunks:", len(chunks))

import chromadb

client = chromadb.PersistentClient(path="chroma_db")
try:
    client.delete_collection("notes")
except Exception:
    pass
collection = client.get_or_create_collection(name="notes")

collection.upsert(
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    documents=[c["text"] for c in chunks],
    metadatas=[{"page": c["page"]} for c in chunks],
)
print("Stored chunks:", collection.count())

results = collection.query(
    query_texts=["What is Arabic NLP?"],
    n_results=3,
)

for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print("Page", meta["page"], ":", doc[:200])
    print("---")
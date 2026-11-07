import chromadb
from dotenv import load_dotenv
from google import genai

load_dotenv()
llm = genai.Client()

db = chromadb.PersistentClient(path="chroma_db")
collection = db.get_collection(name="notes")


def ask(question, n_results=8):
    results = collection.query(query_texts=[question], n_results=n_results)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    print("\n[DEBUG] Retrieved pages:", [m["page"] for m in metas])

    context = ""
    for doc, meta in zip(docs, metas):
        context += f"[Page {meta['page']}]\n{doc}\n\n"

    prompt = f"""Answer the question using ONLY the context below.
If the answer is not in the context, say "I could not find this in the document."
Mention the page numbers you used.

Context:
{context}

Question: {question}
"""
    response = llm.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )
    return response.text


if __name__ == "__main__":
    while True:
        q = input("\nQuestion (type 'exit' to quit): ")
        if q.strip().lower() == "exit":
            break
        print("\nAnswer:", ask(q))
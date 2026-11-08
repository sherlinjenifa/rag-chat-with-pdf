import time

import chromadb
import pymupdf
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client()
db = chromadb.PersistentClient(path="chroma_db")

st.set_page_config(page_title="RAG Chat with PDF")
st.title("📚 Chat with your PDF")
st.write("Upload a PDF and ask questions about it.")


def generate_with_retry(prompt, tries=3):
    for attempt in range(tries):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
            )
            return response.text
        except errors.ServerError:
            if attempt < tries - 1:
                time.sleep(2 * (attempt + 1))
    return None


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


def build_index(file_bytes):
    doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            pages.append({"page": i + 1, "text": text})

    chunks = make_chunks(pages)
    if not chunks:
        return 0

    try:
        db.delete_collection("notes")
    except Exception:
        pass
    collection = db.create_collection("notes")

    for i in range(0, len(chunks), 500):
        batch = chunks[i:i + 500]
        collection.add(
            ids=[f"chunk_{i + j}" for j in range(len(batch))],
            documents=[c["text"] for c in batch],
            metadatas=[{"page": c["page"]} for c in batch],
        )
    return len(chunks)


uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded_file is not None:
    file_key = f"{uploaded_file.name}-{uploaded_file.size}"

    if st.session_state.get("file_key") != file_key:
        with st.spinner("Reading and indexing the PDF..."):
            count = build_index(uploaded_file.getvalue())
        if count == 0:
            st.error("No readable text found in this PDF.")
            st.stop()
        st.session_state["file_key"] = file_key
        st.session_state["chunk_count"] = count

    st.success(f"PDF ready ({st.session_state['chunk_count']} chunks indexed)")

    question = st.text_input("Ask a question about the document")

    if st.button("Ask"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Searching the document..."):
                collection = db.get_collection("notes")
                results = collection.query(
                    query_texts=[question],
                    n_results=min(6, st.session_state["chunk_count"]),
                )
                docs = results["documents"][0]
                metas = results["metadatas"][0]

                context = ""
                for text, meta in zip(docs, metas):
                    context += f"[Page {meta['page']}]\n{text}\n\n"

                prompt = f"""Answer the question using ONLY the context below.
If the answer is not in the context, say "I could not find this in the document."
Mention the page numbers you used.

Context:
{context}

Question: {question}
"""
                answer = generate_with_retry(prompt)

            st.subheader("Answer")
            if answer is None:
                st.error("The AI model is busy right now. Please try again in a minute.")
            else:
                st.write(answer)
            st.caption(f"Pages searched: {sorted(set(m['page'] for m in metas))}")

            with st.expander("Retrieved context (debug)"):
                st.text(context)
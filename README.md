# RAG Chat with PDF

A Retrieval-Augmented Generation (RAG) app that answers questions from an uploaded PDF, with page-level references.

**Live demo:** https://rag-chat-with-pdf-myllmdkyifiwarejank2hz.streamlit.app/

## How it works
1. The PDF is read with PyMuPDF and split into overlapping chunks (1200 characters, 200 overlap).
2. Chunks are embedded and stored in ChromaDB.
3. For each question, the most relevant chunks are retrieved.
4. Gemini generates an answer using only the retrieved context and cites page numbers.

## Tech stack
Python, Streamlit, ChromaDB, PyMuPDF, Gemini API

## Run locally
1. Clone the repo and create a virtual environment.
2. `pip install -r requirements.txt`
3. Create a `.env` file with `GEMINI_API_KEY=your_key`
4. `streamlit run app.py`

## Experiments and known limitations
- Chunk size 800 vs 1200: no clear improvement on a failing question.
- Questions containing author names (for example "Haouhat et al.") sometimes retrieve the wrong pages. The same question without the name retrieved the correct page. Pure semantic search can miss exact names.
- Possible improvement: hybrid search (keyword + semantic).
- The Gemini API can return 503 errors under high demand, so the app retries up to 3 times.
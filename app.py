import streamlit as st
from ask import ask

st.title("Chat with your PDF")
question = st.text_input("Ask a question about the document")

if st.button("Ask") and question:
    with st.spinner("Searching the document..."):
        answer = ask(question)
    st.write(answer)
from __future__ import annotations

import os

import streamlit as st

from app.ui.api_client import APIClientError, RAGAPIClient


def _render_sources(response: dict) -> None:
    sources = response.get("sources", [])
    with st.expander(f"Sources ({len(sources)})"):
        if not sources:
            st.caption("No source chunks were returned.")
            return
        for index, source in enumerate(sources, start=1):
            title = source.get("title") or "Unknown source"
            page = source.get("page_start") or "page unavailable"
            st.markdown(f"**[{index}] {title}, page {page}** | score: `{source.get('score', 0):.3f}`")
            st.caption(source.get("text", ""))
        if response.get("citations"):
            st.caption("Citation markers in the answer refer to these retrieved chunks.")


def main() -> None:
    st.set_page_config(page_title="Book RAG", page_icon="RAG", layout="wide")
    st.title("Book RAG Assistant")
    st.caption("Ask questions grounded in your indexed AI/ML books.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("Settings")
        api_url = st.text_input("FastAPI URL", os.getenv("API_BASE_URL", "http://localhost:8000"))
        top_k = st.slider("Retrieved chunks", min_value=1, max_value=10, value=5)
        book_title = st.text_input("Book filter (optional)")
        st.divider()
        st.header("Add a book")
        upload = st.file_uploader("PDF or EPUB", type=["pdf", "epub"])
        strategy = st.selectbox("Chunking strategy", ["semantic", "fixed"])
        if st.button("Index book", disabled=upload is None, use_container_width=True):
            try:
                result = RAGAPIClient(api_url).ingest(upload.name, upload.getvalue(), strategy=strategy)
                st.success(f"Indexed {result['chunks_indexed']} chunks from {result['filename']}.")
            except APIClientError as exc:
                st.error(str(exc))

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("response"):
                response = message["response"]
                label = "grounded" if response.get("grounded") else "fallback"
                st.caption(f"{label} | retrieval confidence: {response.get('confidence', 0):.3f}")
                _render_sources(response)

    question = st.chat_input("Ask about your books")
    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Searching books and drafting a grounded answer..."):
            try:
                response = RAGAPIClient(api_url).query(
                    question,
                    k=top_k,
                    book_title=book_title or None,
                )
                st.markdown(response.get("answer", ""))
                label = "grounded" if response.get("grounded") else "fallback"
                st.caption(f"{label} | retrieval confidence: {response.get('confidence', 0):.3f}")
                _render_sources(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response.get("answer", ""), "response": response}
                )
            except APIClientError as exc:
                message = f"API error: {exc}"
                st.error(message)
                st.session_state.messages.append({"role": "assistant", "content": message})


if __name__ == "__main__":
    main()

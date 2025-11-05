import os
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from ..schemas.ai import ClientMessage
from ..config.settings import get_settings
from .scraper import scrape


CHROMA_DB_PATH = "./chroma_db"

def _get_chunks(text: str) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
        separators=["\n\n", "\n", " ", ""],
        length_function=len,
    )

    return text_splitter.split_text(text)


def _get_embeddings() -> OpenAIEmbeddings:
    settings = get_settings()
    api_key = settings.OPENAI_API_KEY

    return OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key) #type: ignore


def _get_vectorstore() -> Chroma:
    """Load the persisted Chroma vectorstore. If it doesn't exist, this will create a new handle.

    Returns a Chroma instance wired with the same embeddings used during ingestion.
    """
    embeddings = _get_embeddings()

    return Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)


def retrieve_docs(msgs: list[ClientMessage], k: int = 5) -> List[Document]:
    """Return the top-k documents from the vectorstore for a given query.

    This is a thin wrapper so callers (routers/services) can easily fetch
    relevant chunks to be used as context for generation.
    """
    vectorstore = _get_vectorstore()

    query = ""
    for msg in reversed(msgs):
        if msg.role == "user":
            if isinstance(msg.content, str):
                query = msg.content
                break
            elif isinstance(msg.content, list):
                text_part = next((p.text for p in msg.content if p.type == "text"), None) # type: ignore
                if text_part:
                    query = text_part
                    break
    if not query:
        query = "Vestibular Unicamp 2026" # dummy query

    return vectorstore.similarity_search(query, k=k)

async def create_vector_store(urls: list[str]) -> Chroma:
    """Ingest a list of URLs, split into chunks and persist a Chroma DB.

    Note: embeddings are created with the configured OPENAI API key.
    """
    scrape_results = await scrape(urls)

    documents = []
    for scrape_result in scrape_results:
        chunks = _get_chunks(scrape_result.text)

        documents.extend(
            [
                Document(
                    page_content=chunk,
                    metadata={
                        "source_url": scrape_result.url,
                        "title": str(scrape_result.title),
                        "status_code": scrape_result.status_code,
                    },
                )
                for chunk in chunks
            ]
        )

    embeddings = _get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=documents, embedding=embeddings, persist_directory=CHROMA_DB_PATH
    )

    return vectorstore

def chroma_db_populated() -> bool:
    """Return if the existence of CHROMA_DB_PATH."""

    try:
        if not os.path.isdir(CHROMA_DB_PATH):
            return False

        # Check for any files or subdirectories inside the directory
        for _ in os.scandir(CHROMA_DB_PATH):
            return True
        return False
    except Exception:
        return False
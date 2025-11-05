import os
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from .scraper import scrape


CHROMA_DB_PATH = "./chroma_db"


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


def get_chunks(text: str) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
        separators=["\n\n", "\n", " ", ""],
        length_function=len,
    )

    return text_splitter.split_text(text)


def get_embeddings() -> OpenAIEmbeddings:
    # settings = get_settings()
    # api_key = getattr(settings, "OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

    return OpenAIEmbeddings(model="text-embedding-3-small")


def get_vectorstore() -> Chroma:
    """Load the persisted Chroma vectorstore. If it doesn't exist, this will create a new handle.

    Returns a Chroma instance wired with the same embeddings used during ingestion.
    """
    embeddings = get_embeddings()

    return Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)


def retrieve_docs(query: str, k: int = 5) -> List[Document]:
    """Return the top-k documents from the vectorstore for a given query.

    This is a thin wrapper so callers (routers/services) can easily fetch
    relevant chunks to be used as context for generation.
    """
    vectorstore = get_vectorstore()

    return vectorstore.similarity_search(query, k=k)


async def create_vector_store(urls: list[str]) -> Chroma:
    """Ingest a list of URLs, split into chunks and persist a Chroma DB.

    Note: embeddings are created with the configured OPENAI API key.
    """
    scrape_results = await scrape(urls)

    documents = []
    for scrape_result in scrape_results:
        chunks = get_chunks(scrape_result.text)

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

    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=documents, embedding=embeddings, persist_directory=CHROMA_DB_PATH
    )

    return vectorstore

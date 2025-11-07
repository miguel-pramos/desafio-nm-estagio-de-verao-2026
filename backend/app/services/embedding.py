import os
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from ..schemas.ai import ClientMessage
from ..config.settings import get_settings
from .scraper import scrape
from .query_rewriter import get_query_rewriter, RewriteStrategy


CHROMA_DB_PATH = "./chroma_db"

def _get_chunks(text: str) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
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


def retrieve_docs(
    msgs: list[ClientMessage],
    k: int = 5,
    use_query_rewriting: bool = True,
    rewrite_strategy: RewriteStrategy = RewriteStrategy.COMBINED,
) -> List[Document]:
    """Return the top-k documents from the vectorstore for a given query.

    This is a thin wrapper so callers (routers/services) can easily fetch
    relevant chunks to be used as context for generation.
    """
    vectorstore = _get_vectorstore()

    # Extract the user query from messages
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
    
    # Apply query rewriting if enabled
    queries_to_search = [query]
    if use_query_rewriting:
        rewriter = get_query_rewriter()
        queries_to_search.extend(rewriter.rewrite(query, strategy=rewrite_strategy))
    
    print(queries_to_search)
    
    # Perform similarity search with original query
    # Then collect additional results from rewritten queries
    all_docs = {}  # Use dict to deduplicate by content
    doc_scores = {}  # Track best score for each document
    
    for search_query in queries_to_search:
        try:
            # Get results for this query variation
            results = vectorstore.similarity_search_with_score(search_query, k=k)
            
            for doc, score in results:
                # Use page content as key for deduplication
                doc_key = doc.page_content[:100]  # Use first 100 chars as key
                
                # Keep the document with the best (lowest) score
                if doc_key not in doc_scores or score < doc_scores[doc_key]:
                    all_docs[doc_key] = doc
                    doc_scores[doc_key] = score
                    
        except Exception:
            continue
    
    # Sort by score and return top k
    sorted_docs = sorted(
        [(doc, score) for doc, score in zip(all_docs.values(), doc_scores.values())],
        key=lambda x: x[1]
    )
    
    result = [doc for doc, _ in sorted_docs[:k]]
    
    return result

async def create_vector_store(base_url: str) -> Chroma:
    """Ingest a list of URLs, split into chunks and persist a Chroma DB.

    Note: embeddings are created with the configured OPENAI API key.
    """
    scrape_results = await scrape(base_url)

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
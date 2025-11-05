import asyncio
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from .scraper import scrape


CHROMA_DB_PATH = "./chroma_db"


def get_chunks(text: str) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
        separators=["\n\n", "\n", " ", ""],
        length_function=len,
    )

    return text_splitter.split_text(text)


async def create_vector_store(urls: list[str]) -> Chroma:
    scrape_results = await scrape(urls)

    documents = []
    for scrape_result in scrape_results:
        chunks = get_chunks(scrape_result.text)

        documents.extend([
            Document(
                page_content=chunk,
                metadata={
                    "source_url": scrape_result.url,
                    "title": str(scrape_result.title),
                    "status_code": scrape_result.status_code,  
                },
            )
            for chunk in chunks
        ])

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key="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",
    )

    vectorstore = Chroma.from_documents(
        documents=documents, embedding=embeddings, persist_directory=CHROMA_DB_PATH
    )

    return vectorstore


if __name__ == "__main__":
    asyncio.run(create_vector_store(["https://www.comvest.unicamp.br"]))

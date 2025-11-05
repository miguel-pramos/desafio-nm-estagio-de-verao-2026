import httpx
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional, Set

# --- Configuração como Constantes ---

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

BLOCK_TAGS_TO_REMOVE: Set[str] = {"script", "style", "noscript", "template"}
STRUCTURAL_TAGS_TO_PRUNE: Set[str] = {"header", "footer", "nav", "aside"}


@dataclass(slots=True)
class ScrapeResult:
    """Um objeto de resultado simplificado."""

    url: str
    text: str
    title: Optional[str]
    status_code: int


async def scrape(
    urls: list[str],
    *,
    client: Optional[httpx.AsyncClient] = None,
    timeout: float = 15.0,
) -> list[ScrapeResult]:

    created_client = False

    if client is None:
        client = httpx.AsyncClient(
            follow_redirects=True,
            timeout=timeout,
            headers={"User-Agent": DEFAULT_USER_AGENT},
        )
        created_client = True
    else:
        client = client

    try:
        normalized_urls = [
            url if re.match(r"^https?://", url) else f"https://{url}" for url in urls
        ]

        results: list[ScrapeResult] = []

        for normalized_url in normalized_urls:
            response = await client.get(normalized_url)

            response.raise_for_status()

            # Validação de tipo de conteúdo (essencial)
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type:
                raise ValueError(
                    f"Content type '{content_type}' de '{response.url}' não é HTML."
                )

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove tags indesejadas 
            for element in soup.find_all(BLOCK_TAGS_TO_REMOVE):
                element.decompose()
            for element in soup.find_all(STRUCTURAL_TAGS_TO_PRUNE):
                element.decompose()

            text = soup.get_text(separator=" ", strip=True)
            text = re.sub(r"\s+", " ", text).strip()

            # Extrair título (ainda útil para RAG)
            title = soup.title.string.strip() if soup.title and soup.title.string else None

            results.append(
                ScrapeResult(
                    url=str(response.url),  # URL final após redirecionamentos
                    text=text,
                    title=title,
                    status_code=response.status_code,
                )
            )
        return results
    
    except httpx.HTTPStatusError as exc:
        print(f"Erro de HTTP ao buscar {exc.response.url}: {exc.response.status_code}")
        raise
    except (httpx.HTTPError, ValueError, Exception) as exc:
        print(f"Erro ao processar: {exc}")
        raise
    finally:
        if created_client:
            await client.aclose()

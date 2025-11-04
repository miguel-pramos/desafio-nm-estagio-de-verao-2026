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
    url: str,
    *,
    client: Optional[httpx.AsyncClient] = None,
    timeout: float = 15.0,
) -> ScrapeResult:

    # 1. Gerenciamento do cliente HTTP
    created_client = False
    client_to_use: httpx.AsyncClient

    if client is None:
        client_to_use = httpx.AsyncClient(
            follow_redirects=True,
            timeout=timeout,
            headers={"User-Agent": DEFAULT_USER_AGENT},
        )
        created_client = True
    else:
        client_to_use = client

    try:
        # 2. Normalizar e buscar a URL
        normalized_url = url if re.match(r"^https?://", url) else f"https://{url}"
        response = await client_to_use.get(normalized_url)

        # 3. Validar a Resposta (Forma Enxuta)
        # O .raise_for_status() já cuida de erros 4xx e 5xx
        response.raise_for_status()

        # Validação de tipo de conteúdo (essencial)
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            raise ValueError(
                f"Content type '{content_type}' de '{response.url}' não é HTML."
            )

        # 4. Parsear e Limpar o HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove tags indesejadas (lógica original)
        for element in soup.find_all(BLOCK_TAGS_TO_REMOVE):
            element.decompose()
        for element in soup.find_all(STRUCTURAL_TAGS_TO_PRUNE):
            element.decompose()

        # 5. Extrair Texto (Forma Enxuta)
        # .get_text() é mais eficiente para limpeza de espaços
        # separator=" " garante que palavras não se colem (ex: "palavra1palavra2")
        # strip=True remove espaços em branco no início e fim
        text = soup.get_text(separator=" ", strip=True)

        # Limpeza final para colapsar múltiplos espaços em um único
        text = re.sub(r"\s+", " ", text).strip()

        # Extrair título (ainda útil para RAG)
        title = soup.title.string.strip() if soup.title and soup.title.string else None

        return ScrapeResult(
            url=str(response.url),  # URL final após redirecionamentos
            text=text,
            title=title,
            status_code=response.status_code,
        )

    except httpx.HTTPStatusError as exc:
        print(f"Erro de HTTP ao buscar {url}: {exc.response.status_code}")
        # É importante relançar para que o chamador saiba que falhou
        raise
    except (httpx.HTTPError, ValueError, Exception) as exc:
        print(f"Erro ao processar {url}: {exc}")
        raise
    finally:
        if created_client:
            await client_to_use.aclose()

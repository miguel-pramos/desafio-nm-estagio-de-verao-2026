from urllib.parse import urlparse
import httpx
import re
from enum import Enum
from dataclasses import dataclass

from bs4 import BeautifulSoup
from typing import Optional, Set

from pydantic import BaseModel, Field

# --- Configuração como Constantes ---

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

BLOCK_TAGS_TO_REMOVE: Set[str] = {"script", "style", "noscript", "template"}
STRUCTURAL_TAGS_TO_PRUNE: Set[str] = {"header", "footer", "nav", "aside"}


class CrawlStrategy(str, Enum):
    """Crawling strategy"""

    STATIC = "static"
    RECURSIVE = "recursive"


@dataclass(slots=True)
class ScrapeResult:
    """Simplified result object"""

    url: str
    text: str
    title: Optional[str]
    status_code: int


class URLCrawler:
    """Recursive crawler that searchs for links to be read."""

    def __init__(
        self,
        base_url: str,
        max_depth: int = 5,
        max_urls: int = 100,
        follow_external: bool = False,
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None,
    ):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.follow_external = follow_external
        self.include_patterns = [re.compile(p) for p in (include_patterns or [])]
        self.exclude_patterns = [re.compile(p) for p in (exclude_patterns or [])]
        self.visited: Set[str] = set()
        self.to_visit: list[tuple[str, int]] = [(base_url, 0)]  # (url, depth)

    def _normalize_url(self, url: str) -> Optional[str]:
        """Normalize and validate urls"""
        parsed = urlparse(url)

        if not self.follow_external and parsed.netloc != self.domain:
            return None

        if self.exclude_patterns and any(p.search(url) for p in self.exclude_patterns):
            return None

        if self.include_patterns and not any(
            p.search(url) for p in self.include_patterns
        ):
            return None
        return url.split("#")[0]

    def _extract_links(self, html: str, current_url: str) -> list[str]:
        """Extrai links de um HTML"""
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            normalized = self._normalize_url(href) if isinstance(href, str) else None

            if normalized and normalized not in self.visited:
                links.append(normalized)

        return links

    async def crawl(
        self,
        client: Optional[httpx.AsyncClient] = None,
        timeout: float = 15.0,
    ) -> list[str]:
        """Crawl recursively and exctracts urls"""
        created_client = False
        if client is None:
            client = httpx.AsyncClient(
                follow_redirects=True,
                timeout=timeout,
                headers={"User-Agent": DEFAULT_USER_AGENT},
            )
            created_client = True

        try:
            discovered_urls = []

            while self.to_visit and len(discovered_urls) < self.max_urls:
                url, depth = self.to_visit.pop(0)

                if url in self.visited or depth > self.max_depth:
                    continue

                self.visited.add(url)
                discovered_urls.append(url)

                try:
                    response = await client.get(url)
                    response.raise_for_status()

                    content_type = response.headers.get("content-type", "")
                    if "text/html" not in content_type:
                        continue

                    # find links
                    new_links = self._extract_links(response.text, url)

                    for link in new_links:
                        if len(discovered_urls) < self.max_urls:
                            self.to_visit.append((link, depth + 1))

                except Exception as e:
                    print(f"Error processing {url}: {e}")
                    continue

                with open("urls.txt", "w") as f:
                    f.write("\n".join(discovered_urls))
                    f.close()

            return discovered_urls

        finally:
            if created_client:
                await client.aclose()


async def scrape(
    base_url: str,
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
        crawler = URLCrawler(base_url)
        urls = await crawler.crawl(client)

        normalized_urls = [
            url if re.match(r"^https?://", url) else f"https://{url}" for url in urls
        ]

        results: list[ScrapeResult] = []

        for normalized_url in normalized_urls:
            try:
                response = await client.get(normalized_url)

                # content-tye
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    print(
                        f"Content type '{content_type}' de '{response.url}' não é HTML."
                    )
                    continue

                soup = BeautifulSoup(response.text, "html.parser")

                # remove tags
                for element in soup.find_all(BLOCK_TAGS_TO_REMOVE):
                    element.decompose()
                for element in soup.find_all(STRUCTURAL_TAGS_TO_PRUNE):
                    element.decompose()

                text = soup.get_text(separator=" ", strip=True)
                text = re.sub(r"\s+", " ", text).strip()

                title = (
                    soup.title.string.strip()
                    if soup.title and soup.title.string
                    else None
                )
                
                results.append(
                    ScrapeResult(
                        url=str(response.url),  
                        text=text,
                        title=title,
                        status_code=response.status_code,
                    )
                )
            except httpx.HTTPStatusError as exc:
                print(
                    f"HTTP Error searching {exc.response.url}: {exc.response.status_code}"
                )
                continue
            except (httpx.HTTPError, ValueError, Exception) as exc:
                print(f"Error procesing {normalized_url}: {exc}")
                continue

        return results

    finally:
        if created_client:
            await client.aclose()

from urllib.parse import urlparse
import httpx
import re
from enum import Enum
from dataclasses import dataclass
import io
import tempfile
from pathlib import Path

from bs4 import BeautifulSoup
from typing import Optional, Set
from pypdf import PdfReader

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


async def extract_pdf_text(pdf_bytes: bytes, url: str) -> Optional[str]:
    """Extract text from PDF bytes."""

    try:
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)

        if len(reader.pages) == 0:
            print(f"PDF from {url} has no pages")
            return None

        text_parts = []
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception as e:
                print(f"Error extracting text from page {page_num} in {url}: {e}")
                continue

        if not text_parts:
            print(f"No text could be extracted from PDF: {url}")
            return None

        # Join all pages and clean up whitespace
        full_text = "\n".join(text_parts)
        full_text = re.sub(r"\s+", " ", full_text).strip()

        return full_text

    except Exception as e:
        print(f"Error processing PDF from {url}: {e}")
        return None


async def scrape_pdf(
    url: str,
    client: httpx.AsyncClient,
    timeout: float = 15.0,
) -> Optional[ScrapeResult]:
    """Download and scrape a PDF document."""

    try:
        response = await client.get(url, timeout=timeout)
        response.raise_for_status()

        # Extract text from PDF
        text = await extract_pdf_text(response.content, url)

        if not text:
            return None

        # Try to get title from URL or PDF metadata
        title = None
        try:
            reader = PdfReader(io.BytesIO(response.content))
            metadata = reader.metadata
            if metadata and metadata.title:
                title = metadata.title
        except Exception:
            pass

        # Fallback to URL-based title
        if not title:
            title = Path(urlparse(url).path).stem or "PDF Document"

        return ScrapeResult(
            url=str(response.url),
            text=text,
            title=title,
            status_code=response.status_code,
        )

    except httpx.HTTPStatusError as exc:
        print(
            f"HTTP Error downloading PDF {exc.response.url}: {exc.response.status_code}"
        )
        return None
    except Exception as e:
        print(f"Error scraping PDF from {url}: {e}")
        return None


async def scrape_html(
    url: str,
    response: httpx.Response,
) -> Optional[ScrapeResult]:
    """Scrape HTML content from response."""

    try:
        soup = BeautifulSoup(response.text, "html.parser")

        # remove tags
        for element in soup.find_all(BLOCK_TAGS_TO_REMOVE):
            element.decompose()
        for element in soup.find_all(STRUCTURAL_TAGS_TO_PRUNE):
            element.decompose()

        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text).strip()

        title = soup.title.string.strip() if soup.title and soup.title.string else None

        return ScrapeResult(
            url=str(response.url),
            text=text,
            title=title,
            status_code=response.status_code,
        )
    except Exception as e:
        print(f"Error scraping HTML from {url}: {e}")
        return None


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

    def _extract_links(self, html: str) -> list[str]:
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
        """Crawl recursively and extracts urls (both HTML and PDF)"""
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

                    # Only extract links from HTML documents
                    if "text/html" in content_type:
                        # find links
                        new_links = self._extract_links(response.text)

                        for link in new_links:
                            if len(discovered_urls) < self.max_urls:
                                self.to_visit.append((link, depth + 1))
                    elif "application/pdf" in content_type:
                        # PDFs are collected but we don't crawl into them
                        pass
                    else:
                        # Skip unsupported content types
                        continue

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

                # Get content type
                content_type = response.headers.get("content-type", "")

                # Route to appropriate handler based on content type
                if "application/pdf" in content_type:
                    result = await scrape_pdf(normalized_url, client, timeout)
                    if result:
                        results.append(result)
                elif "text/html" in content_type:
                    result = await scrape_html(normalized_url, response)
                    if result:
                        results.append(result)
                else:
                    print(
                        f"Content type '{content_type}' of '{response.url}' is not supported. "
                        f"Supported types: text/html, application/pdf"
                    )
                    continue

            except httpx.HTTPStatusError as exc:
                print(
                    f"HTTP Error searching {exc.response.url}: {exc.response.status_code}"
                )
                continue
            except (httpx.HTTPError, ValueError, Exception) as exc:
                print(f"Error processing {normalized_url}: {exc}")
                continue

        return results

    finally:
        if created_client:
            await client.aclose()

import logging
import re

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
ALLOWED_CONTENT_TYPES = (
    "text/html",
    "application/xhtml+xml",
)
DEFAULT_MAX_CONTENT_LENGTH = 2_000_000  # ~2 MB
BLOCK_TAGS_TO_REMOVE = {"script", "style", "noscript", "template"}
STRUCTURAL_TAGS_TO_PRUNE = {"header", "footer", "nav", "aside"}


class ScraperError(Exception):
    """Base error for web scraping issues."""


class UnsupportedContentTypeError(ScraperError):
    """Raised when the response content type is not supported."""


class HTTPStatusError(ScraperError):
    """Raised when the server returns an unexpected status code."""


class ContentTooLargeError(ScraperError):
    """Raised when the response body exceeds the configured size limit."""


@dataclass(slots=True)
class ScrapeResult:
    url: str
    text: str
    title: Optional[str]
    status_code: int
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    language: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ScraperConfig:
    timeout: float = 15.0
    max_content_length: int = DEFAULT_MAX_CONTENT_LENGTH
    user_agent: str = DEFAULT_USER_AGENT
    allowed_content_types: Iterable[str] = ALLOWED_CONTENT_TYPES


class WebScraper:
    """Simple web scraper focused on extracting clean textual content."""

    def __init__(self, config: Optional[ScraperConfig] = None) -> None:
        self.config = config or ScraperConfig()

    async def scrape(
        self,
        url: str,
        *,
        client: Optional[httpx.AsyncClient] = None,
    ) -> ScrapeResult:
        """Fetch and clean textual content from an URL."""
        if not url:
            raise ValueError("url must be a non-empty string")

        normalized_url = self._normalize_url(url)
        created_client = False
        client_to_use: httpx.AsyncClient

        if client is None:
            client_to_use = httpx.AsyncClient(
                follow_redirects=True,
                timeout=self.config.timeout,
                headers={"User-Agent": self.config.user_agent},
            )
            created_client = True
        else:
            client_to_use = client

        try:
            response = await client_to_use.get(normalized_url)
        except httpx.TimeoutException as exc:  # pragma: no cover - passthrough
            raise ScraperError(f"Timeout fetching URL '{normalized_url}'") from exc
        except httpx.HTTPError as exc:  # pragma: no cover - passthrough
            raise ScraperError(f"HTTP error fetching URL '{normalized_url}'") from exc
        finally:
            if created_client:
                await client_to_use.aclose()

        self._ensure_success_status(response)
        self._ensure_supported_content_type(response)
        self._enforce_size_limit(response)

        text, title, metadata = self._extract_textual_content(response)

        return ScrapeResult(
            url=str(response.url),
            text=text,
            title=title,
            status_code=response.status_code,
            language=metadata.get("language"),
            metadata=metadata,
        )

    @staticmethod
    def _normalize_url(url: str) -> str:
        parsed = urlparse(url)
        if not parsed.scheme:
            return f"https://{url}"
        return url

    def _ensure_success_status(self, response: httpx.Response) -> None:
        if response.status_code >= 400:
            raise HTTPStatusError(
                f"Fetching '{response.url}' failed with status "
                f"{response.status_code}"
            )

    def _ensure_supported_content_type(self, response: httpx.Response) -> None:
        content_type = response.headers.get("content-type", "")
        if not content_type:
            raise UnsupportedContentTypeError(
                f"Response from '{response.url}' has no content-type header"
            )

        if not any(
            allowed in content_type for allowed in self.config.allowed_content_types
        ):
            raise UnsupportedContentTypeError(
                f"Content type '{content_type}' from '{response.url}' is unsupported"
            )

    def _enforce_size_limit(self, response: httpx.Response) -> None:
        if len(response.content) > self.config.max_content_length:
            raise ContentTooLargeError(
                f"Response from '{response.url}' exceeds size limit"
            )

    def _extract_textual_content(
        self, response: httpx.Response
    ) -> tuple[str, Optional[str], Dict[str, Any]]:
        soup = BeautifulSoup(response.text, "html.parser")

        for element in soup.find_all(BLOCK_TAGS_TO_REMOVE):
            element.decompose()

        for element in soup.find_all(STRUCTURAL_TAGS_TO_PRUNE):
            element.decompose()

        text = soup.get_text(separator="\n")
        text = self._clean_text(text)

        if not text:
            logger.warning("No textual content extracted from '%s'", response.url)

        title = None
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        metadata: Dict[str, Any] = {
            "final_url": str(response.url),
            "status_code": response.status_code,
            "language": self._detect_language(soup),
        }

        canonical = soup.find("link", rel=lambda value: value and "canonical" in value)
        if canonical and canonical.get("href"):
            metadata["canonical_url"] = urljoin(str(response.url), canonical["href"])

        description = soup.find("meta", attrs={"name": "description"})
        if description and description.get("content"):
            metadata["description"] = description["content"].strip()

        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            metadata["og:title"] = og_title["content"].strip()

        og_description = soup.find("meta", property="og:description")
        if og_description and og_description.get("content"):
            metadata["og:description"] = og_description["content"].strip()

        return text, title, metadata

    @staticmethod
    def _clean_text(raw_text: str) -> str:
        lines = [line.strip() for line in raw_text.splitlines()]
        non_empty_lines = [line for line in lines if line]
        if not non_empty_lines:
            return ""
        collapsed = "\n".join(non_empty_lines)
        return re.sub(r"\s+", " ", collapsed).strip()

    @staticmethod
    def _detect_language(soup: BeautifulSoup) -> Optional[str]:
        html_tag = soup.find("html")
        lang_attr = html_tag.get("lang") if html_tag else None
        if isinstance(lang_attr, str) and lang_attr.strip():
            return lang_attr.strip().lower()
        return None


async def scrape_url(
    url: str, *, client: Optional[httpx.AsyncClient] = None
) -> ScrapeResult:
    """Convenience wrapper over :class:`WebScraper`."""
    scraper = WebScraper()
    return await scraper.scrape(url, client=client)

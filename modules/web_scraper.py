
import requests
import ipaddress
import socket

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


# ------------------------------------------
# URL VALIDATION
# ------------------------------------------

def validate_url(url):
    """
    Validate URLs and reject private or local network addresses.
    """

    try:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        if not parsed.hostname or parsed.username or parsed.password:
            return False

        # Resolve the hostname before making a request
        addresses = socket.getaddrinfo(
            parsed.hostname,
            None,
            type=socket.SOCK_STREAM
        )

        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])

            if not ip.is_global:
                return False

        return True

    except (socket.gaierror, ValueError, OSError):
        return False


# ------------------------------------------
# WEBPAGE CONTENT EXTRACTION
# ------------------------------------------

def extract_page_text(html):
    """
    Extract readable text from webpage HTML.
    """

    soup = BeautifulSoup(html, "html.parser")

    # Remove unnecessary elements
    for element in soup([
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "aside",
        "form",
        "noscript",
        "iframe"
    ]):
        element.decompose()

    # Try common article containers
    article = (
        soup.find("article")
        or soup.find("main")
        or soup.find(attrs={"role": "main"})
    )

    # Try common content containers if necessary
    if not article:
        selectors = [
            "div[itemprop='articleBody']",
            ".article-content",
            ".article-body",
            ".post-content",
            ".entry-content",
            "#article-body",
            "#main-content"
        ]

        for selector in selectors:
            article = soup.select_one(selector)

            if article:
                break

    # Last fallback
    if not article:
        article = soup.body

    if not article:
        return None

    text = article.get_text(
        separator=" ",
        strip=True
    )

    # Normalize excessive whitespace
    text = " ".join(text.split())

    if len(text) < 200:
        return None

    return text[:15000]


# ------------------------------------------
# WEB SCRAPER
# ------------------------------------------

def scrape_website(url):
    """
    Download a webpage and extract readable text.

    Redirect destinations are validated before following them.
    """

    if not validate_url(url):
        print(f"Invalid or unsafe URL: {url}")
        return None

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "close"
    }

    try:
        current_url = url

        # Follow a limited number of validated redirects
        for attempt in range(6):

            response = requests.get(
                current_url,
                headers=headers,
                timeout=(10, 20),
                allow_redirects=False
            )

            # Handle redirects manually
            if response.is_redirect:
                location = response.headers.get("Location")
                response.close()

                if not location:
                    return None

                next_url = urljoin(current_url, location)

                if not validate_url(next_url):
                    print("Redirect blocked: unsafe destination")
                    return None

                current_url = next_url
                continue

            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type", ""
            ).lower()

            if "text/html" not in content_type:
                print(f"Unsupported content type: {content_type}")
                return None

            extracted_text = extract_page_text(response.text)

            if extracted_text:
                return extracted_text

            print(f"No readable content found: {current_url}")
            return None

        print("Too many webpage redirects.")
        return None

    except requests.exceptions.HTTPError as error:
        print(f"HTTP error while scraping {url}: {error}")
        return None

    except requests.exceptions.Timeout:
        print(f"Website request timed out: {url}")
        return None

    except requests.exceptions.RequestException as error:
        print(f"Scraping failed for {url}: {error}")
        return None

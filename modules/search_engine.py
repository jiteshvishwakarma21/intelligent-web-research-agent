from ddgs import DDGS
import time


def clean_url(url):
    """Reject sponsored redirect URLs and invalid links."""

    if not url.startswith(("http://", "https://")):
        return ""

    # Ignore Bing sponsored advertisement redirects
    if "bing.com/aclick" in url.lower():
        return ""

    return url


def search_web(topic, max_results=5):

    search_results = []
    seen_urls = set()

    queries = [
        topic,
        f"{topic} research articles",
        f"{topic} studies and findings"
    ]

    last_error = None

    for query in queries:

        try:
            with DDGS(timeout=20) as search_engine:

                results = search_engine.text(
                    query,
                    max_results=max_results,
                    backend="auto"
                )

                for result in results:

                    url = clean_url(result.get("href", ""))

                    if not url or url in seen_urls:
                        continue

                    seen_urls.add(url)

                    search_results.append({
                        "title": result.get("title", ""),
                        "url": url,
                        "snippet": result.get("body", "")
                    })

                    if len(search_results) >= max_results:
                        return search_results

            if search_results:
                return search_results

        except Exception as error:
            last_error = error
            print(f"Search attempt failed: {error}")

        time.sleep(2)

    if not search_results:
        raise RuntimeError(
            f"Web search unavailable: {last_error or 'No results found'}"
        )

    return search_results
import requests


def search_gutenberg(query: str, limit: int = 5) -> list[dict]:
    """Search Project Gutenberg for public domain ebooks."""
    url = "https://gutendex.com/books/"
    params = {"search": query, "languages": "en"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return []

        data = resp.json()
        results = []

        for book in data.get("results", [])[:limit]:
            # Get EPUB download link
            formats = book.get("formats", {})
            epub_url = formats.get("application/epub+zip")
            pdf_url = formats.get("application/pdf")
            cover_url = formats.get("image/jpeg")

            # Authors
            authors = [a.get("name", "Unknown") for a in book.get("authors", [])]

            results.append({
                "title": book.get("title", "Unknown"),
                "author": ", ".join(authors) if authors else "Unknown",
                "cover_url": cover_url,
                "epub_url": epub_url,
                "pdf_url": pdf_url,
                "external_url": f"https://www.gutenberg.org/ebooks/{book.get('id')}",
                "source_name": "Project Gutenberg",
            })

        return results
    except Exception:
        return []

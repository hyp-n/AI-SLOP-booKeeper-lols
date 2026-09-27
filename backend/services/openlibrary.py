import requests


def lookup_isbn(isbn: str) -> dict | None:
    """Look up a book's metadata from OpenLibrary by ISBN."""
    url = f"https://openlibrary.org/isbn/{isbn}.json"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()

        # Fetch authors
        authors = []
        for author_ref in data.get("authors", []):
            author_key = author_ref.get("key", "")
            try:
                author_resp = requests.get(f"https://openlibrary.org{author_key}.json", timeout=5)
                if author_resp.status_code == 200:
                    authors.append(author_resp.json().get("name", "Unknown"))
            except Exception:
                pass

        # Fetch cover
        cover_url = None
        cover_id = data.get("covers", [None])[0]
        if cover_id:
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

        # Extract page count
        page_count = data.get("number_of_pages")

        # Extract publisher
        publishers = data.get("publishers", [])
        publisher = publishers[0] if publishers else None

        # Extract published date
        publish_date = data.get("publish_date")

        return {
            "isbn": isbn,
            "title": data.get("title", "Unknown Title"),
            "author": ", ".join(authors) if authors else "Unknown Author",
            "cover_url": cover_url,
            "description": data.get("description", {}).get("value", "") if isinstance(data.get("description"), dict) else data.get("description", ""),
            "publisher": publisher,
            "published_date": publish_date,
            "page_count": page_count,
            "language": data.get("languages", [{}])[0].get("key", "").replace("/languages/", "") if data.get("languages") else None,
        }
    except Exception:
        return None


def search_books(query: str, limit: int = 10) -> list[dict]:
    """Search OpenLibrary by title/author."""
    url = "https://openlibrary.org/search.json"
    params = {"q": query, "limit": limit}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return []
        data = resp.json()
        results = []
        for doc in data.get("docs", []):
            cover_id = doc.get("cover_i")
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None
            results.append({
                "isbn": doc.get("isbn", [None])[0] if doc.get("isbn") else None,
                "title": doc.get("title", "Unknown"),
                "author": ", ".join(doc.get("author_name", ["Unknown"])),
                "cover_url": cover_url,
                "publisher": ", ".join(doc.get("publisher", [])),
                "published_date": doc.get("first_publish_year"),
                "page_count": doc.get("number_of_median_pages"),
                "key": doc.get("key"),
            })
        return results
    except Exception:
        return []

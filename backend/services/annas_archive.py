import requests
from bs4 import BeautifulSoup


def search_annas_archive(query: str, limit: int = 5) -> list[dict]:
    """Search Anna's Archive for ebook download links."""
    url = "https://annas-archive.org/search"
    params = {"q": query, "format": "epub"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        results = []

        # Parse search results
        for item in soup.select("div.iframe-list > div")[:limit]:
            title_tag = item.select_one("h3 a")
            if not title_tag:
                continue

            title = title_tag.get_text(still=True) if title_tag else "Unknown"
            link = title_tag.get("href", "") if title_tag else ""

            # Get author
            author_tag = item.select_one("div.text-gray-500 a")
            author = author_tag.get_text(strip=True) if author_tag else "Unknown"

            # Get format/size info
            format_tags = item.select("div.text-gray-500 span")
            format_info = " ".join(t.get_text(strip=True) for t in format_tags)

            # Get cover
            cover_tag = item.select_one("img")
            cover_url = cover_tag.get("src", "") if cover_tag else None

            # Build full URL
            full_url = f"https://annas-archive.org{link}" if link.startswith("/") else link

            results.append({
                "title": title,
                "author": author,
                "cover_url": cover_url,
                "format_info": format_info,
                "external_url": full_url,
                "source_name": "Anna's Archive",
            })

        return results
    except Exception:
        return []

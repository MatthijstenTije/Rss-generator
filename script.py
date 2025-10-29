from flask import Flask, Response, request
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__)

@app.route("/rss")
def rss_feed():
    # Get URL from query parameter
    url = request.args.get("url", "https://www.vpro.nl/frontlinie/artikelen")
    if not url.startswith("http"):
        return Response("Please provide a full URL (including https://)", status=400)

    try:
        html = requests.get(url, timeout=10).text
    except Exception as e:
        return Response(f"Error fetching {url}: {e}", status=500)

    soup = BeautifulSoup(html, "html.parser")

    # Find links to articles (common VPRO teaser structure)
    links = soup.select("a.teaser__link, a.c-teaser__link, a.c-article-teaser__link")

    if not links:
        return Response(f"No articles found for {url}", mimetype="text/plain")

    items = ""
    for article in links[:10]:
        href = article.get("href")
        if not href:
            continue
        if not href.startswith("http"):
            href = f"https://{urlparse(url).netloc}{href}"
        title = article.get_text(strip=True)
        if not title:
            continue

        items += f"""
        <item>
          <title>{title}</title>
          <link>{href}</link>
          <guid>{href}</guid>
          <pubDate>{datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
        </item>
        """

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <title>RSS Generator Feed</title>
        <link>{url}</link>
        <description>Automatisch gegenereerde RSS-feed voor {url}</description>
        <language>nl-nl</language>
        {items}
      </channel>
    </rss>"""

    return Response(rss, mimetype="application/rss+xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


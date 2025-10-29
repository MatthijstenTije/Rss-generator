from flask import Flask, Response, request
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse, urljoin

app = Flask(__name__)

@app.route("/rss")
def rss_feed():
    # Get the URL parameter (default: VPRO Frontlinie)
    target_url = request.args.get("url", "https://www.vpro.nl/frontlinie/artikelen").strip()
    print(f"=== Fetching articles from: {target_url} ===")

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(target_url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        err = f"Error fetching {target_url}: {e}"
        print(err)
        return Response(
            f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Error</title><description>{err}</description></channel></rss>',
            mimetype="application/rss+xml"
        )

    soup = BeautifulSoup(res.text, "html.parser")

    # Try multiple selectors (in case site changes its HTML structure)
    possible_selectors = [
        "a.c-teaser__link",
        "a.teaser__link",
        "a.c-article-teaser__link",
        "a.o-teaser__link",
        "a",  # fallback - get all links if others fail
    ]

    found_links = []
    for selector in possible_selectors:
        found_links = soup.select(selector)
        if found_links:
            print(f"✅ Using selector: {selector} -> found {len(found_links)} links")
            break

    if not found_links:
        print("⚠️ No links found using any selector.")
    else:
        print("=== Found article hrefs ===")
        for a in found_links[:50]:
            href = a.get("href")
            if href:
                print(href)

    # Build RSS items
    items = ""
    count = 0
    for a in found_links[:20]:
        href = a.get("href")
        if not href:
            continue
        link = urljoin(target_url, href)
        title = a.get_text(strip=True) or link
        count += 1
        items += f"""
        <item>
            <title>{title}</title>
            <link>{link}</link>
            <guid>{link}</guid>
            <pubDate>{datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
        </item>"""

    if not items:
        items = "<item><title>No articles found</title><description>Check Render logs for detected URLs.</description></item>"

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <title>VPRO / Custom RSS Feed</title>
        <link>{target_url}</link>
        <description>Generated RSS feed for {target_url}</description>
        <language>nl-nl</language>
        {items}
      </channel>
    </rss>"""

    return Response(rss_xml, mimetype="application/rss+xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


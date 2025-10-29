from flask import Flask, Response, request
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__)

@app.route("/rss")
def rss_feed():
    # Get URL from query string
    target_url = request.args.get("url", "").strip()
    if not target_url:
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Error</title><description>Missing ?url= parameter</description></channel></rss>',
            mimetype="application/rss+xml",
        )

    # Fetch the page
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(target_url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        return Response(
            f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Error fetching URL</title><description>{str(e)}</description></channel></rss>',
            mimetype="application/rss+xml",
        )

    soup = BeautifulSoup(res.text, "html.parser")

    # Try to find article links
    selectors = ["a.c-teaser__link", "a.teaser__link", "a.c-article-teaser__link"]
    links = []
    for sel in selectors:
        found = soup.select(sel)
        if found:
            links = found
            break

    items = ""
    for a in links[:10]:
        href = a.get("href")
        if not href:
            continue
        if not href.startswith("http"):
            href = f"https://{urlparse(target_url).netloc}{href}"
        title = a.get_text(strip=True) or href
        pub_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
        items += f"""
        <item>
            <title>{title}</title>
            <link>{href}</link>
            <guid>{href}</guid>
            <pubDate>{pub_date}</pubDate>
        </item>"""

    if not items:
        items = "<item><title>No articles found</title><link>{target_url}</link></item>"

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <title>Generated RSS Feed</title>
        <link>{target_url}</link>
        <description>Automatic feed for {target_url}</description>
        <language>nl-nl</language>
        {items}
      </channel>
    </rss>"""

    return Response(rss_xml, mimetype="application/rss+xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


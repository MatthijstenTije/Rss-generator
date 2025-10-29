from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

urls = "https://www.vpro.nl/frontlinie/artikelen"
@app.route("/rss")
def rss_feed():
    url = urls
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    items = ""
    for article in soup.select("a.c-teaser__link")[:10]:
        link = "https://www.vpro.nl" + article.get("href")
        title = article.get_text(strip=True)
        items += f"""
        <item>
          <title>{title}</title>
          <link>{link}</link>
          <guid>{link}</guid>
          <pubDate>{datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
        </item>
        """

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <title>VPRO Frontlinie Artikelen</title>
        <link>{url}</link>
        <description>Automatisch gegenereerde RSS-feed voor Frontlinie</description>
        <language>nl-nl</language>
        {items}
      </channel>
    </rss>"""
    return Response(rss, mimetype="application/rss+xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

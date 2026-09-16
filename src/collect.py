import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

UA = "anti-japan-influence-monitor/1.0"


def google_news_rss(query):
    q = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja"


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def text(node, tag):
    x = node.find(tag)
    return (x.text or "").strip() if x is not None else ""


def parse_date(value):
    if not value:
        return datetime.now(timezone.utc).isoformat()
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


def parse_rss(data, category, query):
    root = ET.fromstring(data)
    items = []
    for item in root.findall(".//item"):
        title = text(item, "title")
        link = text(item, "link")
        desc = text(item, "description")
        pub = text(item, "pubDate")
        source = text(item, "source")
        if title and link:
            items.append({
                "category": category,
                "query": query,
                "title": re.sub(r"\\s+", " ", title),
                "url": link,
                "summary": re.sub(r"<[^>]+>", " ", desc),
                "source": source,
                "published_at": parse_date(pub)
            })
    return items


def collect(config_dir="config"):
    all_items = []
    for name in ("china.json", "russia.json", "north-korea.json", "third-country.json"):
        with open(f"{config_dir}/{name}", encoding="utf-8") as f:
            cfg = json.load(f)
        for query in cfg["queries"]:
            try:
                data = fetch(google_news_rss(query))
                all_items.extend(parse_rss(data, cfg["name"], query))
            except Exception as e:
                print(f"WARN collection failed: {query}: {e}")
    return all_items

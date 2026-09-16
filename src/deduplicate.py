import hashlib
import json
import os
import re
from urllib.parse import urlsplit, urlunsplit

STATE_PATH = "data/state.json"


def norm_url(url):
    p = urlsplit(url)
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), "", ""))


def norm_title(title):
    return re.sub(r"[^0-9a-zA-Zぁ-んァ-ン一-龥]+", "", title).lower()


def item_id(item):
    key = norm_url(item["url"]) + "|" + norm_title(item["title"])
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def load_state():
    if not os.path.exists(STATE_PATH):
        return {"seen": {}}
    with open(STATE_PATH, encoding="utf-8") as f:
        return json.load(f)


def filter_new(items, state):
    out = []
    local = set()
    for item in items:
        iid = item_id(item)
        if iid in state.get("seen", {}) or iid in local:
            continue
        item["id"] = iid
        out.append(item)
        local.add(iid)
    return out


def mark_seen(state, items, now):
    seen = state.setdefault("seen", {})
    for item in items:
        seen[item["id"]] = now
    # Keep state bounded.
    if len(seen) > 10000:
        for k in list(seen)[:-10000]:
            del seen[k]

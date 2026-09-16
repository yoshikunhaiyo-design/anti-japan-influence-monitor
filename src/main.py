import json
import os
from datetime import datetime, timezone
from collect import collect
from deduplicate import load_state, filter_new, mark_seen, STATE_PATH
from analyze import call_openai, fallback

REPORT_DIR = "reports"


def main():
    now = datetime.now(timezone.utc).isoformat()
    os.makedirs("data", exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)
    state = load_state()
    items = collect()
    new_items = filter_new(items, state)
    analysis = fallback(new_items, "No analysis attempted")
    if new_items:
        try:
            analysis = call_openai(new_items)
        except Exception as e:
            analysis = fallback(new_items, e)
    mark_seen(state, new_items, now)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    report = {
        "generated_at": now,
        "new_candidates": len(new_items),
        "analysis": analysis,
        "collected_items": new_items
    }
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(f"{REPORT_DIR}/{stamp}.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps({"new_candidates": len(new_items), "analysis_status": analysis.get("status", "ok")}, ensure_ascii=False))


if __name__ == "__main__":
    main()

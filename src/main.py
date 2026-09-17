import json
import os
from datetime import datetime, timezone
from collect import collect
from deduplicate import load_state, filter_new, mark_seen, STATE_PATH

REPORT_DIR = "reports"


def main():
    now = datetime.now(timezone.utc).isoformat()
    os.makedirs("data", exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)
    state = load_state()
    items = collect()
    new_items = filter_new(items, state)
    mark_seen(state, new_items, now)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    report = {
        "generated_at": now,
        "new_items": len(new_items),
        "items": new_items
    }
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(f"{REPORT_DIR}/{stamp}.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps({"new_items": len(new_items)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

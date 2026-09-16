import json
import os
import urllib.request

API_URL = "https://api.openai.com/v1/responses"
MODEL = "gpt-5.6-luna"

SYSTEM = """あなたは情報工作・偽情報を監視するOSINT分析官です。候補情報を読み、事実と主張と分析を明確に区別してください。根拠が候補情報にない内容を補完・創作しないでください。同一事案の転載は一件にまとめてください。中国→日本、ロシア→日本、北朝鮮→日本、第三国向け対日離間工作の4分類を維持してください。重要度は1-5で、影響範囲、信頼できる一次情報の有無、日本への関連性、新規性を基準に判断してください。第三国向け対日離間工作は、意図が確認できる事実と、離間効果があり得るという分析を分けてください。JSONだけを返してください。"""


def call_openai(items):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    prompt = json.dumps(items, ensure_ascii=False)
    body = {
        "model": MODEL,
        "input": SYSTEM + "\n\n候補情報:\n" + prompt,
        "text": {"format": {"type": "json_object"}}
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        result = json.loads(r.read())
    return extract_json(result)


def extract_json(result):
    if "output_text" in result:
        return json.loads(result["output_text"])
    chunks = []
    for out in result.get("output", []):
        for c in out.get("content", []):
            if isinstance(c, dict) and c.get("text"):
                chunks.append(c["text"])
    return json.loads("".join(chunks))


def fallback(items, error):
    return {"items": [], "status": "analysis_unavailable", "error": str(error), "candidate_count": len(items)}

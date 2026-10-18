"""Split ordered WebKit rules without changing ignore-previous-rules scope."""
import hashlib
import json
import sys
from pathlib import Path

LIMIT = 148000

def split_rules(rules, limit=LIMIT):
    if not isinstance(rules, list) or not rules:
        raise ValueError("Expected nonempty rule array")
    for rule in rules:
        if not isinstance(rule.get("trigger", {}).get("url-filter"), str):
            raise ValueError("Invalid trigger")
        if rule.get("action", {}).get("type") not in {"block", "block-cookies", "css-display-none", "make-https", "ignore-previous-rules"}:
            raise ValueError("Unsupported action: review splitting semantics before publishing")
    exceptions = sum(r["action"]["type"] == "ignore-previous-rules" for r in rules)
    capacity = limit - exceptions
    if capacity <= 0:
        raise ValueError("Exceptions alone exceed safe capacity")
    ordinary = [i for i, r in enumerate(rules) if r["action"]["type"] != "ignore-previous-rules"]
    if not ordinary:
        return [rules]
    chunks = []
    # Every action occurs once. Every reset occurs in every list at its original
    # relative position, so it cancels exactly the same preceding actions.
    for offset in range(0, len(ordinary), capacity):
        selected = set(ordinary[offset:offset + capacity])
        chunks.append([r for i, r in enumerate(rules) if i in selected or r["action"]["type"] == "ignore-previous-rules"])
    assert all(0 < len(c) <= limit for c in chunks)
    assert sum(len(c) - exceptions for c in chunks) == len(ordinary)
    return chunks

def publish(source, destination):
    rules = json.loads(Path(source).read_text())
    chunks = split_rules(rules)
    output = Path(destination)
    (output / "chunks").mkdir(parents=True, exist_ok=True)
    files = []
    for chunk in chunks:
        data = json.dumps(chunk, ensure_ascii=False, separators=(",", ":")).encode()
        if len(data) > 24 * 1024 * 1024:
            raise ValueError("Chunk exceeds Pages file size budget")
        digest = hashlib.sha256(data).hexdigest()
        path = "chunks/" + digest + ".json"
        (output / path).write_bytes(data)
        files.append({"path": path, "sha256": digest, "count": len(chunk)})
    manifest = {"schemaVersion": 1, "maxRulesPerFile": LIMIT, "sourceRuleCount": len(rules),
                "totalRuleCount": sum(f["count"] for f in files), "files": files}
    (output / "manifest.json").write_text(json.dumps(manifest, separators=(",", ":")))
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    publish(sys.argv[1], sys.argv[2])

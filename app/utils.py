import json, hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

def sha256_of_dict(d: Dict[str, Any]) -> str:
    payload = json.dumps(d, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def write_event(log_dir: Path, event: Dict[str, Any]) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    event["ts_iso"] = datetime.utcnow().isoformat() + "Z"
    fp = log_dir / "events.jsonl"
    with fp.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

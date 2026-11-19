#!/usr/bin/env python3
"""Turn Twitch API scout metadata into a rights-unverified editorial queue.
Never download clips, infer permissions, or publish video.
"""
import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "clipping-bot" / "out" / "candidates.json"
TARGET = ROOT / "web" / "clips.json"
# Exclude potentially adult/spoiler/abusive titles from public discovery index,
# not a guarantee that the linked media is suitable for redistribution.
BLOCKED = re.compile(
    r"strip club|private dance|horny|nsfw|nude|naked|sex|nips|boobs|tits|"
    r"banned|spoiler|slur|racial|suicide|kill yourself|"
    r"стрип|сисюл", re.I
)

def main():
    scout=json.loads(SOURCE.read_text(encoding="utf-8"))
    candidates=[]
    seen=set()
    for clip in scout.get("clips", []):
        url=clip.get("url", "")
        parts=urlparse(url)
        if parts.scheme != "https" or parts.hostname not in ("twitch.tv","www.twitch.tv") or "/clip/" not in parts.path:
            continue
        title=re.sub(r"\s+"," ",clip.get("title","")).strip()[:140]
        if not title or BLOCKED.search(title) or url in seen:
            continue
        seen.add(url)
        creator=re.sub(r"[^\w.\-]","",clip.get("creator",""))[:48]
        candidates.append({
            "url":url,
            "title":title,
            "creator":creator,
            "views":max(0,int(clip.get("views",0))),
            "created_at":clip.get("created_at",""),
            "permission":"not_verified",
        })
    candidates.sort(key=lambda row:row["views"], reverse=True)
    data={
        "updated_at":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z"),
        "description":"Twitch API discovery metadata; view counts at detection only. No clip has been cleared for redistribution.",
        "game":scout.get("game","Grand Theft Auto VI"),
        "clips":candidates[:20],
    }
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("QUEUE_OK",len(data["clips"]),"clips, all permissions unverified")

if __name__=="__main__":main()

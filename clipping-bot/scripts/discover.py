"""Twitch clip scout: finds candidates only; does not download or publish videos."""
import base64
import datetime as dt
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"out"/"candidates.json"

def request_json(url,headers=None,data=None):
    req=Request(url,headers=headers or {},data=data)
    with urlopen(req,timeout=30) as resp:
        return json.loads(resp.read().decode("utf8"))

def main():
    cid=os.getenv("TWITCH_CLIENT_ID")
    secret=os.getenv("TWITCH_CLIENT_SECRET")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    if not cid or not secret:
        OUT.write_text(json.dumps({"status":"missing_credentials","clips":[]},indent=2))
        print("Missing Twitch secrets: no scan performed")
        return
    token=request_json("https://id.twitch.tv/oauth2/token?"+urlencode({"client_id":cid,"client_secret":secret,"grant_type":"client_credentials"}),data=b"")["access_token"]
    headers={"Client-ID":cid,"Authorization":"Bearer "+token}
    games=request_json("https://api.twitch.tv/helix/games?"+urlencode({"name":"Grand Theft Auto VI"}),headers=headers)["data"]
    if not games:
        OUT.write_text(json.dumps({"status":"game_not_found","clips":[]},indent=2))
        return
    game_id=games[0]["id"]
    since=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(days=2)).isoformat().replace("+00:00","Z")
    clips=request_json("https://api.twitch.tv/helix/clips?"+urlencode({"game_id":game_id,"started_at":since,"first":100}),headers=headers)["data"]
    clips=sorted(clips,key=lambda c:c.get("view_count",0),reverse=True)
    picks=[{"url":c["url"],"title":c.get("title"),"views":c.get("view_count"),"creator":c.get("broadcaster_name"),"created_at":c.get("created_at"),"rights":"to_verify"} for c in clips[:25]]
    OUT.write_text(json.dumps({"game":games[0]["name"],"count":len(picks),"clips":picks},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(f"Selected {len(picks)} potential clips; rights must be verified.")

if __name__=="__main__":
    main()

"""Veille de sources Rockstar officielles. Ne génère ni ne publie de contenu."""
import datetime as dt
import html.parser
import json
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

BASE = "https://www.rockstargames.com"
PAGES = [BASE + "/VI", BASE + "/newswire/"]
ROOT = Path(__file__).resolve().parents[1]
SEEN = ROOT / "data" / "official_seen.json"
REPORT = ROOT / "reports" / "official-watch.md"

class Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = None
        self.text = []
        self.found = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.text = []
    def handle_data(self, data):
        if self.href is not None:
            self.text.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self.href:
            url = urljoin(BASE, self.href).split("?")[0]
            host = urlparse(url).hostname
            if host in ("rockstargames.com", "www.rockstargames.com") and "/newswire/article/" in url:
                self.found.append((url," ".join(" ".join(self.text).split())[:150]))
            self.href = None
            self.text = []

def parse(html):
    p = Links(); p.feed(html)
    return dict(p.found)

def main():
    results = {}
    errors = []
    for url in PAGES:
        try:
            req = Request(url, headers={"User-Agent":"Mozilla/5.0 GuideLeonida/0.1"})
            with urlopen(req, timeout=20) as response:
                html = response.read(3_000_000).decode("utf-8", errors="replace")
            results.update(parse(html))
        except Exception as ex:
            errors.append(f"{url}: {ex}")
    if not results:
        raise RuntimeError("Impossible de lire les liens officiels ; aucune nouvelle publication. " + "; ".join(errors))
    old = set(json.loads(SEEN.read_text(encoding="utf8"))) if SEEN.exists() else set()
    fresh = {u:t for u,t in results.items() if u not in old}
    date = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    text = [f"# Veille Rockstar — {date}", "", "**À vérifier manuellement. Aucun article publié automatiquement.**", ""]
    text.extend(f"- [{(title or 'Annonce Rockstar').replace('[','').replace(']','')}]({u})" for u,title in list(fresh.items())[:30])
    if errors: text += ["", "Sources partiellement indisponibles :", *["- "+e for e in errors]]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(text)+"\n",encoding="utf8")
    SEEN.parent.mkdir(parents=True, exist_ok=True)
    SEEN.write_text(json.dumps(sorted(old|set(results)),indent=2)+"\n",encoding="utf8")
    print(f"Sources lues: {len(results)} ; nouveaux liens: {len(fresh)}")
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"],"a",encoding="utf8") as fp:
            fp.write(f"new_count={len(fresh)}\n")

if __name__ == "__main__":
    main()

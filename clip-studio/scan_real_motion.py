#!/usr/bin/env python3
"""Select actual moving footage hosted on the official Rockstar GTA VI domain.
Creates CONTACT SHEET ONLY for private editorial review. No public redistribution.
"""
import json
import os
import subprocess
import urllib.request
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont

NAMES=[
"037107e95f8339418f9077f13cec32d8",
"097f9159ec943910940a3552bcbe5536",
"0f1e9840c0d973a860f170a2338b4a1d",
"2aed05f51aa99bfdbc60d6325dc70def",
"50f7777f7d153744db9feb59272ef0ea",
"759bb3a9c5ca56b11986415d22a81fca",
"807047056237fe6f972ba4af785df314",
"8899d1666c9806eef97e71031194cbea",
"ad02de555c9a641780ea684e352327c4",
"bda2b32c14424a4bf8c5aaa2f9ef41e5",
"ec85c9c2e667647dec6672b486165eba",
"f39029ce36a598ac32578c34b15bc2d2",
]
BASE="https://www.rockstargames.com/VI/_next/static/media/1080.{}.mp4"
OUT=Path("drafts/scout");OUT.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
sheet=Image.new("RGB",(1080,4*210),(11,10,22));d=ImageDraw.Draw(sheet)
entries=[]
for i,name in enumerate(NAMES):
    url=BASE.format(name)
    source=OUT/f"{i:02}.mp4"
    data={"index":i,"url":url,"valid":False}
    try:
        # Small official loop videos, cap at 40 MB each
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=25) as res, source.open("wb") as f:
            total=0
            while True:
                chunk=res.read(512*1024)
                if not chunk:break
                total+=len(chunk)
                if total>40_000_000: raise RuntimeError("source too large")
                f.write(chunk)
        p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of",
                          "default=noprint_wrappers=1:nokey=1",str(source)],capture_output=True,text=True,check=True)
        seconds=float(p.stdout.strip())
        if seconds<1:raise RuntimeError("too short")
        png=OUT/f"frame_{i:02}.jpg"
        subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(min(seconds*.45,3)),
                        "-i",str(source),"-frames:v","1",str(png)],check=True)
        img=Image.open(png).convert("RGB")
        thumb=ImageOps.fit(img,(344,176))
        x=8+(i%3)*357; y=6+(i//3)*210
        sheet.paste(thumb,(x,y))
        d.text((x+4,y+181),f"{i:02}  {seconds:.1f}s  {total/1e6:.1f}MB",font=font,fill=(240,228,244))
        data.update({"valid":True,"duration_seconds":seconds,"size_bytes":total})
    except Exception as exc:
        print("FAILED",i,str(exc)[:100],flush=True)
        data["error"]=str(exc)[:120]
    entries.append(data)
(OUT/"sheet.jpg").write_bytes(b"")
sheet.save(OUT/"sheet.jpg",quality=88)
(OUT/"index.json").write_text(json.dumps(entries,indent=2)+"\n",encoding="utf8")
print("VALID",sum(x["valid"] for x in entries),flush=True)

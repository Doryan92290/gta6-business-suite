#!/usr/bin/env python3
"""Build a review-only vertical video from downloaded official moving Rockstar clips.
NOT licensed for monetized campaign or publication. Nothing is posted.
"""
import io
import json
import re
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

URL="https://media-rockstargames-com.akamaized.net/VI/downloads/videos/GTAVI_Videos.zip"
WORK=Path("drafts/real_motion")
WORK.mkdir(parents=True,exist_ok=True)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MAX_ZIP=800*1024*1024
MAX_SOURCE=190*1024*1024
LABELS=[("GTA VI", "PAS UN SIMPLE MONTAGE"),
        ("JASON & LUCIA", "LEONIDA NOUS ATTEND"),
        ("VICE CITY", "DU VRAI MOUVEMENT"),
        ("ET TOI ?", "TU COMMENCES QUAND ?")]

def run(*args):
    p=subprocess.run([str(x) for x in args],capture_output=True,text=True)
    if p.returncode:
        raise RuntimeError("ffmpeg error: "+p.stderr[-800:])
    return p.stdout

def download():
    target=WORK/"rockstar_official_clips.zip"
    req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=65) as stream, target.open("wb") as out:
        size=stream.headers.get("Content-Length","0")
        print("Content length:",size,flush=True)
        if size.isdigit() and int(size)>MAX_ZIP:
            raise RuntimeError("Official source bundle above 800 MB threshold")
        total=0
        while True:
            chunk=stream.read(1024*1024)
            if not chunk:break
            total+=len(chunk)
            if total>MAX_ZIP:raise RuntimeError("Official source bundle too large")
            out.write(chunk)
    return target

def extract_clips(zippath):
    extracted=[]
    with zipfile.ZipFile(zippath) as z:
        files=[x for x in z.infolist() if x.filename.lower().endswith(".mp4") and not x.is_dir()]
        print("Source MP4s:",[(x.filename,x.file_size) for x in files],flush=True)
        # Select original Rockstar promotional character footage; do not use leaked clips.
        for target_name in ("jason","lucia","raul","cal","boobie","dre"):
            items=[x for x in files if target_name in x.filename.lower()]
            for item in items:
                if any(p["name"]==item.filename for p in extracted):continue
                if item.file_size>MAX_SOURCE:continue
                dest=WORK/f"source_{len(extracted)}.mp4"
                with z.open(item) as src,dest.open("wb") as dst:
                    shutil.copyfileobj(src,dst,1024*1024)
                duration=float(run("ffprobe","-v","error","-show_entries","format=duration",
                                   "-of","default=noprint_wrappers=1:nokey=1",dest).strip())
                if duration>=1.2:extracted.append({"name":item.filename,"path":str(dest),"duration":duration})
                else:dest.unlink(missing_ok=True)
                if len(extracted)>=4:break
            if len(extracted)>=4:break
        # Fallback to other official clips when name differs.
        for item in files:
            if len(extracted)>=4:break
            if any(p["name"]==item.filename for p in extracted):continue
            if item.file_size>MAX_SOURCE or "cover" in item.filename.lower():continue
            dest=WORK/f"source_{len(extracted)}.mp4"
            with z.open(item) as src,dest.open("wb") as dst:
                shutil.copyfileobj(src,dst,1024*1024)
            duration=float(run("ffprobe","-v","error","-show_entries","format=duration",
                               "-of","default=noprint_wrappers=1:nokey=1",dest).strip())
            if duration>=1.2:extracted.append({"name":item.filename,"path":str(dest),"duration":duration})
            else:dest.unlink(missing_ok=True)
    if len(extracted)<2:raise RuntimeError("Not enough real motion clips to edit")
    return extracted

def overlay(a,b,index):
    img=Image.new("RGBA",(720,1280),(0,0,0,0))
    d=ImageDraw.Draw(img)
    d.rounded_rectangle((24,35,696,155),radius=22,fill=(5,6,20,210))
    d.text((45,57),"GTA VI  /  LEONIDA",font=ImageFont.truetype(FONT,40),fill=(255,188,205))
    d.rounded_rectangle((18,1030,702,1242),radius=25,fill=(5,5,22,225))
    for y,line in [(1054,a),(1128,b)]:
        size=48
        while size>25:
            font=ImageFont.truetype(FONT,size)
            width=d.textbbox((0,0),line,font=font)[2]
            if width<640:break
            size-=2
        d.text(((720-width)/2,y),line,font=font,fill=(255,251,250))
    d.rectangle((0,1262,720,1280),fill=(25,5,25,230))
    d.text((23,1264),"REVIEW ONLY • COMMERCIAL RIGHTS UNCONFIRMED",
           font=ImageFont.truetype(FONT,12),fill=(255,215,220))
    path=WORK/f"overlay_{index}.png";img.save(path);return path

def make_clip(item,index):
    seconds=min(4.0,item["duration"])
    png=overlay(*LABELS[index],index)
    dest=WORK/f"edited_{index}.mp4"
    # Accurate, moving footage in center with blurred 9:16 fill.
    graph=(
        "[0:v]split=2[bg][fg];"
        "[bg]scale=720:1280:force_original_aspect_ratio=increase,"
        "crop=720:1280,boxblur=20:3[b];"
        "[fg]scale=720:1280:force_original_aspect_ratio=decrease[f];"
        "[b][f]overlay=(W-w)/2:(H-h)/2:shortest=1[v];"
        "[v][1:v]overlay=0:0:shortest=1[out]"
    )
    run("ffmpeg","-hide_banner","-loglevel","error","-y","-i",item["path"],"-loop","1","-i",png,
        "-t",seconds,"-filter_complex",graph,"-map","[out]","-an",
        "-r","24","-c:v","libx264","-preset","veryfast","-crf","25",
        "-pix_fmt","yuv420p","-movflags","+faststart",dest)
    return dest

def main():
    print("Fetching public official Rockstar clip pack for review; not relicensed for paid ads.",flush=True)
    archive=download()
    sources=extract_clips(archive)
    archive.unlink(missing_ok=True)
    picks=sources[:4]
    edited=[make_clip(p,i) for i,p in enumerate(picks)]
    concat=WORK/"concat.txt"
    concat.write_text("".join("file '"+e.name+"'\n" for e in edited),encoding="utf8")
    movie=WORK/"gta_vi_real_motion_REVIEW_ONLY.mp4"
    run("ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
        "-i",concat,"-c","copy","-movflags","+faststart",movie)
    (WORK/"RIGHTS_AND_SOURCES.txt").write_text(
      "REVIEW ONLY. THIS VIDEO IS NOT LICENSED FOR A PAID COMMERCIAL CAMPAIGN.\n"
      "Original moving video assets from Rockstar, downloaded from:\n"+URL+"\n"
      "Selected filenames:\n"+"\n".join(x["name"] for x in picks)+"\n"
      "No audio is embedded; official Tokyo Girl sound is required on eligible platforms.\n"
      "Before public monetized distribution: get written permission from Rockstar/Take-Two\n"
      "and verify the song campaign rules, the required disclosure and the rights in all footage.\n",
      encoding="utf8")
    print("SUCCESS_REAL_MOVING_FOOTAGE",movie,flush=True)

if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""UNPUBLISHED preview with Rockstar's publicly released GTA VI screenshots.
Commercial use is NOT licensed by Rockstar's general fan-video policy.
No third-party streamer footage, music, publication or platform uploads.
"""
import io
import math
import random
import subprocess
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H, FPS = 720, 1280, 24
TOTAL = 14
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Original images on Rockstar's own GTA VI media page; no fan edits/third-party streams.
SOURCES = [
    ("Jason & Lucia", "https://www.rockstargames.com/VI/_next/static/media/Jason_and_Lucia_14.10e7v.06pcm_t.jpg?akim=1&imdensity=1&imwidth=1920"),
    ("Lucia Caminos", "https://www.rockstargames.com/VI/_next/static/media/Lucia_Caminos_12.0saq9ns-~xj03.jpg?akim=1&imdensity=1&imwidth=1920"),
    ("Vice City", "https://www.rockstargames.com/VI/_next/static/media/Vice_City_27.0d2e~w_r93hmh.jpg?akim=1&imdensity=1&imwidth=1920"),
]
STORY = [
    ("POV: YOU SAID", "ONE LAST MISSION", 0),
    ("THEN YOU LOOK", "AT THE CLOCK...", 1),
    ("STILL LOST IN", "VICE CITY", 2),
    ("IT'S ALREADY", "3 AM?!", 0)
]

def get_image(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; GTA6-draft-preview/1.0)",
        "Referer": "https://www.rockstargames.com/VI/media",
        "Accept": "image/avif,image/webp,image/jpeg,image/png,image/*"
    })
    with urllib.request.urlopen(req, timeout=30) as response:
        data = response.read(12_000_000)
        kind = response.headers.get("Content-Type", "")
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
        if min(img.size) < 400: raise ValueError("Image resolution too small")
        return img.convert("RGB")
    except Exception as exc:
        raise RuntimeError("Official GTA VI image unavailable: " + kind) from exc

def typeface(label, default=64, max_width=645):
    for n in range(default, 28, -2):
        font = ImageFont.truetype(BOLD, n)
        if ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0,0),label,font=font)[2] < max_width:
            return font
    return ImageFont.truetype(BOLD, 28)

def prepare(source):
    # Background is the actual image, defocused; foreground keeps the artwork visible.
    wide = ImageOps.fit(source,(W,H),method=Image.Resampling.LANCZOS)
    blurred = wide.filter(ImageFilter.GaussianBlur(28))
    shade = Image.new("RGBA",(W,H),(10,5,25,68))
    blurred = Image.alpha_composite(blurred.convert("RGBA"),shade)
    # Preserve full screenshot - avoid cutting off the GTA characters.
    front = ImageOps.contain(source,(688,660),method=Image.Resampling.LANCZOS)
    return blurred, front

def draw_text_center(draw, label, y, font, fill):
    box=draw.textbbox((0,0),label,font=font,stroke_width=2)
    width=box[2]-box[0]
    draw.text(((W-width)//2,y),label,font=font,fill=fill,stroke_width=2,stroke_fill=(5,2,15,240))

def main():
    out=Path("drafts/gta6_actual_visuals_review.mp4")
    out.parent.mkdir(parents=True,exist_ok=True)
    gallery=[]
    for label,url in SOURCES:
        print("Downloading official artwork:",label,flush=True)
        gallery.append(prepare(get_image(url)))
    proc = subprocess.Popen([
        "ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
        "-an","-c:v","libx264","-preset","veryfast","-crf","23",
        "-pix_fmt","yuv420p","-movflags","+faststart",str(out)
    ],stdin=subprocess.PIPE)
    for n in range(TOTAL*FPS):
        sec=n/FPS
        scene=min(3,int(sec/3.5))
        local=sec-3.5*scene
        top_text,bottom_text,img_id=STORY[scene]
        bg,fg=gallery[img_id]
        frame=bg.copy()
        # Subtle motion and crossfade with legible GTA-specific imagery.
        size=1+.035*math.sin((local/3.5)*math.pi)
        w=int(fg.width*size);h=int(fg.height*size)
        zoom=fg.resize((w,h),Image.Resampling.LANCZOS)
        posx=(W-w)//2+int(7*math.sin(sec*1.3))
        posy=240+(660-h)//2+int(11*math.sin(sec*.8))
        frame.alpha_composite(zoom.convert("RGBA"),(posx,posy))
        overlay=Image.new("RGBA",(W,H),(0,0,0,0))
        d=ImageDraw.Draw(overlay)
        d.rounded_rectangle((14,24,W-14,192),radius=24,fill=(12,9,32,213))
        d.rounded_rectangle((14,939,W-14,1228),radius=25,fill=(12,9,32,217))
        d.rounded_rectangle((22,234,698,906),radius=18,outline=(255,160,198,135),width=3)
        d.text((38,41),"GTA VI  /  VICE CITY",font=ImageFont.truetype(BOLD,27),fill=(255,206,224))
        d.text((40,99),"JASON  •  LUCIA  •  LEONIDA",font=ImageFont.truetype(REG,20),fill=(233,231,243))
        d.text((36,980),"FAN EDIT  ·  ORIGINAL TEXT",font=ImageFont.truetype(REG,18),fill=(255,195,211))
        a=max(0,min(255,int(255*min(1,(local+.1)/.55,(3.6-local)/.48))))
        draw_text_center(d,top_text,1020,typeface(top_text,51),(255,251,248,a))
        draw_text_center(d,bottom_text,1111,typeface(bottom_text,49),(255,159,198,a))
        # Never mistake this proof-of-concept for licensed paid promo content.
        d.rounded_rectangle((25,1240,695,1275),radius=10,fill=(0,0,0,190))
        d.text((37,1245),"PREVIEW ONLY  •  PAID USE RIGHTS NOT VERIFIED",font=ImageFont.truetype(BOLD,13),fill=(255,231,233))
        # Fade between storyboard scenes.
        opacity=min(1,(local+.05)/.23,(3.55-local)/.23)
        if opacity<1:
            cover=Image.new("RGBA",(W,H),(9,7,20,int(255*(1-max(0,opacity)))))
            frame=Image.alpha_composite(frame,cover)
        frame=Image.alpha_composite(frame,overlay)
        try: proc.stdin.write(frame.convert("RGB").tobytes())
        except BrokenPipeError: break
    proc.stdin.close()
    if proc.wait()!=0: raise RuntimeError("Failed to render video")
    (out.parent/"README_RIGHTS.txt").write_text(
        "DRAFT FOR PRIVATE REVIEW ONLY - NOT CLEARED FOR PAID CAMPAIGN DISTRIBUTION.\n"
        "Includes copyrighted official Grand Theft Auto VI images from:\n"
        "https://www.rockstargames.com/VI/media\n"
        "Rockstar's public posting policy addresses non-commercial fan activity, not ads,\n"
        "music videos or paid promotional content. Seek explicit written permission.\n"
        "Content Rewards participation does not itself prove Rockstar licensed the footage.\n"
        "Audio is intentionally muted. The campaign's official song must be added inside\n"
        "TikTok or Instagram if all necessary permissions are later obtained.\n"
        "No streamer content, no leaked assets, no publishing, no audio downloaded.\n"
        "Rockstar guidelines: https://support.rockstargames.com/articles/7bNaeoMFTV0iUDGhStTXvz/policy-on-posting-copyrighted-rockstar-games-material\n",
        encoding="utf-8"
    )
    print("SUCCESS: video preview includes GTA VI official images, no music; not publishable without permission.")

if __name__ == "__main__":
    main()

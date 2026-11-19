#!/usr/bin/env python3
"""Original 9:16 GTA VI fan meme. All visuals drawn from code.
Music intentionally absent: add the linked official audio in TikTok/Instagram.
No third-party Twitch/game footage or music is downloaded.
"""
import argparse, json, math, random, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

W,H,FPS=720,1280,24
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
STORIES={
  'one_last_mission':[
    ('POV: YOU SAID','ONE LAST MISSION',''),
    ('5 HOURS','LATER...',''),
    ('STILL IN','VICE CITY',''),
    ('BE HONEST...','YOU TOO?','')],
  'weekend':[
    ('FRIDAY NIGHT','QUICK GTA VI SESSION',''),
    ('BLINK TWICE','AND...',''),
    ('MONDAY','ALREADY?!',''),
    ('BE HONEST...','YOU TOO?','')],
  'sleep':[
    ('ME AT 10 PM','I WILL SLEEP EARLY',''),
    ('STARTS GTA VI','JUST FOR A MINUTE',''),
    ('NEXT THING','IT IS SUNRISE',''),
    ('BE HONEST...','YOU TOO?','')]
}
def fit(text, max_w=615, start=90):
    size=start
    while size>26:
        f=ImageFont.truetype(FONT,size)
        if ImageDraw.Draw(Image.new('RGB',(1,1))).textbbox((0,0),text,font=f)[2]<=max_w:return f
        size-=2
    return ImageFont.truetype(FONT,size)
def background():
    anchors=[(0,(8,8,35)),(.25,(25,16,61)),(.5,(119,42,106)),(.65,(220,102,130)),(.72,(13,14,44)),(1,(4,8,28))]
    pix=np.empty((H,W,3),dtype=np.uint8)
    for y in range(H):
        p=y/(H-1)
        for (ya,a),(yb,b) in zip(anchors[:-1],anchors[1:]):
            if ya<=p<=yb:
                z=(p-ya)/(yb-ya); c=[round(a[i]*(1-z)+b[i]*z) for i in range(3)];break
        pix[y,:,:]=c
    im=Image.fromarray(pix,'RGB');d=ImageDraw.Draw(im)
    d.ellipse((315,445,690,820),fill=(249,174,146))
    for yy in range(670,815,23):
        d.rectangle((314,yy,692,yy+max(4,(yy-650)//17)),fill=(143,65,109))
    rng=random.Random(14)
    for j in range(38):
        x=j*21-14;ht=rng.randint(65,210);wd=rng.randint(20,48)
        d.rectangle((x,840-ht,x+wd,844),fill=(19,17,46))
        for xx in range(x+5,x+wd-2,10):
            for yy in range(850-ht,840,17):
                if rng.random()<.28:d.rectangle((xx,yy,xx+3,yy+5),fill=(241,124,184))
    d.rectangle((0,844,W,H),fill=(8,10,34))
    for yy in [890,936,995,1062,1138,1224]:
        d.line((0,yy,W,yy),fill=(140,50,141),width=2)
    for ex in range(-300,1080,145):
        d.line((360,844,ex,H),fill=(99,57,165),width=3)
    d.polygon([(280,845),(442,845),(690,H),(18,H)],fill=(8,13,37))
    d.line((280,845,18,H),fill=(255,88,164),width=5)
    d.line((442,845,690,H),fill=(255,88,164),width=5)
    for yy in range(930,1250,85):
        d.line((360,yy,360,yy+26),fill=(255,180,138),width=4)
    for x,y,lean in [(60,1110,120),(700,1055,-120)]:
        tip=(x+lean,y-310)
        d.line((x,y,x+lean//2,y-175,*tip),fill=(5,9,29),width=17)
        for a in range(-160,181,38):
            rad=math.radians(a)
            d.line((*tip,tip[0]+math.cos(rad)*165,tip[1]+math.sin(rad)*90+33),fill=(5,9,29),width=12)
    return im
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--story',choices=sorted(STORIES),default='one_last_mission')
    p.add_argument('--out',type=Path,default=Path('drafts/tokyo_girl.mp4'))
    a=p.parse_args();a.out.parent.mkdir(parents=True,exist_ok=True)
    base=background();secs=14
    proc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280',
        '-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','22',
        '-pix_fmt','yuv420p','-movflags','+faststart',str(a.out)],stdin=subprocess.PIPE)
    rng=random.Random(29);stars=[(rng.randint(20,698),rng.randint(45,410),rng.randint(1,3)) for _ in range(40)]
    script=STORIES[a.story]
    for n in range(FPS*secs):
        t=n/FPS;scene=min(3,int(t/3.5));within=t-scene*3.5
        im=base.copy();dr=ImageDraw.Draw(im,'RGBA')
        for idx,(x,y,r) in enumerate(stars):
            alpha=int(120+120*(.5+.5*math.sin(t*2+idx)))
            dr.ellipse((x-r,y-r,x+r,y+r),fill=(255,224,230,alpha))
        dr.rounded_rectangle((23,28,265,79),radius=12,fill=(9,5,26,205),outline=(249,127,191,140),width=2)
        dr.text((38,42),'GTA VI  /  FAN EDIT',font=ImageFont.truetype(FONT_REG,19),fill=(255,238,241,255))
        dr.text((575,44),f'00:{int(t):02}',font=ImageFont.truetype(FONT_REG,21),fill=(255,215,232,210))
        fade=min(1,within/.45,(3.5-within)/.35);alpha=max(0,min(255,int(fade*238)))
        dy=int(28*(1-min(1,within/.5)))
        top=442+dy
        dr.rounded_rectangle((35,top-42,685,top+295),radius=22,fill=(13,8,35,int(alpha*.87)),outline=(255,153,199,int(alpha*.65)),width=2)
        lines=[x for x in script[scene] if x]
        for i,line in enumerate(lines):
            ft=fit(line,start=62 if i==0 else 84)
            box=dr.textbbox((0,0),line,font=ft)
            tw=box[2]-box[0]
            x=(W-tw)//2;y=top+35+i*120
            dr.text((x+3,y+4),line,font=ft,fill=(0,0,20,alpha))
            color=(255,225,233,alpha) if i==0 else (255,151,180,alpha)
            dr.text((x,y),line,font=ft,fill=color)
        dr.rounded_rectangle((46,1035,672,1044),radius=4,fill=(255,255,255,70))
        dr.rounded_rectangle((46,1035,46+int(626*(t/secs)),1044),radius=4,fill=(255,145,195,240))
        dr.text((46,1066),'TELL US YOUR GTA VI ALL-NIGHTER',font=ImageFont.truetype(FONT_REG,22),fill=(255,226,235,230))
        dr.text((46,1110),'ORIGINAL ANIMATED EDIT',font=ImageFont.truetype(FONT_REG,18),fill=(244,177,220,180))
        proc.stdin.write(im.tobytes())
    proc.stdin.close()
    if proc.wait():raise RuntimeError('ffmpeg failed')
    tiktok='POV: one last mission turned into an all-nighter. You too? #GTA6 #GTAVI #ViceCity #ad\nSong: Tokyo Girl by @Passive\n'
    insta='POV: one last mission turned into an all-nighter. You too? #GTA6 #GTAVI #ViceCity #ad\nSong: Tokyo Girl by @PassiveBand\n'
    (a.out.parent/'caption_tiktok.txt').write_text(tiktok,encoding='utf8')
    (a.out.parent/'caption_instagram.txt').write_text(insta,encoding='utf8')
    (a.out.parent/'READ_ME_FIRST.txt').write_text(
        'SILENT ORIGINAL DRAFT. ADD THE OFFICIAL CAMPAIGN AUDIO BEFORE POSTING.\n'
        'TikTok: https://www.tiktok.com/music/Tokyo-Girl-7705214475481123615\n'
        'Instagram: https://www.instagram.com/reels/audio/39659270907051930/\n'
        'NO GAMEPLAY/STREAMER FOOTAGE, VOICEOVERS OR THIRD-PARTY MUSIC USED.\n'
        'Verify platform paid-content disclosures and Placements Whop analytics approval steps.\n'
        'No approval or payment guaranteed.\n',encoding='utf8')
    print('DRAFT_GENERATED',a.story,14,'seconds')
if __name__=='__main__':main()

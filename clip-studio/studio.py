#!/usr/bin/env python3
"""Vertical drafts for media that the user has permission to adapt. Never publishes."""
import argparse
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def cmd(args, **kwargs):
    subprocess.run([str(a) for a in args], check=True, **kwargs)

def timestamp(s):
    ms=round(max(0,s)*1000)
    h, rem=divmod(ms,3600000); m,rem=divmod(rem,60000); sec,milli=divmod(rem,1000)
    return f'{h:02}:{m:02}:{sec:02},{milli:03}'

def transcribe(video, srt, language):
    from faster_whisper import WhisperModel
    audio=srt.parent/'audio.wav'
    audio_res=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(video),'-vn','-ac','1','-ar','16000',str(audio)])
    if audio_res.returncode != 0:
        srt.write_text('',encoding='utf8'); return 0
    model=WhisperModel('tiny',device='cpu',compute_type='int8',cpu_threads=2)
    segments,_=model.transcribe(str(audio),language=None if language=='auto' else language,word_timestamps=True,vad_filter=True,beam_size=1)
    cues=[]
    for seg in segments:
        if seg.words:
            for i in range(0,len(seg.words),7):
                group=seg.words[i:i+7]
                cues.append((group[0].start, group[-1].end, ' '.join(w.word.strip() for w in group)))
        elif seg.text.strip():
            cues.append((seg.start,seg.end,seg.text))
    rows=[]
    for i,(begin,end,text) in enumerate(cues,1):
        text=re.sub(r'\s+',' ',text).replace('-->','→').strip()
        if text: rows.extend([str(i),f'{timestamp(begin)} --> {timestamp(max(end,begin+.1))}',text,''])
    srt.write_text('\n'.join(rows),encoding='utf8')
    audio.unlink(missing_ok=True)
    return len(cues)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--out',type=Path,default=Path('drafts'))
    p.add_argument('--title',default='Moment GTA VI')
    p.add_argument('--creator',default='')
    p.add_argument('--layout',choices=['blur','crop'],default='blur')
    p.add_argument('--language',choices=['auto','fr','en'],default='auto')
    p.add_argument('--start',type=float,default=0)
    p.add_argument('--duration',type=float,default=30)
    p.add_argument('--srt',type=Path)
    a=p.parse_args()
    if not a.input.is_file(): p.error('Input video missing')
    if not(0<=a.start<=7200 and 1<=a.duration<=90): p.error('Invalid start/duration')
    if a.srt and not a.srt.is_file(): p.error('SRT missing')
    result=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(a.input)],capture_output=True,text=True,check=True)
    total=float(result.stdout.strip()); duration=min(a.duration,total-a.start)
    if not math.isfinite(duration) or duration < 1: p.error('Source clip too short')
    a.out.mkdir(parents=True,exist_ok=True)
    sample=a.out/'excerpt.mp4'
    cmd(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',a.start,'-i',a.input,'-t',duration,'-map','0:v:0','-map','0:a?','-c:v','libx264','-preset','ultrafast','-crf','28','-c:a','aac',sample])
    srt=a.out/'subtitles.srt'
    if a.srt:
        shutil.copyfile(a.srt,srt); captions=srt.read_text(encoding='utf8').count('-->')
    else:
        captions=transcribe(sample,srt,a.language)
    if a.layout=='blur':
        graph='[0:v]split=2[b][f];[b]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,boxblur=20:3[bg];[f]scale=720:1280:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2:shortest=1[v]'
    else: graph='[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280[v]'
    creator=re.sub(r'[\r\n\t]+',' ',a.creator).strip()[:60]
    preceding='v'
    if creator:
        (a.out/'credit.txt').write_text('CRÉDIT : '+creator,encoding='utf8')
        graph+=f';[v]drawtext=fontfile={FONT}:textfile=credit.txt:fontcolor=white:fontsize=19:x=28:y=32:box=1:boxcolor=black@0.6:boxborderw=10[credit]'
        preceding='credit'
    if captions:
        graph+=f";[{preceding}]subtitles=subtitles.srt:force_style='FontName=DejaVu Sans,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=3,Alignment=2,MarginV=195'[vout]"
    else: graph+=f';[{preceding}]null[vout]'
    cmd(['ffmpeg','-hide_banner','-loglevel','warning','-y','-i','excerpt.mp4','-filter_complex',graph,'-map','[vout]','-map','0:a?','-r','30','-c:v','libx264','-preset','veryfast','-crf','24','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart','clip_vertical.mp4'],cwd=a.out)
    cmd(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss','0.8','-i',a.out/'clip_vertical.mp4','-frames:v','1',a.out/'thumbnail.jpg'])
    sample.unlink(missing_ok=True)
    title=re.sub(r'[\r\n]+',' ',a.title).strip()[:120] or 'Moment GTA VI'
    (a.out/'caption.txt').write_text(title+(f'\nCrédit : {creator}' if creator else '')+'\n\n#GTAVI #GTA6 #Gaming\n',encoding='utf8')
    (a.out/'manifest.json').write_text(json.dumps({'title':title,'creator':creator,'duration_seconds':round(duration,2),'layout':a.layout,'subtitle_cues':captions,'status':'DRAFT_REVIEW_RIGHTS_AND_CAPTIONS'},ensure_ascii=False,indent=2),encoding='utf8')
    print('OUTPUT_OK 9:16',duration,'seconds,',captions,'subtitle cues')

if __name__=='__main__': main()

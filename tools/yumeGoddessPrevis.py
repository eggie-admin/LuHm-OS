#!/usr/bin/env python3
"""Offline concept-only motion preview, NOT Veo output or verified canon artwork.
Requires user-supplied/local licensed concept board; never fetches protected Drive assets.
"""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

COLORS={
  'lum':('#51e5e0','EXECUTIVE ONI','THE ARCHITECT'),
  'urd':('#f04eaa','GOTH AUDIT GODDESS','THE WEAVER'),
  'belldandy':('#e9af60','CATHEDRAL KEEPER','THE HEART'),
  'skuld':('#6ecaff','CLOCKWORK ENGINEER','THE INVENTOR'),
}
CROPS={
  'lum':(25,135,402,795),
  'urd':(222,270,615,825),
  'belldandy':(390,365,790,870),
  'skuld':(630,335,928,845),
}

def font(px, bold=True):
  path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
  return ImageFont.truetype(path,px)

def hexrgb(c):return tuple(int(c[i:i+2],16) for i in (1,3,5))

def paint(src:Image.Image,shot:str)->Image.Image:
  W,H=540,960
  accent,role,subtitle=COLORS[shot]
  a=hexrgb(accent)
  board=Image.new('RGB',(W,H),'#080a0d')
  # depth layer
  full=ImageOps.fit(src,(W,H),centering=(0.5,0.45)).filter(ImageFilter.GaussianBlur(31))
  board=Image.blend(board,full,0.23)
  ink=ImageDraw.Draw(board)
  # off-register machine lines
  for x in [20,33,508,520]:ink.line([(x,58),(x,895)],fill=tuple(int(v*.35) for v in a),width=2)
  for y in [56,104,808,895]:ink.line([(26,y),(513,y)],fill=tuple(int(v*.34) for v in a),width=2)
  for k in range(7):
    yy=125+k*98
    ink.line([(45,yy),(54,yy+8),(60,yy)],fill='#5d4938',width=3)
  crop=src.crop(CROPS[shot]);hero=ImageOps.fit(crop,(460,620),centering=(0.5,0.34))
  # dark photo corners with readable frame
  board.paste(hero,(40,148))
  overlay=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(overlay)
  for i in range(165):
    y=635+i
    d.rectangle((42,y,498,y+1),fill=(4,5,9,min(225,int(i*1.4))))
  d.rectangle((40,148,499,768),outline=(*a,220),width=3)
  d.rectangle((50,161,489,746),outline=(160,117,66,135),width=1)
  for cx,cy in [(42,148),(498,148),(42,767),(498,767)]:
    d.ellipse((cx-6,cy-6,cx+6,cy+6),fill=(119,91,52,255),outline=(220,171,92,255),width=2)
  board=Image.alpha_composite(board.convert('RGBA'),overlay)
  d=ImageDraw.Draw(board)
  d.text((W/2,72),'PIRATE DADDIES FILM',font=font(19),fill=(238,214,171),anchor='mm',stroke_width=1,stroke_fill=(0,0,0))
  d.text((W/2,124),'LuHm OS  /  PROJECT HYDRA',font=font(13),fill=a,anchor='mm')
  d.text((W/2,776),shot.upper(),font=font(52),fill=a,anchor='mm',stroke_width=2,stroke_fill=(0,0,0))
  d.text((W/2,824),role,font=font(15),fill=(232,223,208),anchor='mm')
  d.text((W/2,855),'PRIVATE MOTION CONCEPT  •  NOT CANON',font=font(10),fill=(177,175,170),anchor='mm')
  d.text((W/2,913),'YUME  /  ORIGINAL ADULT GOTH  /  06s SHOT',font=font(10),fill=(193,145,86),anchor='mm')
  return board.convert('RGB')


def main():
  p=argparse.ArgumentParser()
  p.add_argument('--concept',required=True,type=Path)
  p.add_argument('--output',required=True,type=Path)
  p.add_argument('--render',action='store_true')
  args=p.parse_args()
  out=args.output;out.mkdir(parents=True,exist_ok=True)
  img=Image.open(args.concept).convert('RGB')
  thumbs=[]
  for shot in COLORS:
    framed=paint(img,shot); framed.save(out/f'{shot}Still.png',optimize=True)
    thumbs.append(framed.resize((270,480)))
  collage=Image.new('RGB',(1080,480),'#0b0c0e')
  for i,t in enumerate(thumbs): collage.paste(t,((i%4)*270,0))
  collage.save(out/'fourCharacterContactSheet.png',optimize=True)
  receipt={'conceptImageSha256':hashlib.sha256(args.concept.read_bytes()).hexdigest(), 'type':'OFFLINE_CONCEPT_ANIMATIC_NOT_GOOGLE_GENERATION', 'shotIds':list(COLORS),'finishedVeoVideos':0,'licenseAndProfessorApproval':'PENDING'}
  if args.render:
    shorts=[]
    for shot in COLORS:
      dest=out/f'{shot}Previs.mp4'
      inp=out/f'{shot}Still.png'
      # Deliberately deterministic, small proxy, no audio. All source paths safely arg-separated.
      subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-loop','1','-i',str(inp),'-vf',"zoompan=z='min(zoom+0.00026,1.05)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=144:s=540x960:fps=24,format=yuv420p",'-frames:v','144','-c:v','libx264','-preset','veryfast','-crf','25','-movflags','+faststart',str(dest)],check=True)
      shorts.append(dest)
    concatfile=out/'concat.txt'
    concatfile.write_text(''.join('file '+"'"+str(p.resolve())+"'"+'\n' for p in shorts),encoding='utf-8')
    target=out/'fourGoddesses_CONCEPT_PREVIS_SILENT.mp4'
    subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concatfile),'-c','copy','-movflags','+faststart',str(target)],check=True)
    info=json.loads(subprocess.run(['ffprobe','-v','quiet','-print_format','json','-show_streams','-show_format',str(target)],capture_output=True,text=True,check=True).stdout)
    video=next(s for s in info['streams'] if s['codec_type']=='video')
    assert video['width']==540 and video['height']==960 and video['codec_name']=='h264'
    assert 23.9<float(info['format']['duration'])<24.2
    receipt['previs']={'path':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'width':540,'height':960,'durationSeconds':float(info['format']['duration']),'fps':24,'audio':False}
  (out/'animaticReceipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
  print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()

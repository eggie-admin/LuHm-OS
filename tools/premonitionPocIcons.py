#!/usr/bin/env python3
"""Generate a local prototype launcher PNG, original LuHm horned-L geometry."""
from __future__ import annotations
import argparse
from pathlib import Path
import struct
import zlib

BG=(23,19,31,255)
VIOLET=(159,122,234,255)
WHITE=(247,244,255,255)
PINK=(242,82,188,255)

def inside(x,y,points):
    odd=False
    j=len(points)-1
    for i,p in enumerate(points):
        q=points[j]
        if (p[1]>y)!=(q[1]>y) and x < (q[0]-p[0])*(y-p[1])/(q[1]-p[1])+p[0]:
            odd=not odd
        j=i
    return odd

def pixel(x,y,n):
    u=512*(x+.5)/n
    v=512*(y+.5)/n
    r=96
    if any((u-cx)**2+(v-cy)**2>r*r for cx,cy,where in [
        (r,r,u<r and v<r),
        (512-r,r,u>512-r and v<r),
        (r,512-r,u<r and v>512-r),
        (512-r,512-r,u>512-r and v>512-r)] if where):
        return (0,0,0,0)
    if inside(u,v,[(126,112),(190,182),(148,218),(78,180)]) or inside(u,v,[(386,112),(322,182),(364,218),(434,180)]):
        return VIOLET
    if (146<=u<218 and 150<=v<410) or (146<=u<370 and 338<=v<410):
        return WHITE
    if (u-353)**2+(v-315)**2<34**2:
        return PINK
    return BG

def image(n):
    def chunk(name,body):
        return struct.pack('>I',len(body))+name+body+struct.pack('>I',zlib.crc32(name+body)&0xffffffff)
    rows=b''.join(b'\0'+b''.join(bytes(pixel(x,y,n)) for x in range(n)) for y in range(n))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',n,n,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(rows,9))+chunk(b'IEND',b'')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    for n in (192,432):
        path=args.output/('launcher%d.png'%n)
        path.write_bytes(image(n))
        if path.stat().st_size<500:
            raise SystemExit('RED_EMPTY_BRAND_ICON')
    print('ORIGINAL_LUHM_LAUNCHER_ICON_CREATED')

if __name__=='__main__':
    main()

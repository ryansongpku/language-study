#!/usr/bin/env python3
"""Generate app icons (三 = 'three') as PNGs, no external deps."""
import struct, zlib, math
from pathlib import Path

OUT = Path(__file__).parent

def lerp(a, b, t): return tuple(round(a[i] + (b[i]-a[i])*t) for i in range(3))

def rounded(x, y, w, h, r, px, py):
    """Is point (px,py) inside a rounded rect?"""
    if px < x or px > x+w or py < y or py > y+h: return False
    cx = min(max(px, x+r), x+w-r); cy = min(max(py, y+r), y+h-r)
    return (px-cx)**2 + (py-cy)**2 <= r*r

def make(size):
    top = (0x8b, 0x7d, 0xff); bot = (0x5b, 0x4b, 0xe0)   # gradient
    white = (255, 255, 255)
    buf = bytearray()
    # three bars of 三: (x_frac, w_frac), evenly spaced vertically
    bars = [(0.30, 0.40), (0.27, 0.30), (0.22, 0.56)]
    bar_h = size * 0.085
    r = bar_h/2
    ys = [size*0.34, size*0.50, size*0.66]
    for py in range(size):
        row = bytearray([0])  # filter byte
        base = lerp(top, bot, py/size)
        for px in range(size):
            col = base
            for (xf, wf), cy in zip(bars, ys):
                bx = size*xf; bw = size*wf
                if rounded(bx, cy-bar_h/2, bw, bar_h, r, px, py):
                    col = white; break
            row += bytes(col)
        buf += row
    # encode PNG (RGB, 8-bit)
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(buf), 9)
    png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    return png

for s in (180, 192, 512):
    (OUT / f"icon-{s}.png").write_bytes(make(s))
    print(f"  ✓ icon-{s}.png")

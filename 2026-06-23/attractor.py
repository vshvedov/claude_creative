import numpy as np
from PIL import Image

W = H = 1600
N = 3_000_000
BURN = 1000

def clifford(n, a, b, c, d):
    xs = np.empty(n); ys = np.empty(n)
    x = y = 0.1
    for i in range(BURN):
        x, y = np.sin(a*y)+c*np.cos(a*x), np.sin(b*x)+d*np.cos(b*y)
    for i in range(n):
        x, y = np.sin(a*y)+c*np.cos(a*x), np.sin(b*x)+d*np.cos(b*y)
        xs[i] = x; ys[i] = y
    return xs, ys

def de_jong(n, a, b, c, d):
    xs = np.empty(n); ys = np.empty(n)
    x = y = 0.1
    for i in range(BURN):
        x, y = np.sin(a*y)-np.cos(b*x), np.sin(c*x)-np.cos(d*y)
    for i in range(n):
        x, y = np.sin(a*y)-np.cos(b*x), np.sin(c*x)-np.cos(d*y)
        xs[i] = x; ys[i] = y
    return xs, ys

def density(xs, ys):
    # map roughly [-2.2,2.2] world coords into the canvas with a margin
    lo, hi = -2.3, 2.3
    ix = ((xs - lo)/(hi-lo) * (W-1)).astype(np.int32)
    iy = ((ys - lo)/(hi-lo) * (H-1)).astype(np.int32)
    m = (ix>=0)&(ix<W)&(iy>=0)&(iy<H)
    h = np.zeros((H, W), dtype=np.float64)
    np.add.at(h, (iy[m], ix[m]), 1.0)
    return h

def colorize(h, c_low, c_mid, c_high, bg):
    h = np.log1p(h)
    h /= h.max() if h.max() > 0 else 1.0
    h = h ** 0.85
    bg = np.array(bg, float); cl=np.array(c_low,float); cm=np.array(c_mid,float); ch=np.array(c_high,float)
    img = np.empty((H, W, 3), float)
    # two-segment gradient bg->low->mid->high
    t = h[...,None]
    seg1 = bg + (cl-bg)*np.clip(t/0.33,0,1)
    seg2 = cl + (cm-cl)*np.clip((t-0.33)/0.34,0,1)
    seg3 = cm + (ch-cm)*np.clip((t-0.67)/0.33,0,1)
    img = np.where(t<0.33, seg1, np.where(t<0.67, seg2, seg3))
    return Image.fromarray(np.clip(img,0,255).astype(np.uint8))

pieces = [
    # name, fn, params, palette (bg, low, mid, high)
    ("01_amber_clifford", clifford, (-1.7, 1.8, -1.9, -0.4),
        ((10,8,18),(70,30,60),(220,120,40),(255,240,200))),
    ("02_cyan_dejong", de_jong, (1.641, 1.902, 0.316, 1.525),
        ((6,10,14),(20,60,80),(40,180,200),(220,255,255))),
    ("03_rose_clifford", clifford, (1.5, -1.8, 1.6, 0.9),
        ((14,8,14),(80,20,50),(210,60,120),(255,225,235))),
]

for name, fn, p, pal in pieces:
    xs, ys = fn(N, *p)
    h = density(xs, ys)
    img = colorize(h, pal[1], pal[2], pal[3], pal[0])
    img.save(f"{name}.png")
    nz = (h>0).sum()
    print(f"{name}: params={p}  filled px={nz}  coverage={nz/(W*H)*100:.1f}%")
print("done")

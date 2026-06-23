import sys, time
import numpy as np
from PIL import Image
exec(open('attractor.py').read().split('pieces = [')[0])  # bring in funcs + consts
idx = int(sys.argv[1])
pieces = [
    ("01_amber_clifford", clifford, (-1.7, 1.8, -1.9, -0.4),
        ((10,8,18),(70,30,60),(220,120,40),(255,240,200))),
    ("02_cyan_dejong", de_jong, (1.641, 1.902, 0.316, 1.525),
        ((6,10,14),(20,60,80),(40,180,200),(220,255,255))),
    ("03_rose_clifford", clifford, (1.5, -1.8, 1.6, 0.9),
        ((14,8,14),(80,20,50),(210,60,120),(255,225,235))),
]
name, fn, p, pal = pieces[idx]
t=time.time()
xs, ys = fn(N, *p)
h = density(xs, ys)
img = colorize(h, pal[1], pal[2], pal[3], pal[0])
img.save(f"{name}.png")
nz=(h>0).sum()
print(f"{name}: {time.time()-t:.1f}s  coverage={nz/(W*H)*100:.1f}%")

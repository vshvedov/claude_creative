"""
c–d sweep — third session of 2026-06-23.

The afternoon note ended on an open question:
    "c and d are still frozen. The richest variety came from b, so a c–d sweep at
     one of the bladed bottom-row settings might open a different family entirely."

So: pin a,b at the bladed standout (a=2.26, b=2.04) and walk c and d across a 6x6
grid instead. Same de Jong map, same ensemble trick (60k parallel walkers, burn-in,
then accumulate a density histogram). The only thing changing is *which* pair of
parameters we freeze. Question to answer by eye + by coverage numbers: does swapping
the swept pair give a genuinely different family of shapes, or just the same wing/fan
shapes re-skinned?

Two outputs:
  06_cd_sweep.png         — the 6x6 contact sheet
  07_velocity_standout.png — the new lens (see velocity_render.py): one tile colored
                             by orbital SPEED, not density.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os, sys, json

TILE = 360
GRID = 6
WALKERS = 60_000
STEPS = 500
BURN = 200
PAD = 8
LABEL_H = 22

# Pinned: the bladed standout from the a-b sweep.
A_FIX, B_FIX = 2.26, 2.04
# Swept: the previously-frozen pair. Walk both wide to give a new family room to appear.
C_VALS = np.linspace(-2.4, 2.4, GRID)
D_VALS = np.linspace(-2.4, 2.4, GRID)

# Warmer palette than the cyan a-b sheet, deliberately — this is a different cut of
# the parameter space and I want it to read as its own thing, not a recolor.
BG   = np.array((8, 7, 12), float)
LOW  = np.array((70, 36, 60), float)
MID  = np.array((210, 96, 70), float)
HIGH = np.array((255, 238, 200), float)

WORLD_LO, WORLD_HI = -2.3, 2.3
CACHE = "/tmp/cd_cache"


def dejong_density(a, b, c, d, size, walkers, steps, burn, seed=7):
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1, 1, walkers)
    y = rng.uniform(-1, 1, walkers)
    for _ in range(burn):
        x, y = np.sin(a * y) - np.cos(b * x), np.sin(c * x) - np.cos(d * y)
    flat = np.zeros(size * size, dtype=np.int64)
    span = WORLD_HI - WORLD_LO
    for _ in range(steps):
        x, y = np.sin(a * y) - np.cos(b * x), np.sin(c * x) - np.cos(d * y)
        ix = ((x - WORLD_LO) / span * (size - 1)).astype(np.int64)
        iy = ((y - WORLD_LO) / span * (size - 1)).astype(np.int64)
        m = (ix >= 0) & (ix < size) & (iy >= 0) & (iy < size)
        idx = iy[m] * size + ix[m]
        flat += np.bincount(idx, minlength=size * size)
    return flat.reshape(size, size).astype(np.float64)


def colorize(h, gamma=0.8):
    h = np.log1p(h)
    mx = h.max()
    if mx > 0:
        h /= mx
    h = h ** gamma
    t = h[..., None]
    seg1 = BG + (LOW - BG) * np.clip(t / 0.33, 0, 1)
    seg2 = LOW + (MID - LOW) * np.clip((t - 0.33) / 0.34, 0, 1)
    seg3 = MID + (HIGH - MID) * np.clip((t - 0.67) / 0.33, 0, 1)
    img = np.where(t < 0.33, seg1, np.where(t < 0.67, seg2, seg3))
    return np.clip(img, 0, 255).astype(np.uint8)


def load_font(size):
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


def render_tiles():
    """Resumable: skip tiles already cached, persist meta after every tile so the
    run can be killed and restarted without losing work."""
    os.makedirs(CACHE, exist_ok=True)
    meta_path = os.path.join(CACHE, "meta.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    for r in range(GRID):
        d = D_VALS[r]
        for col in range(GRID):
            c = C_VALS[col]
            key = f"{r}_{col}"
            png = os.path.join(CACHE, key + ".png")
            if os.path.exists(png) and key in meta:
                continue
            h = dejong_density(A_FIX, B_FIX, c, d, TILE, WALKERS, STEPS, BURN)
            Image.fromarray(colorize(h)).save(png)
            cov = float((h > 0).sum() / (TILE * TILE))
            meta[key] = {"c": float(c), "d": float(d), "cov": cov}
            json.dump(meta, open(meta_path, "w"))
            print(f"r{r} c{col}: c={c:+.2f} d={d:+.2f} cov={cov*100:.1f}%", flush=True)
    return meta


def compose(meta):
    font = load_font(13)
    title_font = load_font(26)
    cell_w = TILE + PAD
    cell_h = TILE + LABEL_H + PAD
    margin = 28
    title_band = 70
    sheet_w = margin * 2 + GRID * cell_w - PAD
    sheet_h = margin + title_band + GRID * cell_h - PAD + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (5, 4, 8))
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, margin), "c–d sweep", font=title_font, fill=(255, 238, 200))
    draw.text(
        (margin, margin + 34),
        f"x'=sin(a·y)−cos(b·x), y'=sin(c·x)−cos(d·y)   |   a={A_FIX}, b={B_FIX} fixed (the bladed standout);  "
        f"c: {C_VALS[0]:+.2f}→{C_VALS[-1]:+.2f} (cols),  d: {D_VALS[0]:+.2f}→{D_VALS[-1]:+.2f} (rows)",
        font=font, fill=(170, 120, 120),
    )
    for r in range(GRID):
        for col in range(GRID):
            key = f"{r}_{col}"
            tile = Image.open(os.path.join(CACHE, key + ".png"))
            x0 = margin + col * cell_w
            y0 = margin + title_band + r * cell_h
            sheet.paste(tile, (x0, y0))
            m = meta[key]
            draw.text((x0 + 4, y0 + TILE + 4), f"c={m['c']:+.2f}  d={m['d']:+.2f}",
                      font=font, fill=(200, 150, 140))
    sheet.save("06_cd_sweep.png")
    print("saved 06_cd_sweep.png", sheet.size)
    covs = sorted((v["cov"], v["c"], v["d"]) for v in meta.values())
    print("sparsest:", covs[0])
    print("densest :", covs[-1])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "tiles":
        render_tiles()
    elif cmd == "compose":
        compose(json.load(open(os.path.join(CACHE, "meta.json"))))
    else:
        compose(render_tiles())

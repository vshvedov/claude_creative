"""
de Jong sweep — continuing the 2026-06-23 morning session on strange attractors.

The morning note said: "the de Jong sweep is the one I'd come back to next time —
small nudges to a,b,c,d move it through a whole family of these objects."

So this is that. Fix c and d; sweep a and b across a grid. Each tile is the same
map, just nudged. Laid out as a contact sheet so neighbors sit next to each other
and you can watch one shape dissolve into the next.

Trick for speed: the time axis can't be vectorized (each point needs the last one),
but I CAN run a big ENSEMBLE of walkers in parallel. After burn-in they all live on
the attractor and collectively paint it in a few hundred steps. So every step is a
vectorized op over ~50k walkers — the whole grid renders in seconds.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# --- grid / render config ---
TILE = 360          # px per tile (square)
GRID = 6            # 6x6 = 36 attractors
WALKERS = 60_000    # parallel trajectories per tile
STEPS = 500         # iterations after burn-in
BURN = 200
PAD = 8             # gap between tiles
LABEL_H = 22        # strip under each tile for the param label

# fixed pair (from the morning's favorite de Jong), swept pair varies
C_FIX, D_FIX = 0.316, 1.525
A_VALS = np.linspace(1.3, 2.9, GRID)
B_VALS = np.linspace(1.4, 3.0, GRID)

# de Jong cyan palette, matching the morning piece so the sweep reads as one family
BG   = np.array((6, 10, 14), float)
LOW  = np.array((20, 60, 80), float)
MID  = np.array((40, 180, 200), float)
HIGH = np.array((220, 255, 255), float)

WORLD_LO, WORLD_HI = -2.3, 2.3


def dejong_density(a, b, c, d, size, walkers, steps, burn):
    """Run an ensemble of walkers; return an (size,size) density histogram."""
    rng = np.random.default_rng(7)
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


import os, sys, json

CACHE = "/tmp/dj_cache"


def render_rows(rows):
    """Compute tiles for the given row indices; cache colorized PNG + coverage."""
    os.makedirs(CACHE, exist_ok=True)
    meta_path = os.path.join(CACHE, "meta.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    for r in rows:
        b = B_VALS[r]
        for c, a in enumerate(A_VALS):
            key = f"{r}_{c}"
            png = os.path.join(CACHE, key + ".png")
            if os.path.exists(png):
                continue
            h = dejong_density(a, b, C_FIX, D_FIX, TILE, WALKERS, STEPS, BURN)
            Image.fromarray(colorize(h)).save(png)
            cov = float((h > 0).sum() / (TILE * TILE))
            meta[key] = {"a": float(a), "b": float(b), "cov": cov}
            print(f"row {r} col {c}: a={a:.2f} b={b:.2f} cov={cov*100:.1f}%", flush=True)
    json.dump(meta, open(meta_path, "w"))


def render_standout():
    meta = json.load(open(os.path.join(CACHE, "meta.json")))
    # "interesting" = filaments without filling the frame: coverage closest to 0.18
    best = min(meta.values(), key=lambda v: abs(v["cov"] - 0.18))
    a, b = best["a"], best["b"]
    print(f"standout a={a:.3f} b={b:.3f} cov={best['cov']*100:.1f}%", flush=True)
    h = dejong_density(a, b, C_FIX, D_FIX, 1600, 120_000, 900, 300)
    Image.fromarray(colorize(h, gamma=0.82)).save("05_dejong_standout.png")
    with open("standout.txt", "w") as f:
        f.write(f"a={a:.4f} b={b:.4f} c={C_FIX} d={D_FIX} cov={best['cov']*100:.1f}%\n")
    print("saved 05_dejong_standout.png", flush=True)


def main():
    font = load_font(13)
    title_font = load_font(26)

    cell_w = TILE + PAD
    cell_h = TILE + LABEL_H + PAD
    margin = 28
    title_band = 70
    sheet_w = margin * 2 + GRID * cell_w - PAD
    sheet_h = margin + title_band + GRID * cell_h - PAD + margin

    sheet = Image.new("RGB", (sheet_w, sheet_h), (4, 6, 9))
    draw = ImageDraw.Draw(sheet)

    draw.text((margin, margin), "de Jong sweep", font=title_font, fill=(220, 255, 255))
    draw.text(
        (margin, margin + 34),
        f"x'=sin(a·y)−cos(b·x), y'=sin(c·x)−cos(d·y)   |   c={C_FIX}, d={D_FIX} fixed;  "
        f"a: {A_VALS[0]:.2f}→{A_VALS[-1]:.2f} (cols),  b: {B_VALS[0]:.2f}→{B_VALS[-1]:.2f} (rows)",
        font=font, fill=(120, 160, 175),
    )

    meta = json.load(open(os.path.join(CACHE, "meta.json")))
    for r in range(GRID):
        for c in range(GRID):
            key = f"{r}_{c}"
            tile = Image.open(os.path.join(CACHE, key + ".png"))
            x0 = margin + c * cell_w
            y0 = margin + title_band + r * cell_h
            sheet.paste(tile, (x0, y0))
            m = meta[key]
            draw.text((x0 + 4, y0 + TILE + 4), f"a={m['a']:.2f}  b={m['b']:.2f}",
                      font=font, fill=(150, 190, 205))

    sheet.save("04_dejong_sweep.png")
    print("saved 04_dejong_sweep.png", sheet.size)
    covs = sorted((v["cov"], v["a"], v["b"]) for v in meta.values())
    print("sparsest:", covs[0])
    print("densest :", covs[-1])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "rows":
        render_rows([int(x) for x in sys.argv[2:]])
    elif cmd == "standout":
        render_standout()
    elif cmd == "compose":
        main()
    else:
        render_rows(range(GRID))
        render_standout()
        main()

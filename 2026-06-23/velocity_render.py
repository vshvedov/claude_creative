"""
The velocity lens — a new way to look at the same attractor.

Every render so far colored by DENSITY: how often the orbit visits each pixel. That's
a map of *where* attention pools. This asks a different question: how FAST is the orbit
moving when it's there? At each step I know the jump length |Δ| = ||(x',y') - (x,y)||.
Accumulate the mean jump length per bin and you get a map of *pace* — the bright-hot
filaments are where the orbit is sprinting through, the cool-dark ones are where it
shuffles in tiny steps and lingers.

Density and speed are not the same map. A bin can be visited rarely but always crossed
at high speed (a thin fast-traversed thread), or visited constantly in tiny increments
(a slow dense fold). This render shows both at once:
    brightness  = log-density  (so the familiar shape is still legible)
    colour      = mean speed   (cool violet = slow/lingering -> hot white = racing)

Standout chosen from the c–d sweep: the "open-jaw" tile at c=+1.44, d=-0.48, a=2.26,
b=2.04 — enough structure (cov ~18.7%) to have distinct fast and slow regions.
"""

import numpy as np
from PIL import Image

A, B, C, D = 2.26, 2.04, 1.44, -0.48
SIZE = 1600
WALKERS = 120_000
STEPS = 900
BURN = 300
WORLD_LO, WORLD_HI = -2.3, 2.3
OUT = "07_velocity_standout.png"


def accumulate():
    """Return (count, speed_sum) histograms over the attractor."""
    rng = np.random.default_rng(11)
    x = rng.uniform(-1, 1, WALKERS)
    y = rng.uniform(-1, 1, WALKERS)
    for _ in range(BURN):
        x, y = np.sin(A * y) - np.cos(B * x), np.sin(C * x) - np.cos(D * y)

    n = SIZE * SIZE
    count = np.zeros(n, np.float64)
    speed = np.zeros(n, np.float64)
    span = WORLD_HI - WORLD_LO
    for _ in range(STEPS):
        nx, ny = np.sin(A * y) - np.cos(B * x), np.sin(C * x) - np.cos(D * y)
        step = np.hypot(nx - x, ny - y)          # jump length this iteration
        x, y = nx, ny
        ix = ((x - WORLD_LO) / span * (SIZE - 1)).astype(np.int64)
        iy = ((y - WORLD_LO) / span * (SIZE - 1)).astype(np.int64)
        m = (ix >= 0) & (ix < SIZE) & (iy >= 0) & (iy < SIZE)
        idx = iy[m] * SIZE + ix[m]
        count += np.bincount(idx, minlength=n)
        speed += np.bincount(idx, weights=step[m], minlength=n)
    return count.reshape(SIZE, SIZE), speed.reshape(SIZE, SIZE)


def speed_ramp(t):
    """t in [0,1] -> RGB. Cool violet (slow) -> teal -> amber -> white (fast)."""
    stops = [
        (0.00, (30, 18, 60)),     # slow: deep violet
        (0.35, (40, 110, 150)),   # teal
        (0.65, (235, 150, 60)),   # amber
        (1.00, (255, 250, 235)),  # fast: near-white
    ]
    t = np.clip(t, 0, 1)
    r = np.zeros_like(t); g = np.zeros_like(t); b = np.zeros_like(t)
    for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:]):
        seg = (t >= t0) & (t <= t1)
        f = (t[seg] - t0) / (t1 - t0)
        for ch, arr in zip(range(3), (r, g, b)):
            arr[seg] = c0[ch] + (c1[ch] - c0[ch]) * f
    return np.stack([r, g, b], axis=-1)


def main():
    count, speed = accumulate()
    occ = count > 0
    mean_speed = np.zeros_like(speed)
    mean_speed[occ] = speed[occ] / count[occ]

    # Normalise speed robustly across occupied bins (5th–95th percentile).
    vals = mean_speed[occ]
    lo, hi = np.percentile(vals, 5), np.percentile(vals, 95)
    s_norm = np.clip((mean_speed - lo) / (hi - lo + 1e-9), 0, 1)

    # Brightness from log-density so the shape stays legible.
    bright = np.log1p(count)
    bright /= bright.max()
    bright = bright ** 0.8

    rgb = speed_ramp(s_norm) * bright[..., None]
    img = np.clip(rgb, 0, 255).astype(np.uint8)
    Image.fromarray(img).save(OUT)

    # Report what the lens actually separated.
    print(f"saved {OUT}  ({SIZE}x{SIZE})")
    print(f"occupied bins: {occ.sum():,}  ({occ.mean()*100:.1f}% of frame)")
    print(f"mean jump length over occupied bins: {vals.mean():.4f}")
    print(f"  slowest 5%: <= {lo:.4f}   fastest 5%: >= {hi:.4f}   ratio {hi/lo:.1f}x")
    # Correlation between how-often-visited and how-fast: are dense regions slow?
    c_occ = count[occ]
    r = np.corrcoef(np.log(c_occ), vals)[0, 1]
    print(f"corr(log density, speed) over occupied bins: {r:+.3f}")


if __name__ == "__main__":
    main()

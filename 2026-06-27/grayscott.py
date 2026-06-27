#!/usr/bin/env python3
"""
Gray-Scott reaction-diffusion system.

Two chemicals U and V evolve according to:
  ∂u/∂t = Du·∇²u  −  u·v²  +  F·(1−u)
  ∂v/∂t = Dv·∇²v  +  u·v²  −  (F+k)·v

U is replenished from outside at rate F.
V is consumed at rate (F+k).
They react: U + 2V → 3V  (autocatalytic)

Different (F, k) pairs give qualitatively different steady-state patterns:
spots, labyrinths, worms, coral, pulsing holes ...
Turing described this mechanism in 1952. Pearson catalogued the parameter
space numerically in 1993.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
import time

OUT = Path(__file__).parent

# ── colormaps ────────────────────────────────────────────────────────────────
# Each pattern gets its own color personality.

def _cmap(name, stops):
    """Build a linear colormap from a list of (pos, r, g, b) tuples."""
    rd = {'red': [], 'green': [], 'blue': []}
    for p, r, g, b in stops:
        rd['red'].append((p, r, r))
        rd['green'].append((p, g, g))
        rd['blue'].append((p, b, b))
    return LinearSegmentedColormap(name, rd, N=512)

# void black → dark amber → gold → pale cream
AMBER = _cmap('amber', [
    (0.00, 0.03, 0.01, 0.00),
    (0.30, 0.30, 0.10, 0.00),
    (0.65, 0.85, 0.55, 0.05),
    (1.00, 0.98, 0.96, 0.80),
])

# void black → deep navy → bright cyan → pale aqua
CYAN = _cmap('cyan', [
    (0.00, 0.02, 0.02, 0.08),
    (0.30, 0.00, 0.10, 0.38),
    (0.65, 0.00, 0.72, 0.80),
    (1.00, 0.80, 0.98, 0.96),
])

# void black → deep purple → vivid rose → pale lavender
ROSE = _cmap('rose', [
    (0.00, 0.04, 0.00, 0.05),
    (0.30, 0.30, 0.00, 0.28),
    (0.65, 0.92, 0.20, 0.55),
    (1.00, 0.98, 0.88, 0.95),
])

# void black → forest → spring green → pale mint
GREEN = _cmap('green', [
    (0.00, 0.01, 0.03, 0.01),
    (0.30, 0.02, 0.22, 0.08),
    (0.65, 0.08, 0.75, 0.25),
    (1.00, 0.88, 0.99, 0.88),
])

# sweep: dark → indigo → teal → pale sky (scientific, consistent)
TEAL = _cmap('teal', [
    (0.00, 0.04, 0.02, 0.10),
    (0.35, 0.02, 0.12, 0.45),
    (0.70, 0.05, 0.68, 0.72),
    (1.00, 0.82, 0.98, 0.94),
])

BG = '#060610'

# ── simulation ───────────────────────────────────────────────────────────────

def laplacian(z):
    """5-point stencil Laplacian, periodic boundaries."""
    return (np.roll(z, 1, 0) + np.roll(z, -1, 0) +
            np.roll(z, 1, 1) + np.roll(z, -1, 1) - 4.0 * z)


def simulate(N, F, k, steps, Du=0.2097, Dv=0.1050, dt=1.0,
             seed=0, center_only=False, snapshots=None):
    """
    Run Gray-Scott for `steps` steps on an N×N grid.
    Returns (u, v) final fields, or if snapshots=[t1, t2, ...], a list of v
    arrays captured at those timesteps (plus the final state).
    """
    rng = np.random.default_rng(seed)
    u = np.ones((N, N), dtype=np.float64)
    v = np.zeros((N, N), dtype=np.float64)

    if center_only:
        r = max(N // 10, 4)
        cx = cy = N // 2
        h = w = 2 * r
        u[cx-r:cx+r, cy-r:cy+r] = 0.50 + rng.uniform(-0.05, 0.05, (h, w))
        v[cx-r:cx+r, cy-r:cy+r] = 0.25 + rng.uniform(-0.05, 0.05, (h, w))
    else:
        n_seeds = 20
        for _ in range(n_seeds):
            cx = rng.integers(5, N - 5)
            cy = rng.integers(5, N - 5)
            r = rng.integers(3, 8)
            sl = (slice(max(0, cx-r), min(N, cx+r)),
                  slice(max(0, cy-r), min(N, cy+r)))
            h = sl[0].stop - sl[0].start
            w = sl[1].stop - sl[1].start
            u[sl] = 0.50 + rng.uniform(-0.05, 0.05, (h, w))
            v[sl] = 0.25 + rng.uniform(-0.05, 0.05, (h, w))

    snaps = []
    snap_set = set(snapshots) if snapshots else set()

    for t in range(1, steps + 1):
        uvv = u * v * v
        u += dt * (Du * laplacian(u) - uvv + F * (1.0 - u))
        v += dt * (Dv * laplacian(v) + uvv - (F + k) * v)
        np.clip(u, 0.0, 1.0, out=u)
        np.clip(v, 0.0, 1.0, out=v)
        if t in snap_set:
            snaps.append((t, v.copy()))

    if snapshots is not None:
        return snaps
    return u, v


# ── rendering helpers ─────────────────────────────────────────────────────────

def show(ax, v, cmap, vmax=None):
    ax.imshow(v, cmap=cmap, vmin=0, vmax=vmax or max(v.max(), 0.01),
              interpolation='lanczos')
    ax.axis('off')


def save(fig, name):
    path = OUT / name
    fig.savefig(path, dpi=120, bbox_inches='tight', facecolor=BG)
    plt.close(fig)
    return path


# ── individual renders ───────────────────────────────────────────────────────

PATTERNS = [
    # (filename, title,  F,      k,      steps, cmap)
    ('01_spots.png',     'spots\nF 0.037  k 0.060',      0.0370, 0.0600, 8000,  AMBER),
    ('02_labyrinth.png', 'labyrinth\nF 0.026  k 0.051',  0.0260, 0.0510, 10000, CYAN),
    ('03_coral.png',     'coral\nF 0.039  k 0.058',      0.0390, 0.0580, 8000,  ROSE),
    ('04_worms.png',     'worms\nF 0.030  k 0.057',      0.0300, 0.0570, 8000,  GREEN),
]

N_INDIV = 360

def render_individuals():
    print("Individual patterns")
    for fname, title, F, k, steps, cmap in PATTERNS:
        t0 = time.time()
        print(f"  {fname} ... ", end='', flush=True)
        u, v = simulate(N_INDIV, F, k, steps)
        fig, ax = plt.subplots(figsize=(6, 6.5), facecolor=BG)
        ax.set_facecolor(BG)
        show(ax, v, cmap)
        ax.set_title(title, color='#8aabb8', fontsize=9.5,
                     fontfamily='monospace', pad=8, linespacing=1.6)
        fig.tight_layout(pad=0.3)
        save(fig, fname)
        print(f"{time.time()-t0:.1f}s")


# ── parameter space sweep ────────────────────────────────────────────────────

def render_sweep():
    """8×8 survey of (F, k) space, F increasing upward, k increasing rightward."""
    Fs = np.linspace(0.010, 0.058, 8)
    ks = np.linspace(0.042, 0.066, 8)
    SN = 130
    SSTEPS = 5000

    print(f"Parameter sweep 8×8 (N={SN}, {SSTEPS} steps each) ...", flush=True)
    t0 = time.time()

    fig, axes = plt.subplots(8, 8, figsize=(14, 14.8),
                             facecolor=BG,
                             gridspec_kw={'wspace': 0.025, 'hspace': 0.025})

    for i, F in enumerate(Fs):
        row = 7 - i  # F increases upward
        for j, k in enumerate(ks):
            ax = axes[row][j]
            _, v = simulate(SN, F, k, SSTEPS)
            ax.imshow(v, cmap=TEAL, vmin=0, vmax=max(v.max(), 0.01),
                      interpolation='nearest')
            ax.axis('off')

    # k labels (top and bottom)
    for j, k in enumerate(ks):
        axes[0][j].set_title(f'k={k:.3f}', color='#6a8fa0', fontsize=7,
                              fontfamily='monospace')

    # F labels (left side)
    for i, F in enumerate(Fs):
        row = 7 - i
        axes[row][0].set_ylabel(f'F={F:.3f}', color='#6a8fa0', fontsize=7,
                                 fontfamily='monospace', rotation=0, labelpad=36)

    fig.suptitle('Gray-Scott  ·  parameter space  ·  F (↑) × k (→)',
                 color='#b8cfd8', fontsize=11, fontfamily='monospace', y=0.999)

    save(fig, '05_sweep.png')
    print(f"  {time.time()-t0:.0f}s")


# ── time-evolution panel ─────────────────────────────────────────────────────

def render_evolution():
    """
    Show one pattern nucleating and spreading over time.
    Four panels: t=200, t=1000, t=3000, t=8000.
    Uses a single central seed so the spreading front is visible.
    """
    F, k = 0.026, 0.051  # labyrinth parameters
    SNAPS = [200, 1000, 3000, 8000]
    NE = 380

    print(f"Evolution strip (F={F}, k={k}, N={NE}) ... ", end='', flush=True)
    t0 = time.time()

    records = simulate(NE, F, k, steps=max(SNAPS), center_only=True,
                       snapshots=SNAPS)

    vmax = max(v.max() for _, v in records)
    vmax = max(vmax, 0.01)

    fig, axes = plt.subplots(1, 4, figsize=(18, 4.8),
                             facecolor=BG,
                             gridspec_kw={'wspace': 0.04})

    for ax, (t, v) in zip(axes, records):
        ax.imshow(v, cmap=CYAN, vmin=0, vmax=vmax, interpolation='lanczos')
        ax.axis('off')
        ax.set_title(f't = {t}', color='#7faabb', fontsize=10,
                     fontfamily='monospace', pad=7)

    fig.suptitle('labyrinth nucleating from a central seed  ·  F 0.026  k 0.051',
                 color='#b0c8d5', fontsize=10, fontfamily='monospace', y=1.01)

    save(fig, '06_evolution.png')
    print(f"{time.time()-t0:.1f}s")


# ── entry point ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("Gray-Scott reaction-diffusion")
    print("=" * 45)
    render_individuals()
    render_sweep()
    render_evolution()
    print("\nAll done.")

#!/usr/bin/env python3
"""
Gray-Scott reaction-diffusion simulation.
2026-06-24 free time

du/dt = Du·∇²u  -  u·v²  +  f·(1-u)
dv/dt = Dv·∇²v  +  u·v²  -  (f+k)·v

Du=0.2, Dv=0.1 throughout.
Pattern type is governed entirely by (f, k).
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import time, sys, os

Du, Dv = 0.20, 0.10


# ── simulation ──────────────────────────────────────────────────────────────

def lap(z):
    return (np.roll(z,  1, 0) + np.roll(z, -1, 0) +
            np.roll(z,  1, 1) + np.roll(z, -1, 1) - 4.0 * z)

def gs_step(u, v, f, k, dt=1.0):
    uvv = u * v * v
    u2 = u + dt * (Du * lap(u) - uvv + f * (1.0 - u))
    v2 = v + dt * (Dv * lap(v) + uvv - (f + k) * v)
    np.clip(u2, 0.0, 1.0, out=u2)
    np.clip(v2, 0.0, 1.0, out=v2)
    return u2, v2

def make_init(N, n_seeds=30, seed=0):
    rng = np.random.default_rng(seed)
    u = np.ones((N, N), dtype=np.float32)
    v = np.zeros((N, N), dtype=np.float32)
    margin = N // 6
    for _ in range(n_seeds):
        x = rng.integers(margin, N - margin)
        y = rng.integers(margin, N - margin)
        r = rng.integers(4, 10)
        x0, x1 = max(0, x-r), min(N, x+r)
        y0, y1 = max(0, y-r), min(N, y+r)
        u[x0:x1, y0:y1] = 0.50
        v[x0:x1, y0:y1] = 0.25
    return u, v

def simulate(f, k, N=256, steps=8000, dt=1.0, seed=0, verbose=True):
    u, v = make_init(N, seed=seed)
    t0 = time.time()
    for i in range(steps):
        u, v = gs_step(u, v, f, k, dt)
        if verbose and (i + 1) % 2000 == 0:
            elapsed = time.time() - t0
            eta = elapsed / (i+1) * (steps - i - 1)
            print(f"  {i+1}/{steps}  {elapsed:.1f}s elapsed  {eta:.0f}s left",
                  flush=True)
    return u, v


# ── rendering ────────────────────────────────────────────────────────────────

BG = '#080808'

def render_single(v, cmap, label, path, N_display=None, dpi=180):
    if N_display is not None:
        from scipy.ndimage import zoom
        scale = N_display / v.shape[0]
        v = zoom(v, scale, order=1)

    fig, ax = plt.subplots(figsize=(7, 7), facecolor=BG)
    vmax = float(np.quantile(v, 0.998))
    ax.imshow(v, cmap=cmap, interpolation='bilinear', vmin=0.0, vmax=vmax,
              origin='upper')
    ax.axis('off')
    ax.set_title(label, color='#888888', pad=5, fontsize=10,
                 fontfamily='monospace', loc='left')
    plt.tight_layout(pad=0.0)
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor=BG)
    plt.close(fig)
    print(f"→ {path}")


def render_gallery(entries, path, ncols=3, dpi=150):
    """entries: list of (v, cmap, title)"""
    n = len(entries)
    nrows = (n + ncols - 1) // ncols

    fig = plt.figure(figsize=(ncols * 4, nrows * 4), facecolor=BG)
    gs = gridspec.GridSpec(nrows, ncols, figure=fig, wspace=0.03, hspace=0.10)

    for i, (v, cmap, title) in enumerate(entries):
        ax = fig.add_subplot(gs[i // ncols, i % ncols])
        vmax = float(np.quantile(v, 0.998))
        ax.imshow(v, cmap=cmap, interpolation='bilinear', vmin=0.0, vmax=vmax)
        ax.set_title(title, color='#777777', fontsize=8,
                     fontfamily='monospace', pad=3)
        ax.axis('off')

    for i in range(n, nrows * ncols):
        fig.add_subplot(gs[i // ncols, i % ncols]).set_visible(False)

    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor=BG)
    plt.close(fig)
    print(f"→ {path}")


# ── parameter sets ───────────────────────────────────────────────────────────

# Each entry: (name, f, k, colormap, description)
PATTERNS = [
    ('spots',    0.035, 0.065, 'plasma',
     'spots    f=0.035  k=0.065'),
    ('coral',    0.037, 0.060, 'inferno',
     'coral    f=0.037  k=0.060'),
    ('mazes',    0.029, 0.057, 'hot',
     'mazes    f=0.029  k=0.057'),
    ('holes',    0.039, 0.058, 'viridis',
     'holes    f=0.039  k=0.058'),
    ('worms',    0.062, 0.062, 'magma',
     'worms    f=0.062  k=0.062'),
    ('mitosis',  0.028, 0.053, 'cividis',
     'mitosis  f=0.028  k=0.053'),
]


# ── main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    gallery = []
    for name, f, k, cmap, desc in PATTERNS:
        print(f'\n▸ {desc}', flush=True)
        u, v = simulate(f, k, N=256, steps=8000, verbose=True)
        render_single(v, cmap, desc, f'{name}.png')
        gallery.append((v, cmap, desc))

    print('\n▸ gallery', flush=True)
    render_gallery(gallery, '01_gallery.png')
    print('\nDone.')

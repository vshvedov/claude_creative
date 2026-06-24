#!/usr/bin/env python3
"""
Temporal evolution of a Gray-Scott pattern.
Capture snapshots at T = 0, 500, 1500, 3500, 7000, 12000.
Uses mitosis parameters (f=0.028, k=0.053) — the most dramatic self-replication.

Starts with a single centered square of V instead of random seeds,
so the growth radiates outward rather than appearing everywhere at once.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import time, os

Du, Dv = 0.20, 0.10
BG = '#080808'

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


def make_single_seed(N):
    """Single square of V in the center."""
    u = np.ones((N, N), dtype=np.float32)
    v = np.zeros((N, N), dtype=np.float32)
    c, r = N // 2, 12
    u[c-r:c+r, c-r:c+r] = 0.50
    v[c-r:c+r, c-r:c+r] = 0.25
    return u, v


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    N       = 300
    f, k    = 0.028, 0.053
    SNAPSHOTS = [0, 500, 1500, 3500, 7000, 12000]
    CMAP    = 'plasma'

    u, v = make_single_seed(N)
    snaps = {}
    t0 = time.time()
    step_count = 0

    for snap_at in SNAPSHOTS:
        steps_needed = snap_at - step_count
        for _ in range(steps_needed):
            u, v = gs_step(u, v, f, k)
        step_count = snap_at
        snaps[snap_at] = v.copy()
        print(f'  snapshot T={snap_at}  ({time.time()-t0:.1f}s)', flush=True)

    print('Rendering …', flush=True)

    n = len(SNAPSHOTS)
    ncols = 3
    nrows = (n + ncols - 1) // ncols

    fig = plt.figure(figsize=(ncols * 4.2, nrows * 4.4), facecolor=BG)
    gs  = gridspec.GridSpec(nrows, ncols, figure=fig, wspace=0.04, hspace=0.12)

    vmax = float(np.quantile(snaps[SNAPSHOTS[-1]], 0.998))

    for i, t in enumerate(SNAPSHOTS):
        ax = fig.add_subplot(gs[i // ncols, i % ncols])
        ax.imshow(snaps[t], cmap=CMAP, interpolation='bilinear',
                  vmin=0, vmax=vmax, origin='upper')
        ax.set_title(f'T = {t:,}', color='#888888', fontsize=9,
                     fontfamily='monospace', pad=3)
        ax.axis('off')

    fig.text(0.5, 0.99,
             'Gray-Scott  mitosis  f=0.028  k=0.053  —  single seed, propagating outward',
             color='#555555', fontsize=8, fontfamily='monospace',
             ha='center', va='top')

    out = '03_evolution.png'
    fig.savefig(out, dpi=160, bbox_inches='tight', facecolor=BG)
    plt.close(fig)
    print(f'→ {out}  ({time.time()-t0:.0f}s total)')

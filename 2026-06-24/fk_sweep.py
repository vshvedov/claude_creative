#!/usr/bin/env python3
"""
Gray-Scott f–k parameter sweep.
5×5 grid: f on horizontal axis, k on vertical axis.
Small grid (160×160) and 6000 steps — enough to show the pattern family.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import time, os, sys

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

def make_init(N, n_seeds=20, seed=7):
    rng = np.random.default_rng(seed)
    u = np.ones((N, N), dtype=np.float32)
    v = np.zeros((N, N), dtype=np.float32)
    margin = N // 6
    for _ in range(n_seeds):
        x = rng.integers(margin, N - margin)
        y = rng.integers(margin, N - margin)
        r = rng.integers(4, 9)
        x0, x1 = max(0, x-r), min(N, x+r)
        y0, y1 = max(0, y-r), min(N, y+r)
        u[x0:x1, y0:y1] = 0.50
        v[x0:x1, y0:y1] = 0.25
    return u, v

def simulate(f, k, N=160, steps=6000, seed=7):
    u, v = make_init(N, seed=seed)
    for _ in range(steps):
        u, v = gs_step(u, v, f, k)
    return v


# ── sweep parameters ─────────────────────────────────────────────────────────

# f (feed rate) — horizontal axis
F_VALS = np.linspace(0.018, 0.058, 5)   # [0.018, 0.028, 0.038, 0.048, 0.058]
# k (kill rate) — vertical axis (high k at top)
K_VALS = np.linspace(0.068, 0.050, 5)   # descending: stricter kill at top

N_SIM = 160
STEPS = 6000
CMAP  = 'plasma'


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    nf, nk = len(F_VALS), len(K_VALS)
    total = nf * nk
    print(f'{total} simulations  ({nk} k-values × {nf} f-values)', flush=True)
    print(f'Grid {N_SIM}×{N_SIM}  steps={STEPS}\n')

    # collect all V arrays
    results = np.zeros((nk, nf, N_SIM, N_SIM), dtype=np.float32)
    t_start = time.time()

    for ik, k in enumerate(K_VALS):
        for jf, f in enumerate(F_VALS):
            idx = ik * nf + jf + 1
            print(f'  [{idx:02d}/{total}] f={f:.3f}  k={k:.3f}', end='  ', flush=True)
            t0 = time.time()
            results[ik, jf] = simulate(f, k, N=N_SIM, steps=STEPS)
            print(f'{time.time()-t0:.1f}s', flush=True)

    print(f'\nAll done in {time.time()-t_start:.0f}s. Rendering …', flush=True)

    # ── render contact sheet ──────────────────────────────────────────────────
    pad = 0.02
    cell_w, cell_h = 3.0, 3.0
    label_col = 0.55   # width of k-label column on left
    label_row = 0.40   # height of f-label row at top

    fig_w = label_col + nf * cell_w + (nf - 1) * pad * cell_w
    fig_h = label_row + nk * cell_h + (nk - 1) * pad * cell_h

    fig = plt.figure(figsize=(fig_w, fig_h), facecolor=BG)

    # use a plain GridSpec — we'll place axes manually with add_axes
    # compute normalized positions
    total_w = fig_w
    total_h = fig_h

    def norm_x(px): return px / total_w
    def norm_y(py): return py / total_h

    # global vmax for consistent color scale
    vmax = float(np.quantile(results[results > 0], 0.998)) if results.max() > 0 else 0.3

    cell_w_n = cell_w / total_w
    cell_h_n = cell_h / total_h
    pad_w_n  = pad * cell_w / total_w
    pad_h_n  = pad * cell_h / total_h
    label_col_n = label_col / total_w
    label_row_n = label_row / total_h

    for ik in range(nk):
        for jf in range(nf):
            # bottom-left corner of this cell (matplotlib y=0 is bottom)
            x_left  = label_col_n + jf * (cell_w_n + pad_w_n)
            # ik=0 is top row in our data (highest k), so flip for matplotlib
            row_from_bottom = (nk - 1 - ik)
            y_bottom = label_row_n + row_from_bottom * (cell_h_n + pad_h_n)

            ax = fig.add_axes([x_left, y_bottom, cell_w_n, cell_h_n])
            ax.imshow(results[ik, jf], cmap=CMAP,
                      interpolation='bilinear', vmin=0, vmax=vmax,
                      origin='upper')
            ax.axis('off')

    # f labels along top
    for jf, f in enumerate(F_VALS):
        x_ctr = label_col_n + jf * (cell_w_n + pad_w_n) + cell_w_n / 2
        y_top  = label_row_n + nk * (cell_h_n + pad_h_n) - pad_h_n
        fig.text(x_ctr, y_top + 0.008, f'f={f:.3f}',
                 color='#777777', fontsize=9, fontfamily='monospace',
                 ha='center', va='bottom', transform=fig.transFigure)

    # k labels along left
    for ik, k in enumerate(K_VALS):
        row_from_bottom = (nk - 1 - ik)
        y_ctr = label_row_n + row_from_bottom * (cell_h_n + pad_h_n) + cell_h_n / 2
        fig.text(label_col_n - 0.01, y_ctr, f'k={k:.3f}',
                 color='#777777', fontsize=9, fontfamily='monospace',
                 ha='right', va='center', transform=fig.transFigure)

    # axis labels
    x_mid = label_col_n + nf * (cell_w_n + pad_w_n) / 2
    fig.text(x_mid, 0.012, 'feed rate  f  →',
             color='#555555', fontsize=10, fontfamily='monospace',
             ha='center', va='bottom', transform=fig.transFigure)

    fig.text(0.005, label_row_n + nk * (cell_h_n + pad_h_n) / 2,
             '← kill rate  k',
             color='#555555', fontsize=10, fontfamily='monospace',
             ha='left', va='center', rotation=90, transform=fig.transFigure)

    fig.text(0.5, 0.99,
             'Gray-Scott f–k sweep  (Du=0.20  Dv=0.10  160×160  6000 steps)',
             color='#444444', fontsize=8.5, fontfamily='monospace',
             ha='center', va='top', transform=fig.transFigure)

    out = '02_fk_sweep.png'
    fig.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close(fig)
    print(f'→ {out}')

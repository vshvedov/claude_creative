"""
Gray-Scott reaction-diffusion simulation.

Two "chemicals" u and v diffuse across a grid at different rates
and react with each other. The equations:

  du/dt = Du * ∇²u  -  u·v²  +  f·(1 - u)
  dv/dt = Dv * ∇²v  +  u·v²  -  (f + k)·v

u is replenished at feed rate f; v decays at kill rate k.
The reaction term (u·v²) converts u → v in a catalytic, autocatalytic way:
v requires two v molecules to catalyze each reaction.

The only free parameters (besides diffusion constants, which are fixed)
are f and k. Changing them by a few hundredths produces completely different
stable forms: spots, stripes, worms, spirals, solitons, chaos.

That Turing identified this mechanism in 1952, and that it actually underlies
animal coat patterns, is one of those facts that doesn't get less strange with
repetition.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mc
from pathlib import Path

OUT = Path(__file__).parent


def laplacian(Z):
    """5-point discrete Laplacian with periodic boundary conditions."""
    return (
        np.roll(Z, 1, 0) + np.roll(Z, -1, 0) +
        np.roll(Z, 1, 1) + np.roll(Z, -1, 1) -
        4 * Z
    )


def run(f, k, n=256, steps=8000, dt=1.0, Du=0.16, Dv=0.08, seed=42):
    """Simulate Gray-Scott on an n×n grid for `steps` iterations."""
    rng = np.random.default_rng(seed)

    # Start: u=1 everywhere, v=0; seed a small square in the middle with v≈1
    u = np.ones((n, n))
    v = np.zeros((n, n))

    # Seed several small blobs
    cx, cy = n // 2, n // 2
    r = n // 10
    u[cy-r:cy+r, cx-r:cx+r] = 0.5 + rng.uniform(-0.02, 0.02, (2*r, 2*r))
    v[cy-r:cy+r, cx-r:cx+r] = 0.25 + rng.uniform(-0.02, 0.02, (2*r, 2*r))

    for _ in range(steps):
        uvv = u * v * v
        u += dt * (Du * laplacian(u) - uvv + f * (1.0 - u))
        v += dt * (Dv * laplacian(v) + uvv - (f + k) * v)
        np.clip(u, 0, 1, out=u)
        np.clip(v, 0, 1, out=v)

    return u, v


def render(u, v, title, filename, cmap_u='magma', cmap_v=None):
    """Render the v-field (the interesting one) to a file."""
    fig, ax = plt.subplots(figsize=(7, 7), dpi=150)
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')

    # Normalise v to [0,1]
    vn = (v - v.min()) / (v.max() - v.min() + 1e-12)

    if cmap_v:
        img = ax.imshow(vn, cmap=cmap_v, interpolation='bilinear', origin='lower')
    else:
        img = ax.imshow(vn, cmap=cmap_u, interpolation='bilinear', origin='lower')

    ax.set_title(title, color='white', fontsize=11, pad=8, fontfamily='monospace')
    ax.axis('off')

    fig.tight_layout(pad=0.3)
    path = OUT / filename
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f"  saved → {path.name}")
    return path


def render_dual(u, v, title, filename):
    """Side-by-side u and v fields."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.5), dpi=150)
    fig.patch.set_facecolor('#0a0a0a')

    for ax, field, name, cmap in zip(
        axes, [u, v], ['u  (activator)', 'v  (inhibitor)'], ['viridis', 'magma']
    ):
        ax.set_facecolor('black')
        fn = (field - field.min()) / (field.max() - field.min() + 1e-12)
        ax.imshow(fn, cmap=cmap, interpolation='bilinear', origin='lower')
        ax.set_title(name, color='#aaa', fontsize=10, fontfamily='monospace')
        ax.axis('off')

    fig.suptitle(title, color='white', fontsize=12, fontfamily='monospace', y=1.01)
    fig.tight_layout(pad=0.5)
    path = OUT / filename
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close(fig)
    print(f"  saved → {path.name}")
    return path


def render_sweep(results, f_vals, k_vals, filename):
    """Grid of v-fields for a parameter sweep."""
    nf, nk = len(f_vals), len(k_vals)
    fig, axes = plt.subplots(nf, nk, figsize=(nk * 2.4, nf * 2.4), dpi=120)
    fig.patch.set_facecolor('#060606')

    for i, f in enumerate(f_vals):
        for j, k in enumerate(k_vals):
            ax = axes[i][j]
            ax.set_facecolor('black')
            u, v = results[(f, k)]
            vn = (v - v.min()) / (v.max() - v.min() + 1e-12)
            ax.imshow(vn, cmap='magma', interpolation='bilinear', origin='lower')
            ax.set_title(f'f={f:.3f}\nk={k:.3f}', color='#888', fontsize=6.5,
                         fontfamily='monospace', pad=2)
            ax.axis('off')

    fig.suptitle('Gray-Scott  —  (f, k) parameter sweep', color='white',
                 fontsize=13, fontfamily='monospace', y=1.01)
    fig.tight_layout(pad=0.4)
    path = OUT / filename
    fig.savefig(path, dpi=120, bbox_inches='tight', facecolor='#060606')
    plt.close(fig)
    print(f"  saved → {path.name}")
    return path


if __name__ == '__main__':
    print("Gray-Scott reaction-diffusion")
    print("=" * 40)

    # --- Named regimes ---
    named = [
        # (f,     k,      label,           filename,          steps, cmap)
        (0.037, 0.060,  'spots            f=0.037  k=0.060', '01_spots.png',    10000, 'magma'),
        (0.040, 0.059,  'stripes          f=0.040  k=0.059', '02_stripes.png',  10000, 'plasma'),
        (0.062, 0.062,  'worms            f=0.062  k=0.062', '03_worms.png',    10000, 'inferno'),
        (0.030, 0.057,  'solitons         f=0.030  k=0.057', '04_solitons.png', 12000, 'magma'),
        (0.026, 0.051,  'chaos            f=0.026  k=0.051', '05_chaos.png',    12000, 'viridis'),
        (0.050, 0.065,  'coral / labyrinth f=0.050 k=0.065', '06_coral.png',    10000, 'hot'),
    ]

    print("\nRendering named regimes...")
    for f, k, label, fname, steps, cmap in named:
        print(f"  [{label.strip()}]  steps={steps}")
        u, v = run(f, k, n=300, steps=steps, seed=7)
        render(u, v, label, fname, cmap_v=cmap)

    # Dual render for spots (most visually clear)
    print("\nDual render (spots)...")
    u, v = run(0.037, 0.060, n=300, steps=10000, seed=7)
    render_dual(u, v, 'spots — u and v fields   (f=0.037  k=0.060)', '07_spots_dual.png')

    # --- Parameter sweep ---
    print("\nParameter sweep  (f × k grid, 5×5)...")
    f_vals = [0.022, 0.030, 0.037, 0.050, 0.062]
    k_vals = [0.051, 0.055, 0.060, 0.063, 0.066]
    results = {}
    for f in f_vals:
        for k in k_vals:
            print(f"  f={f:.3f}  k={k:.3f} ...", end='', flush=True)
            u, v = run(f, k, n=200, steps=8000, seed=7)
            results[(f, k)] = (u, v)
            print(" done")
    render_sweep(results, f_vals, k_vals, '08_sweep.png')

    print("\nAll done.")

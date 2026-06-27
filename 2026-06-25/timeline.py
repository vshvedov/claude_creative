"""
Show the temporal evolution of a Gray-Scott system.
Same parameters, snapshots at increasing step counts.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).parent


def laplacian(Z):
    return (
        np.roll(Z, 1, 0) + np.roll(Z, -1, 0) +
        np.roll(Z, 1, 1) + np.roll(Z, -1, 1) -
        4 * Z
    )


def evolve(u, v, steps, f, k, dt=1.0, Du=0.16, Dv=0.08):
    for _ in range(steps):
        uvv = u * v * v
        u += dt * (Du * laplacian(u) - uvv + f * (1.0 - u))
        v += dt * (Dv * laplacian(v) + uvv - (f + k) * v)
        np.clip(u, 0, 1, out=u)
        np.clip(v, 0, 1, out=v)
    return u, v


def render_timeline(f, k, checkpoints, n=280, seed=42, filename='09_timeline.png'):
    """Simulate step-by-step and snapshot at each checkpoint."""
    rng = np.random.default_rng(seed)

    u = np.ones((n, n))
    v = np.zeros((n, n))
    cx, cy = n // 2, n // 2
    r = n // 12
    u[cy-r:cy+r, cx-r:cx+r] = 0.5 + rng.uniform(-0.02, 0.02, (2*r, 2*r))
    v[cy-r:cy+r, cx-r:cx+r] = 0.25 + rng.uniform(-0.02, 0.02, (2*r, 2*r))

    snaps = []
    prev = 0
    for step in checkpoints:
        u, v = evolve(u, v, step - prev, f, k)
        snaps.append((step, v.copy()))
        prev = step
        print(f"  step {step:>6} — v range [{v.min():.3f}, {v.max():.3f}]")

    ncols = len(checkpoints)
    fig, axes = plt.subplots(1, ncols, figsize=(ncols * 3.2, 3.5), dpi=150)
    fig.patch.set_facecolor('#060606')

    for ax, (step, snap) in zip(axes, snaps):
        ax.set_facecolor('black')
        vn = (snap - snap.min()) / (snap.max() - snap.min() + 1e-12)
        ax.imshow(vn, cmap='magma', interpolation='bilinear', origin='lower')
        ax.set_title(f't = {step:,}', color='#aaa', fontsize=9, fontfamily='monospace')
        ax.axis('off')

    fig.suptitle(
        f'finding equilibrium  —  f={f:.3f}  k={k:.3f}',
        color='white', fontsize=11, fontfamily='monospace', y=1.02
    )
    fig.tight_layout(pad=0.3)
    path = OUT / filename
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='#060606')
    plt.close(fig)
    print(f"  saved → {path.name}")


if __name__ == '__main__':
    print("Timeline render — stripes finding equilibrium")
    render_timeline(
        f=0.040, k=0.059,
        checkpoints=[100, 500, 1000, 2500, 5000, 10000],
        filename='09_timeline_stripes.png'
    )

    print("\nTimeline render — spots (labyrinth)")
    render_timeline(
        f=0.037, k=0.060,
        checkpoints=[200, 800, 2000, 4000, 7000, 10000],
        filename='10_timeline_spots.png'
    )

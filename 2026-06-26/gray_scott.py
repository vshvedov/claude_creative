"""
Gray-Scott reaction-diffusion system.

dU/dt = Du * laplacian(U) - U*V^2 + F*(1-U)
dV/dt = Dv * laplacian(V) + U*V^2 - (F+k)*V

U = activator-degrader (the "substrate")
V = activator (the pattern-forming chemical)

Different (F, k) pairs produce qualitatively different patterns:
  spots, stripes, mazes, worms, corals, mitosis...
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap


def laplacian(Z):
    """5-point finite-difference Laplacian with periodic boundary."""
    return (
        np.roll(Z,  1, axis=0) + np.roll(Z, -1, axis=0) +
        np.roll(Z,  1, axis=1) + np.roll(Z, -1, axis=1) -
        4 * Z
    )


def run_gray_scott(F, k, N=256, steps=10000, dt=1.0,
                   Du=0.16, Dv=0.08, seed=42, init='random_spots'):
    """
    Simulate Gray-Scott on an N×N grid for `steps` steps.
    Returns the V (pattern-forming) field.
    """
    rng = np.random.default_rng(seed)

    U = np.ones((N, N), dtype=np.float64)
    V = np.zeros((N, N), dtype=np.float64)

    if init == 'random_spots':
        # Seed with random small squares of high V
        for _ in range(20):
            r = rng.integers(N // 4, 3 * N // 4)
            c = rng.integers(N // 4, 3 * N // 4)
            size = rng.integers(3, 8)
            r0, r1 = max(0, r - size), min(N, r + size)
            c0, c1 = max(0, c - size), min(N, c + size)
            U[r0:r1, c0:c1] = 0.50
            V[r0:r1, c0:c1] = 0.25
    elif init == 'center_blob':
        cx, cy = N // 2, N // 2
        s = N // 8
        U[cx-s:cx+s, cy-s:cy+s] = 0.50
        V[cx-s:cx+s, cy-s:cy+s] = 0.25
    elif init == 'noise':
        U = 1.0 - 0.05 * rng.random((N, N))
        V = 0.05 * rng.random((N, N))

    # Add a tiny bit of noise to V to break symmetry
    V += 0.02 * rng.random((N, N))

    for _ in range(steps):
        UV2 = U * V * V
        U += dt * (Du * laplacian(U) - UV2 + F * (1 - U))
        V += dt * (Dv * laplacian(V) + UV2 - (F + k) * V)
        np.clip(U, 0, 1, out=U)
        np.clip(V, 0, 1, out=V)

    return V


def make_cmap_inkblot():
    """Dark background, blue-white pattern."""
    colors = [(0.05, 0.05, 0.10), (0.10, 0.25, 0.50), (0.85, 0.92, 1.00)]
    return LinearSegmentedColormap.from_list('inkblot', colors)

def make_cmap_bone():
    """Warm off-white on charcoal — like an X-ray."""
    colors = [(0.08, 0.07, 0.06), (0.45, 0.38, 0.32), (0.96, 0.93, 0.88)]
    return LinearSegmentedColormap.from_list('bone_warm', colors)

def make_cmap_coral():
    """Dark ocean, bright coral."""
    colors = [(0.04, 0.04, 0.12), (0.55, 0.15, 0.25), (1.00, 0.72, 0.45)]
    return LinearSegmentedColormap.from_list('coral', colors)

def make_cmap_biolum():
    """Black water, glowing cyan."""
    colors = [(0.00, 0.02, 0.08), (0.00, 0.40, 0.50), (0.60, 1.00, 0.90)]
    return LinearSegmentedColormap.from_list('biolum', colors)


NAMED_PARAMS = {
    # name: (F, k, description)
    'mitosis':   (0.0367, 0.0649, 'self-replicating spots that divide'),
    'coral':     (0.0545, 0.0620, 'branching coral / dendritic growth'),
    'labyrinth': (0.0600, 0.0630, 'maze-like wandering passages'),
    'worms':     (0.0700, 0.0630, 'tangled worm-like filaments'),
    'spots':     (0.0300, 0.0620, 'stable isolated spots on a smooth field'),
    'fingerprint':(0.0550, 0.0655, 'parallel stripe arcs — like a fingerprint'),
}


if __name__ == '__main__':
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else 'labyrinth'
    F, k, desc = NAMED_PARAMS[name]
    V = run_gray_scott(F, k)
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.imshow(V, cmap=make_cmap_inkblot(), interpolation='nearest')
    ax.axis('off')
    plt.tight_layout(pad=0)
    out = f'/home/user/claude_creative/2026-06-26/{name}_preview.png'
    plt.savefig(out, bbox_inches='tight', pad_inches=0)
    print(f'Saved {out}')

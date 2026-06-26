"""
High-resolution standout render with shaded-relief lighting.

Treat the V field as a height map, compute surface normals, apply a
directional light. The resulting image looks like the pattern has been
carved into metal or etched in stone — the same underlying simulation,
but suddenly three-dimensional.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from gray_scott import run_gray_scott


def shaded_relief(height, light_dir=(1.0, 1.0, 2.5), ambient=0.28, steepness=8.0):
    """
    Convert a 2D height field to a shaded-relief image (H×W×3).
    light_dir: (dx, dy, dz) — unnormalized; positive z is toward the viewer.
    steepness: multiplier on gradients — higher = more dramatic relief.
    """
    # Gradients via finite differences, then exaggerate for visible relief
    dz_dx = np.gradient(height, axis=1) * steepness
    dz_dy = np.gradient(height, axis=0) * steepness

    # Surface normal: (-dz/dx, -dz/dy, 1) — pointing up
    nx = -dz_dx
    ny = -dz_dy
    nz = np.ones_like(height)
    norm = np.sqrt(nx**2 + ny**2 + nz**2)
    nx /= norm; ny /= norm; nz /= norm

    # Light direction (normalized)
    lx, ly, lz = light_dir
    l_norm = np.sqrt(lx**2 + ly**2 + lz**2)
    lx /= l_norm; ly /= l_norm; lz /= l_norm

    # Diffuse shading
    diffuse = np.clip(nx * lx + ny * ly + nz * lz, 0, 1)
    shade = ambient + (1 - ambient) * diffuse   # in [ambient, 1]

    return shade  # scalar [0,1]


def make_standout(name, F, k, N=512, steps=18000, seed=13,
                  cmap_colors=None, light_dir=(1.2, 0.8, 3.0), steepness=10.0):

    print(f'Simulating {name} at {N}×{N}, {steps} steps...')
    V = run_gray_scott(F, k, N=N, steps=steps, seed=seed)

    print('Computing shaded relief...')
    shade = shaded_relief(V, light_dir=light_dir, steepness=steepness)

    if cmap_colors is None:
        # Default: cool steel
        cmap_colors = [(0.04, 0.04, 0.10), (0.20, 0.35, 0.60), (0.85, 0.92, 1.00)]
    cmap = LinearSegmentedColormap.from_list('standout', cmap_colors)

    # Map V through the colormap to get base color
    V_norm = V / max(V.max(), 1e-6)
    rgba = cmap(V_norm)           # H×W×4

    # Multiply each RGB channel by the shade
    rgb = rgba[..., :3] * shade[..., np.newaxis]
    rgb = np.clip(rgb, 0, 1)

    fig, ax = plt.subplots(figsize=(9, 9), dpi=180)
    fig.patch.set_facecolor('#050508')
    ax.imshow(rgb, interpolation='bilinear')
    ax.axis('off')

    out = f'/home/user/claude_creative/2026-06-26/{name}.png'
    plt.savefig(out, bbox_inches='tight', pad_inches=0.04,
                facecolor=fig.get_facecolor())
    plt.close()
    print(f'Saved {out}')
    return V, shade


STANDOUTS = [
    # (filename, F, k, colormap_colors, light_dir, description)
    (
        '07_standout_coral',
        0.0545, 0.0620,
        [(0.04, 0.03, 0.10), (0.40, 0.10, 0.20), (1.00, 0.70, 0.38)],
        (1.5, 0.8, 2.5),
        'Coral/dendritic branching rendered as shaded relief — the tips '
        'catch the light like raised ridges, the background recedes into shadow.'
    ),
    (
        '08_standout_labyrinth',
        0.0600, 0.0630,
        [(0.04, 0.04, 0.12), (0.12, 0.30, 0.60), (0.88, 0.96, 1.00)],
        (1.0, 1.5, 3.0),
        'Labyrinth as a topographic relief — the walls are ridges, '
        'the corridors valleys. The lighting makes it read as architecture.'
    ),
]


if __name__ == '__main__':
    for filename, F, k, colors, light, desc in STANDOUTS:
        V, shade = make_standout(filename, F, k, cmap_colors=colors,
                                 light_dir=light, steepness=12.0)
        print(f'  V range: [{V.min():.4f}, {V.max():.4f}]')
        print(f'  shade range: [{shade.min():.4f}, {shade.max():.4f}]')
        print()
    print('Done.')

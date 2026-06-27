"""
Render individual Gray-Scott pieces — each with a matched colormap.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from gray_scott import run_gray_scott

def cmap_inkblot():
    return LinearSegmentedColormap.from_list('inkblot',
        [(0.04, 0.04, 0.10), (0.10, 0.25, 0.55), (0.88, 0.94, 1.00)])

def cmap_bone():
    return LinearSegmentedColormap.from_list('bone_warm',
        [(0.08, 0.07, 0.06), (0.40, 0.33, 0.26), (0.96, 0.93, 0.88)])

def cmap_coral():
    return LinearSegmentedColormap.from_list('coral',
        [(0.04, 0.03, 0.10), (0.50, 0.12, 0.22), (1.00, 0.70, 0.42)])

def cmap_biolum():
    return LinearSegmentedColormap.from_list('biolum',
        [(0.00, 0.02, 0.08), (0.00, 0.38, 0.48), (0.55, 1.00, 0.88)])

def cmap_ember():
    return LinearSegmentedColormap.from_list('ember',
        [(0.03, 0.02, 0.02), (0.55, 0.20, 0.05), (1.00, 0.85, 0.30)])


PIECES = [
    # (filename, F, k, steps, cmap_fn, title, description)
    ('01_labyrinth', 0.0600, 0.0630, 12000, cmap_inkblot,
     'Labyrinth (F=0.06, k=0.063)',
     'The default wandering-maze pattern. No two runs look the same, '
     'but the topology is always the same: one long connected boundary '
     'that splits the plane into two mutually inaccessible halves.'),

    ('02_mitosis', 0.0367, 0.0649, 14000, cmap_biolum,
     'Mitosis (F=0.037, k=0.065)',
     'Spots that divide. A single blob grows elongated, pinches in the '
     'middle, and resolves into two daughters — which then do the same. '
     'Population grows until the field reaches carrying capacity.'),

    ('03_coral', 0.0545, 0.0620, 12000, cmap_coral,
     'Coral (F=0.055, k=0.062)',
     'Dendritic branching like coral or lightning. Each tip grows '
     'forward and periodically bifurcates. The branches repel each other '
     'so the structure fills space without crossing itself.'),

    ('04_fingerprint', 0.0550, 0.0655, 14000, cmap_bone,
     'Fingerprint (F=0.055, k=0.066)',
     'Parallel stripe arcs — the pattern named after what it looks like. '
     'Stripes align locally but the global pattern has no long-range order; '
     'each domain finds its own orientation.'),

    ('05_worms', 0.0700, 0.0630, 12000, cmap_ember,
     'Worms (F=0.07, k=0.063)',
     'Dense tangled filaments — somewhere between labyrinth and coral. '
     'The higher feed rate keeps more V alive, so the passages are '
     'narrower and the overall density is higher.'),
]


def render_piece(filename, F, k, steps, cmap_fn, title, description):
    print(f'  Simulating {filename} (F={F}, k={k}, {steps} steps)...')
    V = run_gray_scott(F, k, N=300, steps=steps, seed=7)

    fig, ax = plt.subplots(figsize=(7, 7), dpi=160)
    fig.patch.set_facecolor('#080808')
    ax.imshow(V, cmap=cmap_fn(), interpolation='bilinear', vmin=0, vmax=V.max())
    ax.axis('off')

    path = f'/home/user/claude_creative/2026-06-26/{filename}.png'
    plt.savefig(path, bbox_inches='tight', pad_inches=0.02,
                facecolor=fig.get_facecolor())
    plt.close()
    print(f'  Saved {path}')
    return path


if __name__ == '__main__':
    print('Rendering individual pieces...')
    for piece in PIECES:
        render_piece(*piece)
    print('Done.')

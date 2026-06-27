"""
Parameter sweep across (F, k) space — the "Pearson diagram".

6×6 contact sheet: F on x-axis (feed rate), k on y-axis (kill rate).
Each cell is a small Gray-Scott simulation; the sheet shows how pattern
type changes continuously across the space.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from gray_scott import run_gray_scott

# The interesting region of Pearson space
F_VALS = np.linspace(0.022, 0.078, 7)   # feed rate
K_VALS = np.linspace(0.052, 0.072, 6)   # kill rate (ascending, so top row = high k)

GRID_N    = 150   # grid size per cell
STEPS     = 6000  # simulation steps per cell
CELL_PX   = 120   # rendered pixels per cell
PAD       = 4     # pixels between cells

# Single dark colormap for the whole sheet (easier to read family transitions)
CMAP = LinearSegmentedColormap.from_list('sheet',
    [(0.04, 0.04, 0.10), (0.15, 0.35, 0.60), (0.90, 0.96, 1.00)])


def render_sweep():
    nF = len(F_VALS)
    nK = len(K_VALS)

    total_w = nF * CELL_PX + (nF - 1) * PAD + 60   # left margin for k labels
    total_h = nK * CELL_PX + (nK - 1) * PAD + 50   # bottom margin for F labels
    dpi = 120
    fig_w = total_w / dpi
    fig_h = total_h / dpi

    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
    fig.patch.set_facecolor('#080810')

    results = {}

    for j, k in enumerate(K_VALS):
        for i, F in enumerate(F_VALS):
            print(f'  F={F:.3f} k={k:.3f}  ({j*nF+i+1}/{nK*nF})', flush=True)
            V = run_gray_scott(F, k, N=GRID_N, steps=STEPS, seed=42)
            results[(i, j)] = (F, k, V)

    # Place cells manually using axes
    left_margin  = 52 / total_w
    bottom_margin= 42 / total_h
    cell_w = CELL_PX / total_w
    cell_h = CELL_PX / total_h
    gap_w  = PAD / total_w
    gap_h  = PAD / total_h

    for j in range(nK):
        for i in range(nF):
            F, k, V = results[(i, j)]
            # j=0 is low k; plot j=0 at the bottom
            x0 = left_margin + i * (cell_w + gap_w)
            y0 = bottom_margin + j * (cell_h + gap_h)
            ax = fig.add_axes([x0, y0, cell_w, cell_h])
            ax.imshow(V, cmap=CMAP, interpolation='bilinear',
                      vmin=0, vmax=max(V.max(), 0.01))
            ax.axis('off')

            # Label the outermost edges
            if j == nK - 1:
                ax.set_title(f'F={F:.3f}', fontsize=5.5, color='#aabbcc',
                             pad=2, fontfamily='monospace')
            if i == 0:
                ax.set_ylabel(f'k={k:.3f}', fontsize=5.5, color='#aabbcc',
                              labelpad=3, rotation=0, va='center',
                              fontfamily='monospace')

    # Title
    fig.text(0.5, 0.99, 'Gray–Scott parameter space  (F × k)',
             ha='center', va='top', color='#ddeeff', fontsize=8,
             fontfamily='monospace')

    out = '/home/user/claude_creative/2026-06-26/06_fk_sweep.png'
    plt.savefig(out, bbox_inches='tight', pad_inches=0.05,
                facecolor=fig.get_facecolor())
    plt.close()
    print(f'Saved {out}')
    return results


if __name__ == '__main__':
    print(f'Running {len(F_VALS)}×{len(K_VALS)} sweep '
          f'({len(F_VALS)*len(K_VALS)} simulations)...')
    results = render_sweep()
    print('Done.')

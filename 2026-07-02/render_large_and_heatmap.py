"""Centerpiece: one big sandpile, plus the avalanche-activity heatmap.

Both images come from the same stabilization run (grid, topple counts) so
we only pay for the expensive N=1,000,000 relaxation once.
"""
import time
import numpy as np
import matplotlib.pyplot as plt
from sandpile import stabilize, to_rgb, touches_boundary

N = 901
GRAINS = 1_000_000

grid = np.zeros((N, N), dtype=np.int64)
grid[N // 2, N // 2] = GRAINS

t0 = time.time()
grid, counts = stabilize(grid, track_topples=True)
print("stabilize took", round(time.time() - t0, 1), "s")
print("touches boundary:", touches_boundary(grid), "max height:", grid.max())

# --- 02: the stable height map ---
fig, ax = plt.subplots(figsize=(11, 11), facecolor="#0b0c10")
ax.imshow(to_rgb(grid), interpolation="nearest")
ax.set_facecolor("#0b0c10")
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_title(f"Abelian sandpile — {GRAINS:,} grains dropped at one point, relaxed to rest",
             color="#e8e8e8", fontsize=13, pad=12)
fig.tight_layout()
fig.savefig("02_large.png", dpi=170, facecolor=fig.get_facecolor(), bbox_inches="tight")
plt.close(fig)

# --- 04: topple-count heatmap, cropped to the active region ---
nz = counts.nonzero()
pad = 6
r0, r1 = max(0, nz[0].min() - pad), min(N, nz[0].max() + pad + 1)
c0, c1 = max(0, nz[1].min() - pad), min(N, nz[1].max() + pad + 1)
counts_c = counts[r0:r1, c0:c1]

fig, ax = plt.subplots(figsize=(10.5, 10), facecolor="#0b0c10")
im = ax.imshow(np.log10(counts_c + 1), cmap="inferno", interpolation="nearest")
ax.set_facecolor("#0b0c10")
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)
cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
cbar.set_label("log10(times this site toppled)", color="#e8e8e8")
cbar.ax.yaxis.set_tick_params(color="#e8e8e8")
plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="#e8e8e8")
ax.set_title(f"Avalanche activity: topple count per site ({GRAINS:,} grains)",
             color="#e8e8e8", fontsize=13, pad=12)
fig.tight_layout()
fig.savefig("04_topple_heatmap.png", dpi=160, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("max topples at a single site:", counts.max())
print("done")

"""Same tiling, but each rhombus is colored by *which pair* of the 5
pentagrid families produced it. There are C(5,2) = 10 such pairs; coloring
by them reveals the tiling's hidden layered structure -- each color forms
its own quasiperiodic sub-lattice of rhombi."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

from penrose import pentagrid_rhombi, bounding_filter

rng = np.random.default_rng(7)
gammas = rng.uniform(-0.5, 0.5, 5)
gammas -= gammas.mean() - 0.13  # same gammas as the classic render, for continuity

rhombi = pentagrid_rhombi(gammas, extent=9)
rhombi = bounding_filter(rhombi, 7.2)

pairs = [(j, k) for j in range(5) for k in range(j + 1, 5)]
cmap = plt.get_cmap("rainbow")
colors = {pair: cmap(i / (len(pairs) - 1)) for i, pair in enumerate(pairs)}

fig, ax = plt.subplots(figsize=(11, 11))
by_color = {}
for r in rhombi:
    by_color.setdefault(r["families"], []).append(Polygon(r["verts"], closed=True))

for pair, polys in by_color.items():
    ax.add_collection(PatchCollection(polys, facecolor=colors[pair], edgecolor="#111111", linewidth=0.3))

ax.set_xlim(-7.2, 7.2)
ax.set_ylim(-7.2, 7.2)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

plt.tight_layout(pad=0.3)
plt.savefig("03_rainbow.png", dpi=150, facecolor="white")
print(f"rhombi drawn: {len(rhombi)}, color groups: {len(by_color)}")

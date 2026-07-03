"""The singular pentagrid (all gammas equal, summing to an integer) gives a
tiling with *exact* 5-fold rotational symmetry about the origin -- de Bruijn's
famous 'cartwheel' / sun pattern. A tiny numerical jitter keeps the handful of
points where 5 lines truly coincide from producing degenerate rhombi."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

from penrose import pentagrid_rhombi, bounding_filter

THIN = "#f2c14e"   # gold
THICK = "#5c2a52"  # deep plum

gammas = np.full(5, 0.2) + 1e-9 * np.array([1, -2, 3, -1, -1])  # sums to 1, near-singular

rhombi = pentagrid_rhombi(gammas, extent=9)
rhombi = bounding_filter(rhombi, 6.6)

fig, ax = plt.subplots(figsize=(11, 11))
patches_thin, patches_thick = [], []
for r in rhombi:
    poly = Polygon(r["verts"], closed=True)
    (patches_thin if r["type"] == "thin" else patches_thick).append(poly)

ax.add_collection(PatchCollection(patches_thin, facecolor=THIN, edgecolor="#20101d", linewidth=0.4))
ax.add_collection(PatchCollection(patches_thick, facecolor=THICK, edgecolor="#20101d", linewidth=0.4))

ax.set_xlim(-6.6, 6.6)
ax.set_ylim(-6.6, 6.6)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("#0d0810")
ax.set_facecolor("#0d0810")

plt.tight_layout(pad=0.3)
plt.savefig("02_sun.png", dpi=150, facecolor="#0d0810")
print(f"rhombi drawn: {len(rhombi)}")

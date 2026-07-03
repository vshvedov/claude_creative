"""Classic Penrose rhombus (P3) tiling from a generic pentagrid."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

from penrose import pentagrid_rhombi, bounding_filter

THIN = "#e0623a"   # coral
THICK = "#1b3b5f"  # deep indigo

rng = np.random.default_rng(7)
gammas = rng.uniform(-0.5, 0.5, 5)
gammas -= gammas.mean() - 0.13  # keep generic (non-singular), off zero-sum

rhombi = pentagrid_rhombi(gammas, extent=9)
rhombi = bounding_filter(rhombi, 7.2)

fig, ax = plt.subplots(figsize=(11, 11))
patches_thin, patches_thick = [], []
for r in rhombi:
    poly = Polygon(r["verts"], closed=True)
    (patches_thin if r["type"] == "thin" else patches_thick).append(poly)

ax.add_collection(PatchCollection(patches_thin, facecolor=THIN, edgecolor="#1a0d08", linewidth=0.4))
ax.add_collection(PatchCollection(patches_thick, facecolor=THICK, edgecolor="#1a0d08", linewidth=0.4))

ax.set_xlim(-7.2, 7.2)
ax.set_ylim(-7.2, 7.2)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("#f4ede2")
ax.set_facecolor("#f4ede2")

plt.tight_layout(pad=0.3)
plt.savefig("01_classic.png", dpi=150, facecolor="#f4ede2")
print(f"rhombi drawn: {len(rhombi)}")

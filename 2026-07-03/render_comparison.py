"""Local isomorphism: four tilings from independently-random gammas look
globally different, yet any patch you find in one will, somewhere, also
appear in the others -- a Penrose tiling's defining aperiodic property. Also
note the same 2 tile shapes (36 deg and 72 deg rhombi) build every one of
these, just glued together differently, since the tile shapes alone don't
determine the tiling -- only the matching/gluing rule does."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

from penrose import pentagrid_rhombi, bounding_filter

THIN, THICK = "#e0623a", "#1b3b5f"
R = 4.6

fig, axes = plt.subplots(2, 2, figsize=(12, 12))

for i, ax in enumerate(axes.flat):
    rng = np.random.default_rng(100 + i)
    gammas = rng.uniform(-0.5, 0.5, 5)
    gammas -= gammas.mean() - rng.uniform(-0.2, 0.2)

    rhombi = pentagrid_rhombi(gammas, extent=7)
    rhombi = bounding_filter(rhombi, R + 0.3)

    patches_thin, patches_thick = [], []
    for r in rhombi:
        poly = Polygon(r["verts"], closed=True)
        (patches_thin if r["type"] == "thin" else patches_thick).append(poly)
    ax.add_collection(PatchCollection(patches_thin, facecolor=THIN, edgecolor="#1a0d08", linewidth=0.3))
    ax.add_collection(PatchCollection(patches_thick, facecolor=THICK, edgecolor="#1a0d08", linewidth=0.3))
    ax.set_xlim(-R, R)
    ax.set_ylim(-R, R)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"gammas seed {100+i}", fontsize=11, color="#444444")

fig.patch.set_facecolor("#f4ede2")
plt.tight_layout(pad=1.2, rect=(0, 0, 1, 0.97))
fig.suptitle("Four independent pentagrids: different tilings, same two tiles, same local motifs", fontsize=13, color="#222222")
plt.savefig("05_comparison.png", dpi=150, facecolor="#f4ede2")
print("done")

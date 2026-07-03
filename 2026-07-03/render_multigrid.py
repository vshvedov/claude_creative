"""Show the machinery: the 5 families of pentagrid lines on the left, and
the rhombus tiling they dualize into on the right, sharing the same gammas
and the same view window so the correspondence is visible."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection, LineCollection

from penrose import pentagrid_rhombi, grid_lines, bounding_filter

FAMILY_COLORS = ["#e0623a", "#2fa66f", "#3b6e8f", "#c9a227", "#8757a6"]
THIN, THICK = "#e0623a", "#1b3b5f"

rng = np.random.default_rng(7)
gammas = rng.uniform(-0.5, 0.5, 5)
gammas -= gammas.mean() - 0.13

R = 4.5
fig, axes = plt.subplots(1, 2, figsize=(18, 9))

# left: the 5 grid families
segs = grid_lines(gammas, extent=7, line_half_len=9)
by_family = {j: [] for j in range(5)}
for j, (p0, p1) in segs:
    by_family[j].append([p0, p1])

ax = axes[0]
for j in range(5):
    ax.add_collection(LineCollection(by_family[j], colors=FAMILY_COLORS[j], linewidths=1.1, alpha=0.85))
ax.set_xlim(-R, R)
ax.set_ylim(-R, R)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("5 pentagrid line families", fontsize=16, color="#222222")

# right: the dual rhombus tiling
rhombi = pentagrid_rhombi(gammas, extent=9)
rhombi = bounding_filter(rhombi, R + 0.3)
ax = axes[1]
patches_thin, patches_thick = [], []
for r in rhombi:
    poly = Polygon(r["verts"], closed=True)
    (patches_thin if r["type"] == "thin" else patches_thick).append(poly)
ax.add_collection(PatchCollection(patches_thin, facecolor=THIN, edgecolor="#1a0d08", linewidth=0.4))
ax.add_collection(PatchCollection(patches_thick, facecolor=THICK, edgecolor="#1a0d08", linewidth=0.4))
ax.set_xlim(-R, R)
ax.set_ylim(-R, R)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("its dual: a Penrose tiling", fontsize=16, color="#222222")

fig.patch.set_facecolor("#f4ede2")
plt.tight_layout(pad=1.0, rect=(0, 0, 1, 0.95))
plt.savefig("04_multigrid.png", dpi=150, facecolor="#f4ede2")
print(f"rhombi drawn: {len(rhombi)}")

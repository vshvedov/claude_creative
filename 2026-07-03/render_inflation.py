"""Render a few generations of the Robinson-triangle substitution side by
side, to make the self-similarity of inflation visible directly (unlike the
pentagrid renders, where it's true but not obvious from a single image)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

from inflation import inflate, triangles_to_xy

THIN = "#3b6e8f"
THICK = "#e0623a"
GENS = [3, 5, 7]

fig, axes = plt.subplots(1, 3, figsize=(18, 6.5))

for gen, ax in zip(GENS, axes):
    triangles = triangles_to_xy(inflate(gen))
    patches_thin, patches_thick = [], []
    for color, pts in triangles:
        poly = Polygon(pts, closed=True)
        (patches_thin if color == "thin" else patches_thick).append(poly)

    ax.add_collection(PatchCollection(patches_thin, facecolor=THIN, edgecolor="#0d1b26", linewidth=0.25))
    ax.add_collection(PatchCollection(patches_thick, facecolor=THICK, edgecolor="#2a1108", linewidth=0.25))
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"generation {gen}  ({len(triangles)} triangles)", fontsize=13, color="#222222")

fig.patch.set_facecolor("#f4ede2")
fig.suptitle("Inflation: each generation is built from scaled copies of the last", fontsize=15, color="#222222")
plt.tight_layout(pad=1.0, rect=(0, 0, 1, 0.93))
plt.savefig("06_inflation.png", dpi=150, facecolor="#f4ede2")
print("done")

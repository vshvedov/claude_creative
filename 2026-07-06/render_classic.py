"""The centerpiece: one big radial DLA cluster, colored by arrival time."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from dla import grow_radial

rng = np.random.default_rng(20260706)
pts, arrival = grow_radial(35000, stick_prob=1.0, stick_radius=1.0, rng=rng)
print(f"grew {len(pts)} particles, max radius {np.hypot(pts[:,0], pts[:,1]).max():.1f}")

fig, ax = plt.subplots(figsize=(11, 11), facecolor="black")
ax.set_facecolor("black")

order = np.argsort(arrival)
sc = ax.scatter(
    pts[order, 0], pts[order, 1],
    c=arrival[order], cmap="plasma", s=3.2, linewidths=0,
    edgecolors="none",
)
ax.set_aspect("equal")
ax.axis("off")
r = np.hypot(pts[:, 0], pts[:, 1]).max() * 1.05
ax.set_xlim(-r, r)
ax.set_ylim(-r, r)

cbar = fig.colorbar(sc, ax=ax, fraction=0.035, pad=0.02)
cbar.set_label("arrival order (particle #)", color="white")
cbar.ax.yaxis.set_tick_params(color="white")
plt.setp(plt.getp(cbar.ax, "yticklabels"), color="white")

ax.set_title(
    f"Diffusion-Limited Aggregation — {len(pts):,} particles, single seed",
    color="white", fontsize=13, pad=14,
)
plt.tight_layout()
plt.savefig("01_cluster_classic.png", dpi=170, facecolor="black")
print("saved 01_cluster_classic.png")

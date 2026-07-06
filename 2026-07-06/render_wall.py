"""DLA grown from a flat seed line instead of a point.

Same walk-and-stick rule, different geometry: particles rain down onto a
horizontal wire with periodic boundaries in x. Multiple fingers compete for
incoming particles, and the same tip-screening that shapes the radial
cluster now plays out as a race -- a finger that gets slightly ahead
shadows its neighbors from the particle rain and outgrows them, while
shorter fingers stall. The result looks like frost, coral, or a
Lichtenberg figure, and is the same physics behind real dendritic
electrodeposition.
"""
import numpy as np
import matplotlib.pyplot as plt
from dla import grow_from_wall

rng = np.random.default_rng(20260706)
width = 260
pts, arrival = grow_from_wall(26000, width=width, stick_prob=1.0, stick_radius=1.0, rng=rng)
print(f"grew {len(pts)} particles, max height {pts[:,1].max():.1f}")

fig, ax = plt.subplots(figsize=(14, 7), facecolor="black")
ax.set_facecolor("black")

order = np.argsort(arrival)
ax.scatter(pts[order, 0], pts[order, 1], c=arrival[order], cmap="cool", s=2.4, linewidths=0)
ax.set_aspect("equal")
ax.axis("off")
ax.set_xlim(-width / 2, width / 2)
ax.set_ylim(-3, pts[:, 1].max() * 1.08)
ax.set_title(
    f"DLA from a seed line — {len(pts):,} particles, periodic boundaries, tip-screening in action",
    color="white", fontsize=13, pad=12,
)

plt.tight_layout()
plt.savefig("04_wall_growth.png", dpi=170, facecolor="black")
print("saved 04_wall_growth.png")

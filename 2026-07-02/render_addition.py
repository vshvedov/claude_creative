"""Sandpile group addition: stabilize(A) + stabilize(B), then stabilize again.

A and B are two single-source piles at different points, big enough that
their footprints overlap. Literally adding the two *stable* grids can push
sites back over threshold, so the sum needs its own relaxation pass -- the
group operation is "add heights, then re-topple," not just pixel addition.
That re-relaxation is what makes the sandpile group nonabelian-looking-but-
actually-abelian structure interesting: the result is order-independent, but
not a naive overlay.
"""
import numpy as np
import matplotlib.pyplot as plt
from sandpile import stabilize, to_rgb

N = 601
GRAINS = 300_000
offset = 90

grid_a = np.zeros((N, N), dtype=np.int64)
grid_a[N // 2 - offset, N // 2] = GRAINS
a = stabilize(grid_a)

grid_b = np.zeros((N, N), dtype=np.int64)
grid_b[N // 2 + offset, N // 2] = GRAINS
b = stabilize(grid_b)

summed = stabilize(a + b)

fig, axes = plt.subplots(1, 3, figsize=(16.5, 6), facecolor="#0b0c10")
titles = ["A: pile at top", "B: pile at bottom", "stabilize(A + B)"]
for ax, grid, title in zip(axes, [a, b, summed], titles):
    ax.imshow(to_rgb(grid), interpolation="nearest")
    ax.set_facecolor("#0b0c10")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(title, color="#e8e8e8", fontsize=13)

fig.suptitle("The sandpile group: two piles, added and re-relaxed",
             color="#e8e8e8", fontsize=15, y=1.03)
fig.tight_layout()
fig.savefig("05_addition.png", dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("done")

"""Four stages of a growing sandpile, same center, increasing grain count."""
import matplotlib.pyplot as plt
from sandpile import drop_pile, to_rgb, touches_boundary

STAGES = [1_000, 10_000, 100_000, 300_000]
N = 601  # grid side; big enough to contain the N=300k pile with margin

fig, axes = plt.subplots(1, 4, figsize=(20, 5.4), facecolor="#0b0c10")

for ax, grains in zip(axes, STAGES):
    grid = drop_pile(N, grains)
    clipped = touches_boundary(grid)
    r = grid.shape[0] // 2
    # crop tightly around the nonzero region for the smaller piles so they
    # aren't a speck in a huge black square
    nz = grid.nonzero()
    if len(nz[0]):
        pad = 4
        r0, r1 = max(0, nz[0].min() - pad), min(N, nz[0].max() + pad + 1)
        c0, c1 = max(0, nz[1].min() - pad), min(N, nz[1].max() + pad + 1)
        side = max(r1 - r0, c1 - c0)
        rc, cc = (r0 + r1) // 2, (c0 + c1) // 2
        half = side // 2 + 1
        r0, r1 = max(0, rc - half), min(N, rc + half)
        c0, c1 = max(0, cc - half), min(N, cc + half)
        grid = grid[r0:r1, c0:c1]

    ax.imshow(to_rgb(grid), interpolation="nearest")
    ax.set_title(f"{grains:,} grains" + ("  (touches edge)" if clipped else ""),
                 color="#e8e8e8", fontsize=13)
    ax.set_facecolor("#0b0c10")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

fig.suptitle("One rule, run longer: the sandpile fractal emerging", color="#e8e8e8", fontsize=15, y=1.02)
fig.tight_layout()
fig.savefig("01_growth.png", dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("done")

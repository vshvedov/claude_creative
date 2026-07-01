"""02: The three coordinate-plane projections of the same Lorenz trajectory,
side by side, to make it obvious that the 'two wings' story is a 2D artifact
of the xz view -- the attractor is a single connected sheet in 3D."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flows import lorenz, integrate, colored_line

t, y = integrate(lorenz, [1.0, 1.0, 1.0], (0, 60), 60000, args=(10.0, 28.0, 8.0 / 3.0))
x, yy, z = y

views = [("x", "y", x, yy), ("x", "z", x, z), ("y", "z", yy, z)]

fig, axes = plt.subplots(1, 3, figsize=(18, 6), facecolor="black")
for ax, (lx, ly, a, b) in zip(axes, views):
    ax.set_facecolor("black")
    colored_line(ax, a, b, cmap="cividis", lw=0.3, alpha=0.85)
    ax.set_xlabel(lx, color="white")
    ax.set_ylabel(ly, color="white")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color("white")
        spine.set_alpha(0.2)

fig.tight_layout()
fig.savefig("02_projections.png", dpi=170, facecolor="black")
print("wrote 02_projections.png")

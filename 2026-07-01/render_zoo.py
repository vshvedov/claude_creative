"""06: A small zoo of other chaotic flows, each with a very different
character despite all being "three coupled autonomous nonlinear ODEs":
Chen (a Lorenz-like double scroll but more angular), Halvorsen (thin,
razor-like sheets), Aizawa (a layered, translucent-looking torus stack),
and Thomas (soft, foamy, cyclically symmetric)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flows import chen, halvorsen, aizawa, thomas, integrate, colored_line

SPECS = [
    ("Chen attractor",      chen,      [1.0, 1.0, 1.0],   (0, 60),  60000, "x", "z", "inferno"),
    ("Halvorsen attractor", halvorsen, [1.0, 0.0, 0.0],   (0, 40),  60000, "x", "y", "viridis"),
    ("Aizawa attractor",    aizawa,    [0.1, 0.0, 0.0],   (0, 200), 100000, "x", "z", "cool"),
    ("Thomas attractor",    thomas,    [0.1, 0.0, 0.0],   (0, 800), 160000, "x", "y", "spring"),
]

fig, axes = plt.subplots(2, 2, figsize=(14, 14), facecolor="black")
for ax, (name, rhs, state0, tspan, n, cx, cy, cmap) in zip(axes.flat, SPECS):
    t, y = integrate(rhs, state0, tspan, n)
    coords = {"x": y[0], "y": y[1], "z": y[2]}
    a, b = coords[cx], coords[cy]
    drop = n // 20
    ax.set_facecolor("black")
    colored_line(ax, a[drop:], b[drop:], cmap=cmap, lw=0.25, alpha=0.85)
    ax.set_title(name, color="white", fontsize=13)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color("white")
        spine.set_alpha(0.2)

fig.tight_layout()
fig.savefig("06_zoo.png", dpi=170, facecolor="black")
print("wrote 06_zoo.png")

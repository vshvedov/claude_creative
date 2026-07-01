"""01: The classic Lorenz butterfly, single high-resolution render."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flows import lorenz, integrate, colored_line

t, y = integrate(lorenz, [1.0, 1.0, 1.0], (0, 60), 60000, args=(10.0, 28.0, 8.0 / 3.0))
x, yy, z = y

fig, ax = plt.subplots(figsize=(12, 9), facecolor="black")
ax.set_facecolor("black")
colored_line(ax, x, z, cmap="plasma", lw=0.35, alpha=0.85)
ax.set_xlim(x.min() - 2, x.max() + 2)
ax.set_ylim(z.min() - 2, z.max() + 2)
ax.axis("off")
fig.tight_layout(pad=0)
fig.savefig("01_lorenz_butterfly.png", dpi=200, facecolor="black")
print("wrote 01_lorenz_butterfly.png")

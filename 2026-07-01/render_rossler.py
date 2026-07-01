"""04: The Rossler attractor -- a single spiraling band that occasionally
folds over itself, the simplest possible chaotic flow (one nonlinear term)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flows import rossler, integrate, colored_line

t, y = integrate(rossler, [1.0, 1.0, 1.0], (0, 300), 120000, args=(0.2, 0.2, 5.7))
x, yy, z = y
# drop transient
x, yy, z = x[2000:], yy[2000:], z[2000:]

fig, ax = plt.subplots(figsize=(12, 9), facecolor="black")
ax.set_facecolor("black")
colored_line(ax, x, yy, cmap="turbo", lw=0.35, alpha=0.85)
ax.set_xlim(x.min() - 1, x.max() + 1)
ax.set_ylim(yy.min() - 1, yy.max() + 1)
ax.axis("off")
fig.tight_layout(pad=0)
fig.savefig("04_rossler.png", dpi=200, facecolor="black")
print("wrote 04_rossler.png")

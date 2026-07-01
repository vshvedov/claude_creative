"""07: Standout piece -- Thomas' cyclically symmetric attractor, rendered as
a residence-time density map (log-scaled bin counts, not a line plot) from
one very long trajectory (20000 time units). Its light damping (b ~ 0.2)
makes it drift slowly and re-visit the same regions from slightly different
angles, producing this braided, translucent-ribbon look -- qualitatively
unlike the thin wire-frame renders of Lorenz/Rossler/Chen.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from flows import thomas, integrate

t, y = integrate(thomas, [0.1, 0.0, 0.0], (0, 20000), 4_000_000, args=(0.208186,))
x, yy, z = y
drop = 20000  # discard initial transient

fig, ax = plt.subplots(figsize=(12, 12), facecolor="black")
ax.set_facecolor("black")
hist, xedges, yedges = np.histogram2d(x[drop:], yy[drop:], bins=900)
ax.imshow(hist.T, origin="lower", extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
          cmap="bone", norm=LogNorm(vmin=1, vmax=hist.max()), interpolation="bilinear")
ax.set_aspect("equal")
ax.axis("off")
fig.tight_layout(pad=0)
fig.savefig("07_thomas_standout.png", dpi=200, facecolor="black")
print("wrote 07_thomas_standout.png")

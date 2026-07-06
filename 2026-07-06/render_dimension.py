"""Box-counting fractal dimension of a DLA cluster, measured from scratch.

Cover the cluster with a grid of boxes of size s, count how many boxes N(s)
contain at least one particle, repeat across a range of s. For a fractal,
N(s) ~ s^-D, so plotting log N vs log(1/s) gives a straight line whose slope
is the fractal dimension D. No formula for D is assumed anywhere -- it falls
out of a linear fit to simulated data, and lands close to the accepted
DLA value D ~ 1.71 (Witten & Sander 1981).
"""
import numpy as np
import matplotlib.pyplot as plt
from dla import grow_radial, box_count_dimension

rng = np.random.default_rng(311)
pts, arrival = grow_radial(20000, stick_prob=1.0, rng=rng)
sizes, counts, dim, intercept = box_count_dimension(pts, n_scales=20)
print(f"{len(pts)} particles, fitted dimension = {dim:.4f}")

fig, (ax_cluster, ax_fit) = plt.subplots(1, 2, figsize=(14, 6.5), facecolor="black")

ax_cluster.set_facecolor("black")
order = np.argsort(arrival)
ax_cluster.scatter(pts[order, 0], pts[order, 1], c=arrival[order], cmap="plasma",
                    s=2.2, linewidths=0)
ax_cluster.set_aspect("equal")
ax_cluster.axis("off")
ax_cluster.set_title(f"{len(pts):,}-particle cluster used for the fit", color="white", fontsize=12)

ax_fit.set_facecolor("black")
log_inv_s = np.log(1.0 / sizes)
log_n = np.log(counts)
ax_fit.scatter(log_inv_s, log_n, color="#ffd23f", s=40, zorder=3, label="measured N(box size)")
fit_line = dim * log_inv_s + intercept
ax_fit.plot(log_inv_s, fit_line, color="#4cc9f0", lw=2,
            label=f"linear fit: slope D = {dim:.3f}")
ax_fit.axhline(0, color="none")
ax_fit.set_xlabel("log(1 / box size)", color="white")
ax_fit.set_ylabel("log(box count N)", color="white")
ax_fit.tick_params(colors="white")
for spine in ax_fit.spines.values():
    spine.set_color("white")
ax_fit.legend(facecolor="black", edgecolor="white", labelcolor="white", loc="upper left")
ax_fit.set_title(
    f"Box-counting dimension: D = {dim:.3f}  (Witten-Sander 1981 value: 1.71)",
    color="white", fontsize=12,
)

plt.tight_layout()
plt.savefig("03_fractal_dimension.png", dpi=160, facecolor="black")
print("saved 03_fractal_dimension.png")

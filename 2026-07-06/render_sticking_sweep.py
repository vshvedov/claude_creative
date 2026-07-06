"""Sticking-probability sweep: same particle budget, four morphologies.

Counter-intuitive result (well documented in the DLA literature, reproduced
here from scratch): LOWER sticking probability does not make the cluster
sparser. A particle that fails to stick on contact just bounces and keeps
wandering nearby, so it has many more chances to find its way into the deep
fjords between existing branches before finally sticking. High sticking
probability freezes it onto the first branch tip it touches instead
(tip-screening). So p: 1.0 -> 0.02 sweeps from sparse dendritic fractal
towards a dense, round, Eden-model-like blob.
"""
import numpy as np
import matplotlib.pyplot as plt
from dla import grow_radial, box_count_dimension

probs = [1.0, 0.5, 0.15, 0.03]
n_attempt = 9000
seed = 20260706

fig, axes = plt.subplots(1, 4, figsize=(20, 5.5), facecolor="black")

for ax, p in zip(axes, probs):
    rng = np.random.default_rng(seed)
    pts, arrival = grow_radial(n_attempt, stick_prob=p, stick_radius=1.0, rng=rng)
    _, _, dim, _ = box_count_dimension(pts, r_min_factor=0.03, r_max_factor=0.5)

    ax.set_facecolor("black")
    order = np.argsort(arrival)
    ax.scatter(pts[order, 0], pts[order, 1], c=arrival[order], cmap="plasma",
               s=2.6, linewidths=0)
    ax.set_aspect("equal")
    ax.axis("off")
    r = np.hypot(pts[:, 0], pts[:, 1]).max() * 1.08
    ax.set_xlim(-r, r)
    ax.set_ylim(-r, r)
    ax.set_title(f"p = {p}\n{len(pts):,} stuck, dim ~ {dim:.2f}", color="white", fontsize=12)
    print(f"p={p}: stuck={len(pts)} dim={dim:.3f}")

fig.suptitle(
    "Sticking probability sweep — same 9,000-particle budget each panel",
    color="white", fontsize=15, y=1.03,
)
plt.tight_layout()
plt.savefig("02_sticking_probability_sweep.png", dpi=160, facecolor="black", bbox_inches="tight")
print("saved 02_sticking_probability_sweep.png")

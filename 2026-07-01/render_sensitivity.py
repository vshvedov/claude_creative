"""03: Sensitive dependence on initial conditions -- the actual content of
'the butterfly effect', which the shape of the attractor only gestures at.
Two Lorenz trajectories start 1e-8 apart in x. Left: they're visually
identical for a while, then diverge and end up on unrelated loops. Right:
log-separation vs time is linear (exponential growth) until it saturates at
the attractor's diameter -- the slope of the straight part is the largest
Lyapunov exponent.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flows import lorenz, integrate

EPS = 1e-8
T_END = 40
N = 40000

t, y1 = integrate(lorenz, [1.0, 1.0, 1.0], (0, T_END), N)
_, y2 = integrate(lorenz, [1.0 + EPS, 1.0, 1.0], (0, T_END), N)

sep = np.sqrt(((y1 - y2) ** 2).sum(axis=0))

# crude Lyapunov estimate: fit log(sep) vs t over the exponential-growth
# window, i.e. before it saturates near the attractor's own scale.
sat_level = sep.max() * 0.3
mask = (sep > 3 * EPS) & (sep < sat_level)
if mask.sum() > 10:
    slope, intercept = np.polyfit(t[mask], np.log(sep[mask]), 1)
else:
    slope = float("nan")

fig, axes = plt.subplot_mosaic([["a", "a", "b"], ["a", "a", "b"]],
                                figsize=(16, 7), facecolor="black")

ax = axes["a"]
ax.set_facecolor("black")
ax.plot(t, y1[0], color="#37c8ff", lw=0.8, label="run A (x0 = 1.0)")
ax.plot(t, y2[0], color="#ff5f56", lw=0.8, label="run B (x0 = 1.0 + 1e-8)")
ax.set_xlabel("t", color="white")
ax.set_ylabel("x(t)", color="white")
ax.set_title("Two trajectories, 1e-8 apart at t=0", color="white")
ax.tick_params(colors="white")
leg = ax.legend(facecolor="black", labelcolor="white", framealpha=0.3)
for spine in ax.spines.values():
    spine.set_color("white")
    spine.set_alpha(0.3)

axb = axes["b"]
axb.set_facecolor("black")
axb.semilogy(t, sep, color="#f5d76e", lw=1.2)
if not np.isnan(slope):
    fit_t = t[mask]
    axb.semilogy(fit_t, np.exp(intercept + slope * fit_t), "--",
                 color="white", lw=1.5,
                 label=f"fit: lambda ~ {slope:.3f} / time unit")
    axb.legend(facecolor="black", labelcolor="white", framealpha=0.3, loc="lower right")
axb.set_xlabel("t", color="white")
axb.set_ylabel("|separation|", color="white")
axb.set_title("Divergence of the two trajectories", color="white")
axb.tick_params(colors="white")
for spine in axb.spines.values():
    spine.set_color("white")
    spine.set_alpha(0.3)

fig.tight_layout()
fig.savefig("03_sensitivity.png", dpi=170, facecolor="black")
print(f"wrote 03_sensitivity.png  (fitted Lyapunov exponent ~ {slope:.4f})")

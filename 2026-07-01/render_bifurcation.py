"""05: Lorenz's rho parameter is the one that Lorenz himself varied (it's
proportional to the Rayleigh number in his convection-roll model). Sweeping
it walks through the whole story: a stable resting state, a stable
convecting state, transient chaos before the fixed points even lose
stability, the classic butterfly, and periodic windows hiding inside the
chaos at large rho. sigma and beta are held at Lorenz's original values.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flows import lorenz, integrate, colored_line

RHOS = [0.5, 5, 10, 13.93, 15, 20, 24.06, 24.74, 28, 100.5, 160, 350]
LABELS = [
    "rho=0.5  (origin is the only, stable, fixed point)",
    "rho=5    (still relaxes straight to the origin)",
    "rho=10   (two new fixed points appear at rho=1; stable, no overshoot)",
    "rho=13.93 (homoclinic explosion: chaotic transients begin)",
    "rho=15   (spirals into a fixed point, but takes a detour first)",
    "rho=20   (longer chaotic transient before settling)",
    "rho=24.06 (right at the edge -- barely settles)",
    "rho=24.74 (Hopf bifurcation: fixed points just went unstable)",
    "rho=28   (the classic butterfly -- permanently chaotic)",
    "rho=100.5 (a periodic window: a clean period-2 loop)",
    "rho=160  (still periodic, now a longer-period loop)",
    "rho=350  (periodic again, simpler still)",
]

fig, axes = plt.subplots(3, 4, figsize=(20, 14), facecolor="black")
for ax, rho, label in zip(axes.flat, RHOS, LABELS):
    t, y = integrate(lorenz, [1.0, 1.0, 1.0], (0, 60), 30000, args=(10.0, rho, 8.0 / 3.0))
    x, yy, z = y
    keep = t > 15  # drop initial transient so steady behaviour dominates the view
    ax.set_facecolor("black")
    colored_line(ax, x[keep], z[keep], cmap="magma", lw=0.3, alpha=0.9)
    ax.set_title(label, color="white", fontsize=9)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color("white")
        spine.set_alpha(0.2)

fig.suptitle("Lorenz system: one route through order, transient chaos, and permanent chaos, "
             "found just by turning the rho knob", color="white", fontsize=14)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig("05_bifurcation_rho.png", dpi=150, facecolor="black")
print("wrote 05_bifurcation_rho.png")

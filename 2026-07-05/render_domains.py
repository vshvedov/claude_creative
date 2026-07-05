"""Snapshot gallery: equilibrium spin configurations across a range of
temperatures, from deeply ordered to deeply disordered, straddling Tc."""
import numpy as np
import matplotlib.pyplot as plt
from ising import random_state, equilibrate, TC_ONSAGER

L = 200
N_EQ = 800
temps = [0.5, 1.5, 2.1, TC_ONSAGER, 2.4, 3.0]

fig, axes = plt.subplots(2, 3, figsize=(13.5, 9.2))
for ax, T in zip(axes.flat, temps):
    rng = np.random.default_rng(int(T * 1000) + 7)
    spins = random_state(L, rng)
    equilibrate(spins, T, rng, N_EQ)
    ax.imshow(spins, cmap="Greys", vmin=-1, vmax=1, interpolation="nearest")
    label = "Tc" if abs(T - TC_ONSAGER) < 1e-6 else f"T={T:.2f}"
    ax.set_title(f"{label}  (T/Tc = {T/TC_ONSAGER:.2f})", fontsize=12)
    ax.set_xticks([])
    ax.set_yticks([])

fig.suptitle(
    "2D Ising model: equilibrium domains across the phase transition\n"
    f"({L}x{L} lattice, {N_EQ} Metropolis sweeps, Onsager Tc = {TC_ONSAGER:.4f})",
    fontsize=13,
)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig("01_domains.png", dpi=130)
print("wrote 01_domains.png")

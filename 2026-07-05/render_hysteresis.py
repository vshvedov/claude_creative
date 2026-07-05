"""Hysteresis loop: sweep an external field h up and down at fixed T < Tc
and watch the magnetization lag behind it — the signature of ferromagnetic
memory. Above Tc the loop should collapse to a single reversible curve;
below Tc it opens up into the classic loop shape."""
import numpy as np
import matplotlib.pyplot as plt
from ising import random_state, sweep, magnetization

L = 64
N_SETTLE = 30
H_MAX = 1.2
N_STEPS = 60

h_path = np.concatenate([
    np.linspace(0, H_MAX, N_STEPS),
    np.linspace(H_MAX, -H_MAX, 2 * N_STEPS),
    np.linspace(-H_MAX, H_MAX, 2 * N_STEPS),
])


def run_loop(T, seed):
    rng = np.random.default_rng(seed)
    spins = random_state(L, rng, magnetized=True)
    ms = []
    for h in h_path:
        for _ in range(N_SETTLE):
            sweep(spins, T, rng, h=h)
        ms.append(magnetization(spins))
    return np.array(ms)


fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.2))

for ax, T, label, color in [
    (axes[0], 1.5, "T = 1.5  (< Tc, ferromagnetic)", "#c0392b"),
    (axes[1], 3.2, "T = 3.2  (> Tc, paramagnetic)", "#1f5fa8"),
]:
    ms = run_loop(T, seed=int(T * 100))
    ax.plot(h_path, ms, color=color, lw=1.3)
    ax.axhline(0, color="gray", lw=0.6)
    ax.axvline(0, color="gray", lw=0.6)
    ax.set_xlabel("external field h")
    ax.set_ylabel("magnetization m")
    ax.set_title(label, fontsize=11)
    ax.set_ylim(-1.05, 1.05)

fig.suptitle(
    f"Ferromagnetic hysteresis: {L}x{L} Ising lattice under an oscillating field\n"
    "below Tc the spins resist flipping and the loop opens up; above Tc the response is reversible",
    fontsize=12,
)
fig.tight_layout(rect=[0, 0, 1, 0.88])
fig.savefig("04_hysteresis.png", dpi=130)
print("wrote 04_hysteresis.png")

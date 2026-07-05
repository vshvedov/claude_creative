"""Domain coarsening: quench a random (T=infinity) start down to T well
below Tc and watch ferromagnetic domains grow and coalesce over time.
This is a classic non-equilibrium phenomenon (Ostwald ripening / Ising
coarsening), distinct from the equilibrium snapshots in image 1."""
import numpy as np
import matplotlib.pyplot as plt
from ising import random_state, sweep, TC_ONSAGER

L = 220
T_QUENCH = 1.5  # well below Tc ~ 2.269
checkpoints = [0, 2, 8, 32, 128, 512]

rng = np.random.default_rng(42)
spins = random_state(L, rng)

fig, axes = plt.subplots(1, len(checkpoints), figsize=(3.1 * len(checkpoints), 3.6))
done = 0
for ax, target in zip(axes, checkpoints):
    while done < target:
        sweep(spins, T_QUENCH, rng)
        done += 1
    ax.imshow(spins, cmap="Greys", vmin=-1, vmax=1, interpolation="nearest")
    ax.set_title(f"t = {target} sweeps", fontsize=11)
    ax.set_xticks([])
    ax.set_yticks([])

fig.suptitle(
    f"Domain coarsening after a quench to T={T_QUENCH} (Tc = {TC_ONSAGER:.3f}), {L}x{L} lattice\n"
    "random initial condition -> growing domains competing for territory, never fully finishing within finite time",
    fontsize=12,
)
fig.tight_layout(rect=[0, 0, 1, 0.88])
fig.savefig("03_coarsening.png", dpi=130)
print("wrote 03_coarsening.png")

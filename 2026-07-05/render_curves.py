"""Magnetization, specific heat and susceptibility vs temperature.

For each T we equilibrate, then sample the system every few sweeps to
estimate thermal averages. C and chi come from the fluctuation-dissipation
theorem: C = (<E^2> - <E>^2) / T^2,  chi = N*(<M^2> - <M>^2) / T
(computed here per-site, so the N is folded into using per-site m, e and
multiplying the variance by L^2 for chi to keep it an extensive-looking
susceptibility curve that still peaks cleanly at Tc).
"""
import numpy as np
import matplotlib.pyplot as plt
from ising import random_state, sweep, magnetization, energy_per_site, TC_ONSAGER

L = 48
N_EQ = 600
N_SAMPLE = 600
SAMPLE_EVERY = 4

temps = np.concatenate([
    np.linspace(1.0, 2.0, 8),
    np.linspace(2.0, 2.6, 20),
    np.linspace(2.6, 3.6, 8),
])

mean_absM, mean_E, varM, varE = [], [], [], []

for T in temps:
    rng = np.random.default_rng(hash(("ising", round(T, 4))) % (2**32))
    spins = random_state(L, rng)
    for _ in range(N_EQ):
        sweep(spins, T, rng)
    ms, es = [], []
    for i in range(N_SAMPLE):
        sweep(spins, T, rng)
        if i % SAMPLE_EVERY == 0:
            ms.append(magnetization(spins))
            es.append(energy_per_site(spins))
    ms, es = np.array(ms), np.array(es)
    mean_absM.append(np.mean(np.abs(ms)))
    mean_E.append(np.mean(es))
    varM.append(np.var(ms))
    varE.append(np.var(es))

mean_absM = np.array(mean_absM)
varM = np.array(varM)
varE = np.array(varE)
N = L * L
specific_heat = N * varE / temps**2
susceptibility = N * varM / temps

# Onsager's exact spontaneous magnetization for T < Tc:
# m(T) = (1 - sinh(2/T)^-4)^(1/8), 0 above Tc.
with np.errstate(invalid="ignore"):
    sinh_term = np.sinh(2.0 / temps) ** -4
    onsager_m = np.where(temps < TC_ONSAGER, (1 - sinh_term) ** 0.125, 0.0)
    onsager_m = np.nan_to_num(onsager_m)

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

ax = axes[0]
ax.plot(temps, mean_absM, "o-", ms=4, color="#1f5fa8", label=f"simulated, L={L}")
ax.plot(temps, onsager_m, "--", color="#c0392b", label="Onsager exact (L=inf)")
ax.axvline(TC_ONSAGER, color="gray", ls=":", lw=1)
ax.set_xlabel("T")
ax.set_ylabel("|m|")
ax.set_title("Magnetization")
ax.legend(fontsize=9)

ax = axes[1]
ax.plot(temps, specific_heat, "o-", ms=4, color="#2e8b57")
ax.axvline(TC_ONSAGER, color="gray", ls=":", lw=1)
ax.set_xlabel("T")
ax.set_ylabel("C(T)")
ax.set_title("Specific heat")

ax = axes[2]
ax.plot(temps, susceptibility, "o-", ms=4, color="#8e44ad")
ax.axvline(TC_ONSAGER, color="gray", ls=":", lw=1, label=f"Tc = {TC_ONSAGER:.3f}")
ax.set_xlabel("T")
ax.set_ylabel("chi(T)")
ax.set_title("Susceptibility")
ax.legend(fontsize=9)

fig.suptitle(
    f"Thermodynamics of the 2D Ising model ({L}x{L}, periodic BC) — "
    "both C and chi peak right at the critical point", fontsize=13
)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig("02_magnetization_and_response.png", dpi=130)
print("wrote 02_magnetization_and_response.png")

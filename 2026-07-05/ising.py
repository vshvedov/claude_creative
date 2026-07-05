"""
2D Ising model on a periodic square lattice, simulated with the Metropolis
algorithm using a checkerboard (red-black) update: the lattice splits into
two sublattices such that every neighbor of a site on sublattice A lies on
sublattice B, so all of A can be updated simultaneously with vectorized
numpy ops, then all of B. This is the standard trick that turns an
otherwise O(L^2) Python loop per sweep into a handful of array operations.

Hamiltonian: H = -J * sum_{<i,j>} s_i s_j - h * sum_i s_i,  s_i = +-1.
Ferromagnetic coupling J=1 throughout (favors aligned neighbors).
Onsager's exact critical temperature for J=1, k_B=1: Tc = 2/ln(1+sqrt(2)).
"""
import numpy as np

J = 1.0
TC_ONSAGER = 2.0 / np.log(1.0 + np.sqrt(2.0))  # ~2.269

_CHECKER = None
_CHECKER_SHAPE = None


def _checkerboard(shape):
    global _CHECKER, _CHECKER_SHAPE
    if _CHECKER_SHAPE != shape:
        ii, jj = np.indices(shape)
        _CHECKER = (ii + jj) % 2 == 0
        _CHECKER_SHAPE = shape
    return _CHECKER


def random_state(L, rng, magnetized=False):
    if magnetized:
        return np.ones((L, L))
    return rng.choice([-1.0, 1.0], size=(L, L))


def neighbor_sum(spins):
    return (
        np.roll(spins, 1, axis=0) + np.roll(spins, -1, axis=0)
        + np.roll(spins, 1, axis=1) + np.roll(spins, -1, axis=1)
    )


def sweep(spins, T, rng, h=0.0):
    """One full Metropolis sweep (both checkerboard colors), in place."""
    L = spins.shape[0]
    even = _checkerboard((L, L))
    for mask in (even, ~even):
        nsum = neighbor_sum(spins)
        dE = 2.0 * spins * (J * nsum + h)
        accept = (dE <= 0) | (rng.random((L, L)) < np.exp(-np.clip(dE, 0, None) / T))
        flip = mask & accept
        spins[flip] *= -1.0
    return spins


def equilibrate(spins, T, rng, n_sweeps, h=0.0):
    for _ in range(n_sweeps):
        sweep(spins, T, rng, h=h)
    return spins


def magnetization(spins):
    return spins.mean()


def energy_per_site(spins, h=0.0):
    L = spins.shape[0]
    nsum = neighbor_sum(spins)
    total = -J * 0.5 * np.sum(spins * nsum) - h * np.sum(spins)
    return total / (L * L)

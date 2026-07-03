"""
Penrose rhombus tilings via de Bruijn's pentagrid ("multigrid") method.

The idea: take 5 families of parallel lines, one family for each 5th root of
unity direction, each family offset by some real gamma_j. Every pair of
lines from two different families crosses at a point; dualizing each
crossing (line intersection -> rhombus) produces a tiling of the plane by
two rhombus shapes (36 degrees "thin" and 72 degrees "thick") that never
repeats periodically -- a Penrose tiling.

Reference construction: N.G. de Bruijn, "Algebraic theory of Penrose's
non-periodic tilings of the plane", 1981.
"""
import numpy as np


def pentagrid_rhombi(gammas, extent=6):
    """Generate Penrose rhombi from a pentagrid.

    gammas: 5 real offsets, one per grid family (index j = 0..4).
    extent: how many lines out from the origin to consider per family
        (controls how much of the plane gets covered).

    Returns a list of dicts: {"verts": (4,2) array, "type": "thin"|"thick",
    "families": (j, k)} describing each rhombus.
    """
    gammas = np.asarray(gammas, dtype=float)
    assert len(gammas) == 5

    angles = 2 * np.pi * np.arange(5) / 5
    e = np.stack([np.cos(angles), np.sin(angles)], axis=1)  # (5,2) unit vectors

    rhombi = []
    ns = np.arange(-extent, extent + 1)

    for j in range(5):
        for k in range(j + 1, 5):
            # Solve for intersection of line n_j (family j) and n_k (family k):
            #   x . e_j = n_j - gamma_j
            #   x . e_k = n_k - gamma_k
            M = np.array([e[j], e[k]])
            Minv = np.linalg.inv(M)

            for n_j in ns:
                for n_k in ns:
                    b = np.array([n_j - gammas[j], n_k - gammas[k]])
                    x = Minv @ b

                    # Index of x within each of the 5 families.
                    KL = np.ceil(x @ e.T + gammas)
                    KL[j] = n_j
                    KL[k] = n_k

                    # The 4 vertices of the rhombus come from the 4 ways of
                    # nudging the two "active" indices (n_j, n_k) between
                    # their floor/ceil choice at this crossing.
                    verts = []
                    for dj, dk in [(0, 0), (1, 0), (1, 1), (0, 1)]:
                        KL2 = KL.copy()
                        KL2[j] = n_j + dj
                        KL2[k] = n_k + dk
                        verts.append(KL2 @ e)
                    verts = np.array(verts)

                    # angular separation of one grid step is 72 degrees, which
                    # is the *acute* angle of the "thick" (72/108) rhombus;
                    # two grid steps (144 degrees) is the acute angle's
                    # supplement, i.e. the "thin" (36/144) rhombus's obtuse angle.
                    diff = (k - j) % 5
                    rtype = "thick" if diff in (1, 4) else "thin"
                    rhombi.append({"verts": verts, "type": rtype, "families": (j, k)})

    return rhombi


def grid_lines(gammas, extent=6, line_half_len=8.0):
    """Return line segments for each of the 5 pentagrid families, for
    visualizing the multigrid that generates the tiling."""
    gammas = np.asarray(gammas, dtype=float)
    angles = 2 * np.pi * np.arange(5) / 5
    e = np.stack([np.cos(angles), np.sin(angles)], axis=1)
    perp = np.stack([-np.sin(angles), np.cos(angles)], axis=1)

    segments = []  # list of (family_index, (p0, p1))
    for j in range(5):
        for n in range(-extent, extent + 1):
            # point on the line closest to origin: (n - gamma_j) * e_j
            c = (n - gammas[j]) * e[j]
            p0 = c - line_half_len * perp[j]
            p1 = c + line_half_len * perp[j]
            segments.append((j, (p0, p1)))
    return segments


def bounding_filter(rhombi, radius):
    """Keep only rhombi whose centroid lies within `radius` of the origin."""
    out = []
    for r in rhombi:
        c = r["verts"].mean(axis=0)
        if np.hypot(*c) <= radius:
            out.append(r)
    return out

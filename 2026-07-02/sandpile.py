"""Shared bits for Abelian sandpile (chip-firing) renders.

Model: Z^2 grid, threshold 4. A site with >=4 grains topples, sending one
grain to each of its up/down/left/right neighbors; grains that would leave
the grid are lost to an implicit sink. Because the model is "abelian", the
final stable configuration doesn't depend on the order grains are added or
toppled in -- so we can dump an entire pile at a site in one shot (grid[i,j]
= N) and just relax the whole grid to stability in one call, instead of
adding grains one at a time.
"""

import numpy as np

CMAP4 = ["#0b0c10", "#0f9b8e", "#c724b1", "#f2b134"]  # heights 0,1,2,3


def stabilize(grid, track_topples=False):
    """Relax `grid` to a stable configuration (all values < 4) in place.

    Uses batched toppling: every site above threshold fires `grid // 4`
    times at once, distributing to neighbors via shifted arrays. Sites that
    would send grain off the edge just lose it -- that's the boundary sink.

    This is an explicit diffusion-like update, so the avalanche's outer edge
    only advances ~1 cell per while-loop pass: reaching radius R takes O(R^2)
    passes. To keep each pass cheap while the pile is still small, every
    array op below is restricted to a shrink-wrapped bounding box around the
    active region (grown by 1 cell whenever activity touches its edge)
    instead of the full grid -- so early passes, when the pile is tiny, are
    correspondingly tiny too.

    Returns the (mutated) grid, and optionally a same-shape array counting
    how many times each site fired.
    """
    grid = grid.astype(np.int64)
    counts = np.zeros_like(grid) if track_topples else None
    h, w = grid.shape

    nz = grid.nonzero()
    if not len(nz[0]):
        return (grid, counts) if track_topples else grid
    r0, r1 = int(nz[0].min()), int(nz[0].max()) + 1
    c0, c1 = int(nz[1].min()), int(nz[1].max()) + 1

    while True:
        box = grid[r0:r1, c0:c1]
        fires = box // 4
        if not fires.any():
            break
        if track_topples:
            counts[r0:r1, c0:c1] += fires
        box -= 4 * fires

        north = np.zeros_like(fires)
        south = np.zeros_like(fires)
        east = np.zeros_like(fires)
        west = np.zeros_like(fires)
        north[:-1, :] = fires[1:, :]
        south[1:, :] = fires[:-1, :]
        east[:, :-1] = fires[:, 1:]
        west[:, 1:] = fires[:, :-1]
        box += north + south + east + west

        # spill onto the grid's outer neighbors (one cell outside the box)
        if r0 > 0:
            grid[r0 - 1, c0:c1] += fires[0, :]
        if r1 < h:
            grid[r1, c0:c1] += fires[-1, :]
        if c0 > 0:
            grid[r0:r1, c0 - 1] += fires[:, 0]
        if c1 < w:
            grid[r0:r1, c1] += fires[:, -1]

        # grow the bounding box if activity reached its edge
        if r0 > 0 and fires[0, :].any():
            r0 -= 1
        if r1 < h and fires[-1, :].any():
            r1 += 1
        if c0 > 0 and fires[:, 0].any():
            c0 -= 1
        if c1 < w and fires[:, -1].any():
            c1 += 1

    if track_topples:
        return grid, counts
    return grid


def drop_pile(n, grains, center=None):
    """n x n grid, `grains` chips dropped at `center` (default: middle), stabilized."""
    grid = np.zeros((n, n), dtype=np.int64)
    if center is None:
        center = (n // 2, n // 2)
    grid[center] = grains
    return stabilize(grid)


def to_rgb(grid, cmap=CMAP4):
    """Map integer heights 0..3 (clipped) to an RGB image using cmap."""
    import matplotlib.colors as mcolors

    colors = np.array([mcolors.to_rgb(c) for c in cmap])
    idx = np.clip(grid, 0, len(cmap) - 1)
    return colors[idx]


def apply_laplacian(x):
    """(L x)_v = 4 x_v - sum of x over grid neighbors of v (zero outside grid).

    This is exactly the linear part of one toppling step: firing site v
    subtracts (L e_v) from the configuration. So a vector is in the "same
    sandpile-group element" as 0 exactly when it's L @ (some integer
    vector) -- which is how compute_identity below constructs a valid seed.
    """
    north = np.zeros_like(x)
    south = np.zeros_like(x)
    east = np.zeros_like(x)
    west = np.zeros_like(x)
    north[:-1, :] = x[1:, :]
    south[1:, :] = x[:-1, :]
    east[:, :-1] = x[:, 1:]
    west[:, 1:] = x[:, :-1]
    return 4 * x - (north + south + east + west)


def compute_identity(n, target=7.0):
    """The identity element of the sandpile group on an n x n grid, exactly.

    Doubling the maximal stable configuration (stabilize(2 * c_max)) is
    recurrent but is *not* generally idempotent -- verified against a
    brute-force group computation on a 3x3 grid, where it differs from the
    true identity at the center cell. The correct construction: find an
    integer vector y with L @ y >= 3 everywhere (solved via conjugate
    gradient on the matrix-free operator `apply_laplacian`, then rounded to
    integers), so that seed = L @ y lands exactly in the sandpile group's
    identity coset (seed == 0, mod L) while also being large enough
    everywhere to guarantee stabilize(seed) is recurrent. stabilize(seed)
    is then provably both recurrent and in the zero coset, which makes it
    the identity.
    """
    import scipy.sparse.linalg as spla

    shape = (n, n)
    N = n * n

    def matvec(flat):
        return apply_laplacian(flat.reshape(shape)).reshape(-1).astype(float)

    op = spla.LinearOperator((N, N), matvec=matvec, dtype=float)
    y, info = spla.cg(op, np.full(N, target), rtol=1e-12, maxiter=10 * N)
    if info != 0:
        raise RuntimeError(f"conjugate gradient did not converge (info={info})")

    y_int = np.round(y).reshape(shape).astype(np.int64)
    seed = apply_laplacian(y_int)
    if seed.min() < 3:
        raise RuntimeError(f"seed too small ({seed.min()}), raise `target`")

    return stabilize(seed)


def touches_boundary(grid):
    """True if any grain reached the outer ring (avalanche may be clipped)."""
    return bool(grid[0, :].any() or grid[-1, :].any() or grid[:, 0].any() or grid[:, -1].any())

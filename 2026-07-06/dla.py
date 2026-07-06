"""
Off-lattice diffusion-limited aggregation (DLA).

The rule: release a particle far from a growing cluster, let it random-walk
(Brownian motion) until it bumps into the cluster and sticks, permanently, at
the point of contact. Repeat with thousands of particles. That's it — no
branching rule, no fractal formula, nothing about "dendrites" anywhere in the
code. The fractal, self-similar, tip-screened tree shape is a *consequence*
of the walk, not an input to it.

Two spatial arrangements are implemented, both sharing the same walk/stick
machinery:

  - grow_radial: a single seed point at the origin, particles launched on a
    shrinking-then-regrown circle around the cluster. Produces the classic
    radially-symmetric "Brownian tree" / lightning-bolt look.

  - grow_from_wall: a horizontal seed line, particles rain down from above
    with periodic boundary conditions in x. Produces competing upward
    fingers ("frost on a wire") and makes the tip-screening effect -- front
    fingers starve the ones behind them of particles -- visually obvious.

Performance notes (this is plain Python + numpy, no numba/cython):
  - Particles far from the cluster take adaptively large steps: since the
    cluster is entirely contained in a disk of radius R around the origin,
    a walker at distance d > R can safely jump anywhere up to (d - R) in a
    random direction without any chance of tunnelling through the cluster.
    This collapses what would be a slow random walk across empty space into
    O(log d) steps.
  - Once within a few stick-radii of the cluster, we fall back to small
    fixed-size steps and do real nearest-neighbor queries against a uniform
    spatial hash grid (cell size = stick radius), checking only the point's
    own cell and its 8 neighbors.
"""

import numpy as np


class SpatialHash:
    """Uniform grid for approximate nearest-neighbor queries on a growing point set."""

    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.cells = {}
        self.points = []

    def _key(self, x, y):
        return (int(np.floor(x / self.cell_size)), int(np.floor(y / self.cell_size)))

    def insert(self, x, y):
        idx = len(self.points)
        self.points.append((x, y))
        self.cells.setdefault(self._key(x, y), []).append(idx)
        return idx

    def nearest_dist(self, x, y):
        """Distance from (x, y) to the nearest inserted point (searches 3x3 cells)."""
        cx, cy = self._key(x, y)
        best = np.inf
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for idx in self.cells.get((cx + dx, cy + dy), ()):
                    px, py = self.points[idx]
                    d = np.hypot(px - x, py - y)
                    if d < best:
                        best = d
        return best


def grow_radial(n_particles, stick_prob=1.0, stick_radius=1.0, rng=None,
                 launch_margin=8.0, kill_factor=3.0, max_steps=200_000):
    """Grow a DLA cluster from a single seed at the origin.

    Returns (points[N,2] float array, arrival_time[N] int array) including
    the seed as point 0 at time 0.
    """
    if rng is None:
        rng = np.random.default_rng()

    grid = SpatialHash(cell_size=stick_radius)
    grid.insert(0.0, 0.0)
    points = [(0.0, 0.0)]
    arrival = [0]
    r_max = stick_radius  # radius of the disk guaranteed to contain the cluster

    close_step = stick_radius * 0.9

    for n in range(1, n_particles + 1):
        theta = rng.uniform(0, 2 * np.pi)
        launch_r = r_max + launch_margin
        x, y = launch_r * np.cos(theta), launch_r * np.sin(theta)
        kill_r = launch_r * kill_factor

        for _ in range(max_steps):
            d_center = np.hypot(x, y)
            if d_center > kill_r:
                break  # escaped -- give up and relaunch a fresh particle

            gap = d_center - r_max
            if gap > close_step:
                # far from the cluster: jump freely up to `gap` in a random
                # direction, guaranteed not to skip past the cluster
                step = rng.uniform(0.0, gap)
                phi = rng.uniform(0, 2 * np.pi)
                x += step * np.cos(phi)
                y += step * np.sin(phi)
                continue

            # close to the cluster: small step, then a real distance check
            phi = rng.uniform(0, 2 * np.pi)
            nx, ny = x + close_step * np.cos(phi), y + close_step * np.sin(phi)
            dist = grid.nearest_dist(nx, ny)
            if dist < stick_radius:
                if rng.uniform() < stick_prob:
                    grid.insert(nx, ny)
                    points.append((nx, ny))
                    arrival.append(n)
                    r = np.hypot(nx, ny)
                    if r > r_max:
                        r_max = r
                    break
                # didn't stick this time -- bounce off, stay put, try again
                continue
            x, y = nx, ny
        # if max_steps exhausted or escaped, particle is simply dropped

    return np.array(points), np.array(arrival)


def grow_from_wall(n_particles, width, stick_prob=1.0, stick_radius=1.0, rng=None,
                    launch_margin=8.0, max_steps=200_000, seed_spacing=None):
    """Grow a DLA deposit from a horizontal seed line y=0, x in [-width/2, width/2],
    with periodic boundary conditions in x. Particles rain down from above.

    Returns (points[N,2], arrival_time[N]) including the seed points at time 0.
    """
    if rng is None:
        rng = np.random.default_rng()
    if seed_spacing is None:
        seed_spacing = stick_radius * 0.9

    grid = SpatialHash(cell_size=stick_radius)
    points = []
    arrival = []
    n_seed = int(width / seed_spacing) + 1
    for i in range(n_seed):
        sx = -width / 2 + i * seed_spacing
        grid.insert(sx, 0.0)
        points.append((sx, 0.0))
        arrival.append(0)

    h_max = 0.0
    close_step = stick_radius * 0.9

    def wrap(x):
        return (x + width / 2) % width - width / 2

    for n in range(1, n_particles + 1):
        x = rng.uniform(-width / 2, width / 2)
        y = h_max + launch_margin
        kill_y = h_max + launch_margin * 4 + 20

        for _ in range(max_steps):
            if y < -5 * stick_radius or y > kill_y:
                break  # escaped sideways off the top or dug below the seed line

            gap = y - h_max
            if gap > close_step:
                step = rng.uniform(0.0, gap)
                phi = rng.uniform(0, 2 * np.pi)
                x = wrap(x + step * np.cos(phi))
                y += step * np.sin(phi)
                continue

            phi = rng.uniform(0, 2 * np.pi)
            nx = wrap(x + close_step * np.cos(phi))
            ny = y + close_step * np.sin(phi)
            dist = grid.nearest_dist(nx, ny)
            if dist < stick_radius:
                if rng.uniform() < stick_prob:
                    grid.insert(nx, ny)
                    points.append((nx, ny))
                    arrival.append(n)
                    if ny > h_max:
                        h_max = ny
                    break
                continue
            x, y = nx, ny

    return np.array(points), np.array(arrival)


def box_count_dimension(points, n_scales=18, r_min_factor=0.02, r_max_factor=0.6):
    """Estimate the fractal (box-counting) dimension of a 2D point set.

    Returns (box_sizes, counts, dimension, fit_intercept).
    """
    x, y = points[:, 0], points[:, 1]
    span = max(x.max() - x.min(), y.max() - y.min())
    sizes = np.geomspace(span * r_min_factor, span * r_max_factor, n_scales)
    counts = []
    for s in sizes:
        ix = np.floor((x - x.min()) / s).astype(np.int64)
        iy = np.floor((y - y.min()) / s).astype(np.int64)
        occupied = set(zip(ix.tolist(), iy.tolist()))
        counts.append(len(occupied))
    counts = np.array(counts)
    log_s = np.log(1.0 / sizes)
    log_n = np.log(counts)
    slope, intercept = np.polyfit(log_s, log_n, 1)
    return sizes, counts, slope, intercept

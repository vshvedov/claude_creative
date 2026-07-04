"""
Buddhabrot: instead of coloring c by escape time, sample many random c
points that DO escape the Mandelbrot iteration, and for each one, plot
every z-value its orbit visits on its way out to infinity. Points that
never escape (i.e. c is in the Mandelbrot set) contribute nothing.

Classic "Nebulabrot" coloring: run three separate accumulation passes
with different iteration-count ceilings, and use the three histograms as
R/G/B channels. Short-lived orbits are common and fill in broad structure;
long-lived orbits are rare and trace fine ghostly filaments.
"""
import numpy as np


def _in_main_bulbs(C):
    """Closed-form test for the main cardioid and the period-2 bulb — the
    two big interior regions. Points inside never escape, so filtering them
    out up front avoids burning max_iter steps on the majority of 'wasted'
    interior samples."""
    x, y = C.real, C.imag
    p = np.sqrt((x - 0.25) ** 2 + y ** 2)
    in_cardioid = x < p - 2 * p ** 2 + 0.25
    in_bulb2 = (x + 1) ** 2 + y ** 2 < 0.0625
    return in_cardioid | in_bulb2


def sample_escaping_points(n_samples, max_iter, xmin, xmax, ymin, ymax, rng):
    """Vectorized: draw n_samples random c in the box, iterate, and return
    (c_escaped, escape_iter) for the subset that escapes within max_iter."""
    cx = rng.uniform(xmin, xmax, n_samples)
    cy = rng.uniform(ymin, ymax, n_samples)
    C = cx + 1j * cy
    C = C[~_in_main_bulbs(C)]
    n_samples = C.shape[0]

    Z = np.zeros(n_samples, dtype=np.complex128)
    escape_iter = np.full(n_samples, -1, dtype=np.int32)
    active = np.ones(n_samples, dtype=bool)

    for i in range(max_iter):
        idx = np.where(active)[0]
        if idx.size == 0:
            break
        Zi = Z[idx] ** 2 + C[idx]
        Z[idx] = Zi
        escaped_now = np.abs(Zi) > 2.0
        if np.any(escaped_now):
            escape_iter[idx[escaped_now]] = i
            active[idx[escaped_now]] = False

    escaped_mask = escape_iter >= 0
    return C[escaped_mask], escape_iter[escaped_mask]


def accumulate_trajectories(c_points, escape_iters, width, height,
                            xmin, xmax, ymin, ymax, channel_ranges):
    """Replay each escaping trajectory and bin every visited z into one
    histogram per channel range (lo, hi] of escape iteration."""
    hists = [np.zeros((height, width), dtype=np.int64) for _ in channel_ranges]

    n = len(c_points)
    Z = np.zeros(n, dtype=np.complex128)
    C = c_points
    remaining = escape_iters.copy()
    active = np.ones(n, dtype=bool)

    channel_of_point = np.full(n, -1, dtype=np.int8)
    for ch, (lo, hi) in enumerate(channel_ranges):
        in_range = (escape_iters > lo) & (escape_iters <= hi)
        channel_of_point[in_range] = ch

    max_iter = int(escape_iters.max())
    for i in range(max_iter):
        idx = np.where(active)[0]
        if idx.size == 0:
            break
        Zi = Z[idx] ** 2 + C[idx]
        Z[idx] = Zi

        col = ((Zi.real - xmin) / (xmax - xmin) * width).astype(np.int64)
        row = ((Zi.imag - ymin) / (ymax - ymin) * height).astype(np.int64)
        valid = (col >= 0) & (col < width) & (row >= 0) & (row < height)

        for ch in range(len(channel_ranges)):
            in_ch = valid & (channel_of_point[idx] == ch)
            if np.any(in_ch):
                np.add.at(hists[ch], (row[in_ch], col[in_ch]), 1)

        finished = remaining[idx] <= i
        active[idx[finished]] = False

    return hists

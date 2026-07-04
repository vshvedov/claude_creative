"""
Core escape-time machinery for Mandelbrot / Julia / Multibrot sets.

The iteration is always z_{n+1} = z_n^power + c. For the Mandelbrot family,
z_0 = 0 and c ranges over the plane; for a Julia set, c is fixed and z_0
ranges over the plane. Smooth (continuous) iteration counts avoid the
banding you'd get from raw integer escape counts.
"""
import numpy as np


def escape_time(width, height, xmin, xmax, ymin, ymax, max_iter,
                 power=2, julia_c=None, bailout=1e6):
    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymin, ymax, height)
    X, Y = np.meshgrid(x, y)

    if julia_c is None:
        Z = np.zeros_like(X, dtype=np.complex128)
        C = X + 1j * Y
    else:
        Z = X + 1j * Y
        C = np.full(Z.shape, julia_c, dtype=np.complex128)

    smooth_iter = np.full(Z.shape, max_iter, dtype=np.float64)
    active = np.ones(Z.shape, dtype=bool)

    for i in range(max_iter):
        Zi = Z[active]
        Zi = Zi ** power + C[active]
        Z[active] = Zi

        escaped = np.abs(Zi) > bailout
        if np.any(escaped):
            idx = np.where(active)
            esc_idx = (idx[0][escaped], idx[1][escaped])
            log_zn = np.log(np.abs(Zi[escaped]))
            nu = np.log(log_zn / np.log(bailout)) / np.log(power)
            smooth_iter[esc_idx] = (i + 1) - nu
            active[esc_idx] = False

        if not np.any(active):
            break

    in_set = active  # never escaped within max_iter
    return smooth_iter, in_set


def newton_fractal(width, height, xmin, xmax, ymin, ymax, max_iter,
                    roots, f, fprime, tol=1e-6):
    """Basins of attraction of Newton's method for polynomial f with
    known roots. Returns (root_index, iterations_to_converge)."""
    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymin, ymax, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y

    root_idx = np.full(Z.shape, -1, dtype=int)
    conv_iter = np.full(Z.shape, max_iter, dtype=np.float64)
    active = np.ones(Z.shape, dtype=bool)
    roots = np.asarray(roots, dtype=np.complex128)

    for i in range(max_iter):
        idx = np.where(active)
        Zi = Z[active]
        deriv = fprime(Zi)
        deriv[deriv == 0] = 1e-12
        Zi = Zi - f(Zi) / deriv
        Z[active] = Zi

        dists = np.abs(Zi[:, None] - roots[None, :])
        nearest = np.argmin(dists, axis=1)
        converged = dists[np.arange(len(Zi)), nearest] < tol

        if np.any(converged):
            conv_positions = (idx[0][converged], idx[1][converged])
            root_idx[conv_positions] = nearest[converged]
            conv_iter[conv_positions] = i
            active[conv_positions] = False

        if not np.any(active):
            break

    # leftover unconverged pixels: assign to nearest root anyway
    if np.any(active):
        idx = np.where(active)
        dists = np.abs(Z[active][:, None] - roots[None, :])
        root_idx[idx] = np.argmin(dists, axis=1)

    return root_idx, conv_iter

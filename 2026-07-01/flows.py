"""
Shared machinery for rendering continuous-time chaotic flows (strange
attractors defined by ODEs, as opposed to the iterated maps from 2026-06-23).

Each system is a right-hand-side function f(t, state, **params) -> d(state)/dt,
integrated with scipy's adaptive RK45 and rendered as a smoothly-colored
LineCollection so the gradient follows the trajectory rather than time-binned
scatter dots.
"""
import numpy as np
from scipy.integrate import solve_ivp
from matplotlib.collections import LineCollection


def integrate(rhs, state0, t_span, n_points, args=(), rtol=1e-9, atol=1e-9):
    t_eval = np.linspace(t_span[0], t_span[1], n_points)
    sol = solve_ivp(rhs, t_span, state0, t_eval=t_eval, args=args,
                     method="RK45", rtol=rtol, atol=atol, max_step=0.05)
    return sol.t, sol.y  # y is shape (3, n_points)


def lorenz(t, state, sigma=10.0, rho=28.0, beta=8.0 / 3.0):
    x, y, z = state
    return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]


def rossler(t, state, a=0.2, b=0.2, c=5.7):
    x, y, z = state
    return [-y - z, x + a * y, b + z * (x - c)]


def thomas(t, state, b=0.208186):
    x, y, z = state
    return [np.sin(y) - b * x, np.sin(z) - b * y, np.sin(x) - b * z]


def chen(t, state, a=35.0, b=3.0, c=28.0):
    x, y, z = state
    return [a * (y - x), (c - a) * x - x * z + c * y, x * y - b * z]


def halvorsen(t, state, a=1.4):
    x, y, z = state
    return [-a * x - 4 * y - 4 * z - y ** 2,
            -a * y - 4 * z - 4 * x - z ** 2,
            -a * z - 4 * x - 4 * y - x ** 2]


def aizawa(t, state, a=0.95, b=0.7, c=0.6, d=3.5, e=0.25, f=0.1):
    x, y, z = state
    dx = (z - b) * x - d * y
    dy = d * x + (z - b) * y
    dz = (c + a * z - z ** 3 / 3.0) - (x ** 2 + y ** 2) * (1 + e * z) + f * z * x ** 3
    return [dx, dy, dz]


def colored_line(ax, xs, ys, cmap, lw=0.6, alpha=0.9, zorder=2):
    """Draw a 2D curve whose color sweeps through `cmap` along its length."""
    points = np.array([xs, ys]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    t = np.linspace(0, 1, len(xs))
    lc = LineCollection(segments, cmap=cmap, array=t, linewidths=lw,
                         alpha=alpha, zorder=zorder)
    ax.add_collection(lc)
    ax.autoscale()
    return lc

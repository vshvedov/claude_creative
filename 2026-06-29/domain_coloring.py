#!/usr/bin/env python3
"""
Domain coloring of complex functions — 2026-06-29

Enhanced Wegert scheme: hue = arg(f(z)), brightness oscillates with log|f(z)|
to reveal magnitude contour rings. Zeros appear as black; poles as white.
Winding number = number of full color cycles around a point.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
from scipy.special import loggamma
import warnings
warnings.filterwarnings('ignore')


# ─── Core rendering ──────────────────────────────────────────────────────────

def domain_color(w):
    """
    Convert complex values to RGB.
    Hue = arg(w), value oscillates with log|w| (one ring per unit of log mag).
    """
    w = np.asarray(w, dtype=complex)
    with np.errstate(all='ignore'):
        arg = np.angle(w)                          # -π to π
        mag = np.abs(w)

    hue = (arg / (2.0 * np.pi)) % 1.0             # 0=red, 0.5=cyan
    log_mag = np.log(np.maximum(mag, 1e-15))
    value = 0.5 + 0.45 * np.sin(log_mag * np.pi)  # rings at each factor of e

    hsv = np.stack([
        np.clip(hue, 0.0, 1.0),
        np.full_like(hue, 0.92),
        np.clip(value, 0.0, 1.0),
    ], axis=-1)
    return hsv_to_rgb(hsv)


def render(ax, f, xr, yr, res=700, title='', fontsize=13):
    """Render f on the rectangle xr × yr into axis ax."""
    dx, dy = xr[1] - xr[0], yr[1] - yr[0]
    # Square pixels in data coordinates
    if dx >= dy:
        rx = res
        ry = max(16, int(res * dy / dx))
    else:
        ry = res
        rx = max(16, int(res * dx / dy))

    x = np.linspace(xr[0], xr[1], rx)
    y = np.linspace(yr[0], yr[1], ry)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y

    with np.errstate(all='ignore'):
        W = np.asarray(f(Z), dtype=complex)

    rgb = domain_color(W)
    ax.imshow(rgb, origin='lower', extent=[xr[0], xr[1], yr[0], yr[1]],
              aspect='auto', interpolation='bilinear')
    ax.set_title(title, color='#e0e0e0', fontsize=fontsize, pad=7)
    ax.tick_params(colors='#555', labelsize=8)
    for sp in ax.spines.values():
        sp.set_color('#333')
    if xr[0] < 0 < xr[1]:
        ax.axvline(0, color='#ffffff18', lw=0.6)
    if yr[0] < 0 < yr[1]:
        ax.axhline(0, color='#ffffff18', lw=0.6)


BG = '#0d0d0d'


def new_fig(rows, cols, wp, hp, title=''):
    fig, axes = plt.subplots(rows, cols, figsize=(cols * wp, rows * hp),
                             facecolor=BG)
    axes = np.array(axes).reshape(rows, cols)
    for ax in axes.flat:
        ax.set_facecolor(BG)
    if title:
        fig.suptitle(title, color='#c8c8c8', fontsize=14, y=0.01, va='bottom')
    return fig, axes


# ─── Special functions ────────────────────────────────────────────────────────

def gamma_c(z):
    """Gamma function for complex z via log-gamma."""
    with np.errstate(all='ignore'):
        return np.exp(loggamma(z.astype(complex)))


def zeta_approx(z, N=200, chunk=4000):
    """
    Approximate Riemann zeta via Dirichlet eta:
        eta(s) = sum_{n=1}^N (-1)^{n-1} / n^s   (converges Re(s) > 0)
        zeta(s) = eta(s) / (1 - 2^{1-s})
    Computed in chunks to limit peak memory.
    """
    z = np.asarray(z, dtype=complex)
    shape = z.shape
    zf = z.reshape(-1)
    M = len(zf)

    n = np.arange(1, N + 1, dtype=float)
    log_n = np.log(n)
    signs = (-1.0) ** (n - 1)

    result = np.zeros(M, dtype=complex)
    for i in range(0, M, chunk):
        b = zf[i:i + chunk]                              # (B,)
        powers = np.exp(-b[:, None] * log_n[None, :])   # (B, N)
        eta_b = (signs[None, :] * powers).sum(axis=1)   # (B,)
        factor = 1.0 - 2.0 ** (1.0 - b)
        factor = np.where(np.abs(factor) < 1e-10, 1e-10 + 0j, factor)
        result[i:i + chunk] = eta_b / factor

    return result.reshape(shape)


# ─────────────────────────────────────────────────────────────────────────────
# Figure 1: Polynomials & rational functions
# ─────────────────────────────────────────────────────────────────────────────
print("Figure 1: polynomials …")

fig, axes = new_fig(2, 3, 5.5, 5.5,
    title='Domain Coloring — Polynomials & Rational Functions')

polys = [
    ('z',              lambda z: z,                    (-2.5, 2.5), (-2.5, 2.5)),
    ('z²',             lambda z: z**2,                 (-2.5, 2.5), (-2.5, 2.5)),
    ('z³ − 1',         lambda z: z**3 - 1,             (-2.0, 2.0), (-2.0, 2.0)),
    ('1 / z',          lambda z: 1.0 / z,              (-2.5, 2.5), (-2.5, 2.5)),
    ('(z²−1) / z²',   lambda z: (z**2 - 1) / z**2,   (-2.5, 2.5), (-2.5, 2.5)),
    ('z⁴ − 1',         lambda z: z**4 - 1,             (-1.8, 1.8), (-1.8, 1.8)),
]

for ax, (title, f, xr, yr) in zip(axes.flat, polys):
    render(ax, f, xr, yr, title=title)

plt.tight_layout(rect=[0, 0.04, 1, 1])
fig.savefig('01_polynomials.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("  saved 01_polynomials.png")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 2: Transcendental functions
# ─────────────────────────────────────────────────────────────────────────────
print("Figure 2: transcendental …")

fig, axes = new_fig(2, 3, 5.5, 5.5,
    title='Domain Coloring — Transcendental Functions')

transcendental = [
    ('eᶻ',          lambda z: np.exp(z),         (-3.0, 3.0), (-3.0, 3.0)),
    ('sin(z)',       lambda z: np.sin(z),          (-5.0, 5.0), (-5.0, 5.0)),
    ('tan(z)',       lambda z: np.tan(z),          (-4.0, 4.0), (-4.0, 4.0)),
    ('e^(1/z)',      lambda z: np.exp(1.0 / z),   (-1.2, 1.2), (-1.2, 1.2)),
    ('sin(1/z)',     lambda z: np.sin(1.0 / z),   (-0.5, 0.5), (-0.5, 0.5)),
    ('1 / sin(z)',   lambda z: 1.0 / np.sin(z),   (-4.5, 4.5), (-4.5, 4.5)),
]

for ax, (title, f, xr, yr) in zip(axes.flat, transcendental):
    render(ax, f, xr, yr, title=title)

plt.tight_layout(rect=[0, 0.04, 1, 1])
fig.savefig('02_transcendental.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("  saved 02_transcendental.png")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 3: Gamma function
# ─────────────────────────────────────────────────────────────────────────────
print("Figure 3: Gamma …")

fig, axes = new_fig(1, 2, 7.5, 7.0,
    title='Γ(z) — poles at 0, −1, −2, … and NO zeros anywhere')

render(axes[0, 0], gamma_c, (-5.5, 3.5), (-5.0, 5.0), res=800,
       title='Γ(z) — wide view')
render(axes[0, 1], gamma_c, (-8.0, 1.5), (-2.0, 2.0), res=800,
       title='Γ(z) — poles along negative real axis')

plt.tight_layout(rect=[0, 0.05, 1, 1])
fig.savefig('03_gamma.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("  saved 03_gamma.png")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 4: Essential singularity zoom sequence
# ─────────────────────────────────────────────────────────────────────────────
print("Figure 4: essential singularity zoom …")

fig, axes = new_fig(1, 4, 4.5, 4.5,
    title="e^(1/z) — Picard's theorem: every color at every scale near z = 0")

radii = [1.5, 0.4, 0.10, 0.025]
for ax, r in zip(axes.flat, radii):
    render(ax, lambda z, r=r: np.exp(1.0 / z), (-r, r), (-r, r),
           res=600, title=f'|z| ≤ {r}')

plt.tight_layout(rect=[0, 0.06, 1, 1])
fig.savefig('04_essential_singularity.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("  saved 04_essential_singularity.png")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 5: Riemann zeta — critical strip
# ─────────────────────────────────────────────────────────────────────────────
print("Figure 5: Riemann zeta (slow) …")

fig, axes = new_fig(1, 2, 5.0, 9.0,
    title='ζ(s) — Riemann zeta function in the critical strip')

# Left panel: strip 0 < Re(s) < 2, 0 < Im(s) < 50 — first dozen non-trivial zeros
render(axes[0, 0],
       lambda z: zeta_approx(z, N=180),
       (0.05, 2.0), (1.0, 50.0), res=500,
       title='ζ(s),  0 < Re(s) < 2,  Im(s) up to 50')
axes[0, 0].axvline(0.5, color='white', lw=0.8, alpha=0.5, linestyle='--')
axes[0, 0].set_xlabel('Re(s)', color='#888', fontsize=9)
axes[0, 0].set_ylabel('Im(s)', color='#888', fontsize=9)

# Right panel: zoomed near critical line, first three zeros at ~14.13, 21.02, 25.01
render(axes[0, 1],
       lambda z: zeta_approx(z, N=250),
       (0.1, 0.9), (12.0, 28.0), res=500,
       title='ζ(s) zoomed — zeros at Im ≈ 14.1, 21.0, 25.0')
axes[0, 1].axvline(0.5, color='white', lw=0.8, alpha=0.5, linestyle='--')
axes[0, 1].set_xlabel('Re(s)', color='#888', fontsize=9)
# Annotate the known zeros
for y_zero, label in [(14.135, '14.13'), (21.022, '21.02'), (25.010, '25.01')]:
    axes[0, 1].annotate(f'Im={label}', xy=(0.5, y_zero),
                        xytext=(0.62, y_zero + 0.4),
                        color='#ffffff88', fontsize=7.5,
                        arrowprops=dict(arrowstyle='->', color='#ffffff44', lw=0.8))

plt.tight_layout(rect=[0, 0.05, 1, 1])
fig.savefig('05_zeta.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("  saved 05_zeta.png")

print("\nAll done.")

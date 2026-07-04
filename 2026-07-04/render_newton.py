import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
from fractals import newton_fractal

# z^3 - 1 = 0 -> 3 cube roots of unity. Newton's method on this polynomial,
# extended to the complex plane, produces a fractal boundary between the
# three basins of attraction (the "Newton fractal" for the cubic).
def make_panel(power, roots):
    f = lambda z: z ** power - 1
    fprime = lambda z: power * z ** (power - 1)
    root_idx, conv_iter = newton_fractal(
        700, 700, -1.6, 1.6, -1.6, 1.6, max_iter=60, roots=roots, f=f, fprime=fprime,
    )
    hue = (root_idx.astype(float) % len(roots)) / len(roots)
    val = 1.0 - (conv_iter / conv_iter.max()) * 0.85
    sat = np.full_like(hue, 0.85)
    hsv = np.stack([hue, sat, val], axis=-1)
    return hsv_to_rgb(hsv)


fig, axes = plt.subplots(1, 3, figsize=(18, 6.2), dpi=150)
fig.patch.set_facecolor("black")

for ax, power in zip(axes, [3, 4, 5]):
    roots = [np.exp(2j * np.pi * k / power) for k in range(power)]
    rgb = make_panel(power, roots)
    ax.imshow(rgb, origin="lower", extent=[-1.6, 1.6, -1.6, 1.6])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"Newton fractal for z^{power} − 1 = 0", color="white", fontsize=13)

fig.suptitle(
    "Newton's method in the complex plane — each color is a basin of attraction\n"
    "toward one root; brightness is how fast it converged; the boundary is fractal",
    color="white", fontsize=13,
)
plt.tight_layout()
plt.savefig("04_newton.png", facecolor="black")
print("wrote 04_newton.png")

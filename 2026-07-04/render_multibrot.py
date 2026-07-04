import numpy as np
import matplotlib.pyplot as plt
from fractals import escape_time

# z ↦ z^d + c for d = 2..7. The Mandelbrot set generalizes to a "Multibrot"
# with (d-1)-fold rotational symmetry: d=2 gives the familiar cardioid+bulb,
# d=3 gives a 2-fold-symmetric body with two main lobes, and so on.
POWERS = [2, 3, 4, 5, 6, 7]

fig, axes = plt.subplots(2, 3, figsize=(15, 10.4), dpi=140)
fig.patch.set_facecolor("black")
cmap = plt.get_cmap("cubehelix")

for ax, d in zip(axes.flat, POWERS):
    smooth_iter, in_set = escape_time(
        600, 600, xmin=-1.8, xmax=1.8, ymin=-1.8, ymax=1.8,
        max_iter=300, power=d, bailout=1e4,
    )
    img = np.log(smooth_iter + 1)
    img[in_set] = -1
    ax.imshow(img, cmap=cmap, origin="lower")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"z ↦ z^{d} + c   ({d - 1}-fold symmetry)", color="white", fontsize=12)

fig.suptitle("Multibrot sets: generalizing z² + c to higher powers", color="white", fontsize=15)
plt.tight_layout()
plt.savefig("06_multibrot.png", facecolor="black")
print("wrote 06_multibrot.png")

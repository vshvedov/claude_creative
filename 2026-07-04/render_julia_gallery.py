import numpy as np
import matplotlib.pyplot as plt
from fractals import escape_time

# A spread of c-values chosen to show qualitatively different Julia sets:
# connected dendrites, "rabbit"-style fat basins, dust (totally disconnected),
# and the spiral/San-Marco type basins near the boundary of the main cardioid.
CS = [
    (-0.4 + 0.6j,   "dendrite-ish spiral"),
    (-0.8 + 0.156j, "elephant valley"),
    (-0.7269 + 0.1889j, "airplane / rabbit hybrid"),
    (0.285 + 0.01j, "near-boundary spiral"),
    (-0.70176 - 0.3842j, "classic dendrite"),
    (0.355 + 0.355j, "seaweed"),
    (-0.75 + 0.11j, "boundary of the main body"),
    (0.7 + 0.3j,    "disconnected dust (c outside M)"),
    (-1.25 + 0.0j,  "period-2 bulb, on the real axis"),
]

fig, axes = plt.subplots(3, 3, figsize=(15, 15), dpi=140)
fig.patch.set_facecolor("black")
cmap = plt.get_cmap("magma")

for ax, (c, label) in zip(axes.flat, CS):
    smooth_iter, in_set = escape_time(
        500, 500, xmin=-1.6, xmax=1.6, ymin=-1.6, ymax=1.6,
        max_iter=400, power=2, julia_c=c,
    )
    img = np.log(smooth_iter + 1)
    img[in_set] = -1
    ax.imshow(img, cmap=cmap, origin="lower")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"c = {c.real:+.4f}{c.imag:+.4f}i\n{label}", color="white", fontsize=10)

plt.tight_layout()
plt.savefig("02_julia_gallery.png", facecolor="black")
print("wrote 02_julia_gallery.png")

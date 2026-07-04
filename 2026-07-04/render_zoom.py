import numpy as np
import matplotlib.pyplot as plt
from fractals import escape_time

# "Seahorse valley" — a classic zoom target where an infinite necklace of
# mini-Mandelbrots hangs off the main cardioid.
cx, cy = -0.743643887037151, 0.13182590420533

zoom_factors = [1, 15, 150, 1500, 15000, 150000]
max_iters =    [300, 400, 600, 900, 1400, 2000]

fig, axes = plt.subplots(2, 3, figsize=(16, 11), dpi=140)
fig.patch.set_facecolor("black")
cmap = plt.get_cmap("twilight_shifted")

for ax, zoom, max_iter in zip(axes.flat, zoom_factors, max_iters):
    half_w = 1.4 / zoom
    smooth_iter, in_set = escape_time(
        500, 500,
        xmin=cx - half_w, xmax=cx + half_w,
        ymin=cy - half_w, ymax=cy + half_w,
        max_iter=max_iter, power=2,
    )
    img = np.log(smooth_iter + 1)
    img[in_set] = -1
    ax.imshow(img, cmap=cmap, origin="lower")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"zoom ×{zoom:,}", color="white", fontsize=11)

fig.suptitle(
    "Zooming into Seahorse Valley — the same cardioid-and-bulb motif\n"
    "reappears at every scale, always slightly deformed",
    color="white", fontsize=14,
)
plt.tight_layout()
plt.savefig("03_zoom.png", facecolor="black")
print("wrote 03_zoom.png")

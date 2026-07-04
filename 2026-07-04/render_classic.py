import numpy as np
import matplotlib.pyplot as plt
from fractals import escape_time

W, H = 2400, 1800
smooth_iter, in_set = escape_time(
    W, H, xmin=-2.4, xmax=0.9, ymin=-1.25, ymax=1.25,
    max_iter=1000, power=2,
)

img = np.log(smooth_iter + 1)
img[in_set] = np.nan  # the set itself rendered separately, in flat black

fig, ax = plt.subplots(figsize=(16, 12), dpi=150)
ax.set_facecolor("black")
cmap = plt.get_cmap("twilight_shifted").copy()
cmap.set_bad("black")

ax.imshow(img, extent=[-2.4, 0.9, -1.25, 1.25], cmap=cmap, origin="lower")
ax.set_xticks([])
ax.set_yticks([])
ax.set_title(
    "The Mandelbrot set — z ↦ z² + c, colored by smoothed escape time",
    color="white", fontsize=15, pad=14,
)
fig.patch.set_facecolor("black")
plt.tight_layout()
plt.savefig("01_classic.png", facecolor="black")
print("wrote 01_classic.png")

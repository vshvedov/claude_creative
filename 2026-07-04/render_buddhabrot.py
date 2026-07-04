import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from buddhabrot import sample_escaping_points, accumulate_trajectories

XMIN, XMAX, YMIN, YMAX = -2.0, 1.0, -1.5, 1.5
WIDTH, HEIGHT = 1400, 1400
N_SAMPLES = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
MAX_ITER = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
OUTFILE = sys.argv[3] if len(sys.argv) > 3 else "05_buddhabrot.png"

CHANNELS = [(1, 40), (40, 300), (300, MAX_ITER)]  # R, G, B escape-iteration bands

rng = np.random.default_rng(0)

t0 = time.time()
c_points, esc_iters = sample_escaping_points(
    N_SAMPLES, MAX_ITER, XMIN, XMAX, YMIN, YMAX, rng
)
t1 = time.time()
print(f"sampled {N_SAMPLES:,} points, {len(c_points):,} escaped "
      f"({t1 - t0:.1f}s)")
for i, (lo, hi) in enumerate(CHANNELS):
    n_in_band = np.sum((esc_iters > lo) & (esc_iters <= hi))
    print(f"  channel {i} ({lo},{hi}]: {n_in_band:,} trajectories")

hists = accumulate_trajectories(
    c_points, esc_iters, WIDTH, HEIGHT, XMIN, XMAX, YMIN, YMAX, CHANNELS
)
t2 = time.time()
print(f"accumulated trajectories ({t2 - t1:.1f}s)")

def normalize(h, gamma=0.45):
    h = h.astype(np.float64)
    h = h / (h.max() + 1e-9)
    return h ** gamma

rgb = np.stack([normalize(h) for h in hists], axis=-1)
rgb = np.rot90(rgb)  # classic vertical "sitting figure" orientation

fig, ax = plt.subplots(figsize=(11, 14), dpi=150)
fig.patch.set_facecolor("black")
ax.imshow(rgb, origin="lower")
ax.set_xticks([])
ax.set_yticks([])
ax.set_title(
    "Buddhabrot — density of escaping orbits, R/G/B = short/medium/long-lived",
    color="white", fontsize=12,
)
plt.tight_layout()
plt.savefig(OUTFILE, facecolor="black")
print(f"wrote {OUTFILE} (total {time.time() - t0:.1f}s)")

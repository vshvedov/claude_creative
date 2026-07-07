"""02: Rule 30 at scale, plus the center-column randomness Wolfram's own
software (Mathematica's RandomInteger) has used as an actual PRNG source
since the 1990s.
"""
import numpy as np
import matplotlib.pyplot as plt
from eca import run

WIDTH = 1201
STEPS = 600
hist = run(30, WIDTH, STEPS, init="single")

fig = plt.figure(figsize=(16, 11))
gs = fig.add_gridspec(2, 1, height_ratios=[5, 1], hspace=0.12)

ax0 = fig.add_subplot(gs[0])
ax0.imshow(hist, cmap="binary", interpolation="nearest", aspect="auto")
ax0.set_xticks([])
ax0.set_yticks([])
ax0.set_title(
    "Rule 30, single seed, 600 generations — deterministic, reversible-input,\n"
    "and by every statistical test that's been thrown at it, indistinguishable from noise",
    fontsize=13,
)

# Center column: this exact bit sequence is what Wolfram's software has
# used as a random number source since Mathematica 3 (1996).
center = hist[:, WIDTH // 2]
ax1 = fig.add_subplot(gs[1])
ax1.imshow(center[np.newaxis, :400], cmap="binary", interpolation="nearest", aspect="auto")
ax1.set_yticks([])
ax1.set_xlabel("center column, first 400 generations — this bit sequence is Mathematica's default PRNG", fontsize=11)

ones = center.sum()
fig.text(
    0.5, 0.015,
    f"center-column density over all {STEPS} generations: {ones}/{STEPS} = {ones/STEPS:.3f} "
    f"(a fair coin would give 0.500)",
    ha="center", fontsize=11,
)

fig.tight_layout(rect=[0, 0.03, 1, 1])
fig.savefig("02_rule30_and_the_prng.png", dpi=140)
print("wrote 02_rule30_and_the_prng.png")

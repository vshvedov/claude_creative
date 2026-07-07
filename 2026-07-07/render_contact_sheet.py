"""06: All 256 elementary CA rules, single seed, small contact-sheet
thumbnails -- the entire rule space of this toy universe laid out at once.
Under the symmetry group (mirror left/right, complement 0<->1, or both)
the 256 rules collapse to 88 equivalence classes, so a lot of these tiles
are literally the same picture reflected or inverted -- but seeing all 256
side by side is still the fastest way to get a feel for how much of the
space is "boring" (dies out or fills solid) versus how thin the sliver of
genuinely rich rules (30, 45, 60, 90, 110, 150...) really is.
"""
import numpy as np
import matplotlib.pyplot as plt
from eca import run

WIDTH = 81
STEPS = 55
COLS, ROWS = 16, 16

fig, axes = plt.subplots(ROWS, COLS, figsize=(20, 21))

for rule in range(256):
    r, c = divmod(rule, COLS)
    ax = axes[r, c]
    hist = run(rule, WIDTH, STEPS, init="single")
    ax.imshow(hist, cmap="binary", interpolation="nearest", aspect="auto")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(str(rule), fontsize=7, pad=1.5)

fig.suptitle(
    "All 256 elementary cellular automaton rules, single-cell seed — "
    "the entire rule space of this toy universe",
    fontsize=15,
)
fig.tight_layout(rect=[0, 0, 1, 0.97], h_pad=0.3, w_pad=0.3)
fig.savefig("06_all_256_rules.png", dpi=130)
print("wrote 06_all_256_rules.png")

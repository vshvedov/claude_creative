"""01: Wolfram's four qualitative classes, same single-cell seed, four rules."""
import numpy as np
import matplotlib.pyplot as plt
from eca import run, wolfram_class

WIDTH = 401
STEPS = 220
RULES = [250, 182, 30, 110]

fig, axes = plt.subplots(2, 2, figsize=(14, 15))

for ax, rule in zip(axes.flat, RULES):
    hist = run(rule, WIDTH, STEPS, init="single")
    ax.imshow(hist, cmap="binary", interpolation="nearest", aspect="auto")
    ax.set_title(f"Rule {rule} — {wolfram_class(rule)}", fontsize=13)
    ax.set_xticks([])
    ax.set_yticks([])

fig.suptitle(
    "Same eight-line rule format, same single-pixel seed — four qualitatively\n"
    "different destinies (Wolfram's classes 1-4)",
    fontsize=14,
)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig("01_wolfram_classes.png", dpi=140)
print("wrote 01_wolfram_classes.png")

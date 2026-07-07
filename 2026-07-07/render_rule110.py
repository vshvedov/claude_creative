"""04: Rule 110 -- the one member of this family proven Turing-complete
(Cook, 2004). From a messy random start it doesn't stay chaotic: it
crystallizes into a periodic "ether" background within a few dozen steps,
and what's left over is a small population of localized, particle-like
defects (gliders) that travel through the ether at various fixed
velocities and interact -- collide, merge, annihilate, spawn new ones --
when they meet. Universal computation in Cook's proof is built entirely
out of streams of these gliders encoding a cyclic-tag system; nothing here
constructs that explicitly, this is just the raw ingredient made visible.
"""
import numpy as np
import matplotlib.pyplot as plt
from eca import rule_table, step

WIDTH = 420
STEPS = 320
rng = np.random.default_rng(3)
row = np.zeros(WIDTH, dtype=np.uint8)
row[rng.choice(WIDTH, size=56, replace=False)] = 1

table = rule_table(110)
hist = np.empty((STEPS + 1, WIDTH), dtype=np.uint8)
hist[0] = row
for t in range(1, STEPS + 1):
    row = step(row, table)
    hist[t] = row

fig, ax = plt.subplots(figsize=(15, 11))
ax.imshow(hist, cmap="binary", interpolation="nearest", aspect="auto")
ax.set_xticks([])
ax.set_yticks([])
ax.set_title(
    "Rule 110 from a random start: a chaotic first ~20 rows crystallizes into a\n"
    "periodic background ('ether'), leaving isolated traveling defects (gliders) that\n"
    "collide, merge and annihilate as they cross paths -- the substrate Cook's 2004\n"
    "proof used to show this eight-line rule is a universal computer",
    fontsize=13,
)
fig.tight_layout()
fig.savefig("04_rule110_gliders.png", dpi=140)
print("wrote 04_rule110_gliders.png")

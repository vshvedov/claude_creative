"""05: Rule 184 as a traffic model. Read each cell as a road segment: 1 = car,
0 = empty. Rule 184's lookup table turns out to implement exactly "a car
moves one step right if the cell ahead is empty, otherwise it waits" --
the simplest possible traffic-flow rule, and it comes from an ordinary
elementary CA table, not from anyone hand-coding "cars" or "roads."

Sweep initial car density from sparse to gridlocked and watch free flow
(cars glide right at constant speed, untouched) give way to permanent
traffic jams once density crosses 1/2 -- the same density threshold that
shows up in real highway-traffic phase-transition data.
"""
import numpy as np
import matplotlib.pyplot as plt
from eca import rule_table, step

WIDTH = 300
STEPS = 220
DENSITIES = [0.2, 0.35, 0.5, 0.65, 0.8]

table = rule_table(184)
fig, axes = plt.subplots(1, len(DENSITIES), figsize=(20, 8))

rng = np.random.default_rng(42)
for ax, density in zip(axes, DENSITIES):
    row = (rng.random(WIDTH) < density).astype(np.uint8)
    hist = np.empty((STEPS + 1, WIDTH), dtype=np.uint8)
    hist[0] = row
    for t in range(1, STEPS + 1):
        row = step(row, table)
        hist[t] = row
    ax.imshow(hist, cmap="binary", interpolation="nearest", aspect="auto")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"density = {density}", fontsize=13)

fig.suptitle(
    "Rule 184 as a traffic model (1 = car, moves right if the cell ahead is empty):\n"
    "below 1/2, free flow -- every car eventually cruises at full speed; at and above 1/2,\n"
    "permanent jams -- the same critical density seen in real traffic-flow data",
    fontsize=13,
)
fig.tight_layout(rect=[0, 0, 1, 0.88])
fig.savefig("05_rule184_traffic.png", dpi=140)
print("wrote 05_rule184_traffic.png")

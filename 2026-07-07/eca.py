"""Elementary cellular automaton engine.

A 1D row of cells, each 0 or 1. At each time step every cell looks at
itself and its two neighbors (3 bits -> 8 possible patterns) and a rule
number 0-255 gives the lookup table mapping each of those 8 patterns to
the cell's next state. That's the entire rule space: 256 possible
"physics", Wolfram-numbered by treating the 8 output bits as a binary
number (rule 30 = 00011110 in binary, etc).

Vectorized over the whole row with numpy + np.roll, periodic (wrap-around)
boundary conditions.
"""
import numpy as np


def rule_table(rule):
    """8-entry lookup table: table[4*left + 2*center + right] -> next state."""
    return np.array([(rule >> k) & 1 for k in range(8)], dtype=np.uint8)


def step(row, table):
    left = np.roll(row, 1)
    right = np.roll(row, -1)
    idx = (4 * left + 2 * row + right).astype(np.intp)
    return table[idx]


def run(rule, width, steps, init="single", seed=None):
    """Return an (steps+1, width) uint8 array, row 0 = initial condition."""
    table = rule_table(rule)
    row = np.zeros(width, dtype=np.uint8)
    if init == "single":
        row[width // 2] = 1
    elif init == "random":
        rng = np.random.default_rng(seed)
        row[:] = rng.integers(0, 2, size=width)
    else:
        raise ValueError(init)

    history = np.empty((steps + 1, width), dtype=np.uint8)
    history[0] = row
    for t in range(1, steps + 1):
        row = step(row, table)
        history[t] = row
    return history


def wolfram_class(rule):
    """Rough, informal classification used only for labeling figures."""
    labels = {
        250: "Class 1 (homogeneous)",
        182: "Class 2 (periodic / nested)",
        30: "Class 3 (chaotic)",
        110: "Class 4 (complex / localized structures)",
    }
    return labels.get(rule, "")

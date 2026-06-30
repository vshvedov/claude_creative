"""
Langton's Ant — 2026-06-30

A 2D Turing machine on a grid:
  - White cell: turn right 90°, flip to black, move forward
  - Black cell: turn left 90°, flip to white, move forward

First ~10,000 steps: apparent chaos.
Around step 10,000: a "highway" suddenly self-assembles and the ant marches
diagonally forever. No one has proved why. It just... does.

Multi-color generalization: define a rule string like "RL" (the classic),
or "LRRL", "RRLL", etc. Ant turns according to the rule character for the
current cell color, then advances the color by 1 (mod k).
Different rule strings produce radically different long-term behaviors:
periodic, chaotic, highway-building, or fractal-like.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec
from pathlib import Path

OUT = Path(__file__).parent

# ---------------------------------------------------------------------------
# Core simulation
# ---------------------------------------------------------------------------

def simulate_ant(n_steps, grid_size=None, rule="RL", seed_xy=None):
    """
    Run Langton's Ant (possibly multi-color) for n_steps.
    rule: string of 'L'/'R' characters, length = number of colors.
    Returns grid (2D int array) and ant path (N,2 array of positions).
    """
    k = len(rule)
    if grid_size is None:
        # size so the ant can't hit the boundary for typical step counts
        grid_size = max(200, int(np.sqrt(n_steps) * 1.5) + 20)
    grid = np.zeros((grid_size, grid_size), dtype=np.int32)

    cx, cy = (grid_size // 2, grid_size // 2) if seed_xy is None else seed_xy
    # direction: 0=N, 1=E, 2=S, 3=W
    d = 0
    dx = [0, 1, 0, -1]
    dy = [-1, 0, 1, 0]   # row increases downward

    path = np.empty((n_steps, 2), dtype=np.int32)

    for i in range(n_steps):
        path[i, 0] = cx
        path[i, 1] = cy
        color = grid[cy, cx]
        if rule[color] == 'R':
            d = (d + 1) % 4
        else:
            d = (d - 1) % 4
        grid[cy, cx] = (color + 1) % k
        cx += dx[d]
        cy += dy[d]
        # wrap (should be rare)
        cx = cx % grid_size
        cy = cy % grid_size

    return grid, path


def crop_grid(grid, margin=5):
    """Crop to bounding box of non-zero cells + margin."""
    rows = np.any(grid != 0, axis=1)
    cols = np.any(grid != 0, axis=0)
    if not rows.any():
        return grid
    r0, r1 = np.where(rows)[0][[0, -1]]
    c0, c1 = np.where(cols)[0][[0, -1]]
    r0 = max(0, r0 - margin)
    r1 = min(grid.shape[0], r1 + margin + 1)
    c0 = max(0, c0 - margin)
    c1 = min(grid.shape[1], c1 + margin + 1)
    return grid[r0:r1, c0:c1]


# ---------------------------------------------------------------------------
# Figure 1 — Evolution timeline (classic 2-color ant)
# ---------------------------------------------------------------------------

def figure_evolution():
    steps_list = [500, 2_000, 5_000, 10_000, 15_000, 25_000]
    labels = ["500", "2 000", "5 000", "10 000", "15 000", "25 000"]

    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    fig.patch.set_facecolor("#0a0a0a")
    axes = axes.ravel()

    # black = background (0), white = flipped cells (1)
    cmap = mcolors.ListedColormap(["#1a1a2e", "#e8e8f0"])

    for ax, n, label in zip(axes, steps_list, labels):
        grid, _ = simulate_ant(n, rule="RL")
        g = crop_grid(grid, margin=8)
        ax.imshow(g, cmap=cmap, interpolation="nearest", aspect="equal")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"step {label}", color="#cccccc", fontsize=12, pad=6,
                     fontfamily="monospace")
        for spine in ax.spines.values():
            spine.set_edgecolor("#333355")

    fig.suptitle("Langton's Ant — evolution timeline",
                 color="#e0e0f0", fontsize=15, y=0.98,
                 fontfamily="monospace", fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT / "01_evolution.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("01_evolution.png done")


# ---------------------------------------------------------------------------
# Figure 2 — Highway emergence close-up
# ---------------------------------------------------------------------------

def figure_highway():
    """Three panels: just-before / just-after / long-run, all same zoom."""
    steps_list = [9_800, 11_000, 30_000]
    labels = ["9 800 — pre-highway", "11 000 — highway forming", "30 000 — highway"]

    # Run 30k steps, snapshot intermediate grids by re-running (cheap enough)
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    fig.patch.set_facecolor("#0a0a0a")

    cmap = mcolors.ListedColormap(["#0d1117", "#c9d1d9"])

    # determine a consistent crop window from the final state
    grid_full, _ = simulate_ant(30_000, rule="RL")
    rows = np.any(grid_full != 0, axis=1)
    cols = np.any(grid_full != 0, axis=0)
    r0, r1 = np.where(rows)[0][[0, -1]]
    c0, c1 = np.where(cols)[0][[0, -1]]
    margin = 12
    r0 = max(0, r0 - margin); r1 = min(grid_full.shape[0], r1 + margin + 1)
    c0 = max(0, c0 - margin); c1 = min(grid_full.shape[1], c1 + margin + 1)

    for ax, n, label in zip(axes, steps_list, labels):
        grid, _ = simulate_ant(n, rule="RL", grid_size=grid_full.shape[0])
        g = grid[r0:r1, c0:c1]
        ax.imshow(g, cmap=cmap, interpolation="nearest", aspect="equal")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(label, color="#c9d1d9", fontsize=11, pad=8,
                     fontfamily="monospace")
        for spine in ax.spines.values():
            spine.set_edgecolor("#334455")

    fig.suptitle("Highway emergence — same spatial window, three snapshots",
                 color="#e0e0f0", fontsize=14, y=0.99,
                 fontfamily="monospace", fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT / "02_highway.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("02_highway.png done")


# ---------------------------------------------------------------------------
# Figure 3 — Multi-color variants
# ---------------------------------------------------------------------------

VARIANTS = [
    ("RL",    "RL — classic (highway)"),
    ("RRL",   "RRL — chaotic / growing blob"),
    ("RLLR",  "RLLR — fills region, then escapes"),
    ("LLRR",  "LLRR — symmetric diamond growth"),
    ("LRRL",  "LRRL — large-scale highway"),
    ("RRLLR", "RRLLR — complex fractal-like"),
]

def make_multicolor_cmap(k):
    """
    k-color colormap: color 0 is near-black (background),
    remaining colors sample a vivid perceptual cycle.
    """
    if k == 2:
        return mcolors.ListedColormap(["#0d1117", "#c9d1d9"])
    base_colors = ["#0d1117"]
    hues = np.linspace(0, 1, k, endpoint=False)
    for h in hues[1:]:
        r, g, b = mcolors.hsv_to_rgb([h, 0.75, 0.90])
        base_colors.append(mcolors.to_hex((r, g, b)))
    return mcolors.ListedColormap(base_colors)


def figure_multicolor():
    n_steps = 80_000

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.patch.set_facecolor("#080810")
    axes = axes.ravel()

    for ax, (rule, title) in zip(axes, VARIANTS):
        k = len(rule)
        grid, _ = simulate_ant(n_steps, rule=rule)
        g = crop_grid(grid, margin=10)
        cmap = make_multicolor_cmap(k)
        ax.imshow(g, cmap=cmap, vmin=0, vmax=k - 1,
                  interpolation="nearest", aspect="equal")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(title, color="#d0d0e8", fontsize=11, pad=6,
                     fontfamily="monospace")
        for spine in ax.spines.values():
            spine.set_edgecolor("#223344")

    fig.suptitle(f"Multi-color Langton's Ant — {n_steps:,} steps each",
                 color="#e8e8ff", fontsize=14, y=0.99,
                 fontfamily="monospace", fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(OUT / "03_multicolor.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("03_multicolor.png done")


# ---------------------------------------------------------------------------
# Figure 4 — Ant trajectory (path density map)
# ---------------------------------------------------------------------------

def figure_trajectory():
    """
    Show the ant's path as a density heatmap — how many times did the ant
    visit each cell? This reveals the internal structure of the chaos phase
    and the linear "burn" left by the highway.
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    fig.patch.set_facecolor("#080810")

    step_pairs = [
        (10_000,  "10 000 steps — chaos phase"),
        (15_000,  "15 000 steps — highway forming"),
        (50_000,  "50 000 steps — highway dominates"),
    ]

    for ax, (n, label) in zip(axes, step_pairs):
        g_size = max(250, int(np.sqrt(n) * 2.5) + 30)
        _, path = simulate_ant(n, rule="RL", grid_size=g_size)

        # Visit count
        density = np.zeros((g_size, g_size), dtype=np.int32)
        for x, y in path:
            density[y, x] += 1

        density = crop_grid(density, margin=10)
        log_density = np.log1p(density.astype(float))

        ax.imshow(log_density, cmap="inferno", interpolation="bilinear",
                  aspect="equal")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(label, color="#d8d8f0", fontsize=11, pad=8,
                     fontfamily="monospace")
        for spine in ax.spines.values():
            spine.set_edgecolor("#332244")

    fig.suptitle("Ant path density — log(visit count), inferno scale",
                 color="#e8e8ff", fontsize=14, y=0.99,
                 fontfamily="monospace", fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(OUT / "04_trajectory.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("04_trajectory.png done")


# ---------------------------------------------------------------------------
# Figure 5 — Rule space survey (3-color rules)
# ---------------------------------------------------------------------------

def figure_rule_survey():
    """
    All 3-color rules: 2^3 = 8 possibilities (LLL, LLR, LRL, LRR, RLL, RLR, RRL, RRR).
    Skip LLL (always left = pure circle) and RRR (always right = another circle).
    Show 6 interesting rules.
    """
    rules_3 = ["LLR", "LRL", "LRR", "RLL", "RLR", "RRL"]
    n_steps = 100_000

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.patch.set_facecolor("#080810")
    axes = axes.ravel()

    for ax, rule in zip(axes, rules_3):
        k = len(rule)
        grid, _ = simulate_ant(n_steps, rule=rule)
        g = crop_grid(grid, margin=10)
        cmap = make_multicolor_cmap(k)
        ax.imshow(g, cmap=cmap, vmin=0, vmax=k - 1,
                  interpolation="nearest", aspect="equal")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f'"{rule}"', color="#d0d8f0", fontsize=13, pad=6,
                     fontfamily="monospace", fontweight="bold")
        for spine in ax.spines.values():
            spine.set_edgecolor("#223344")

    fig.suptitle(f"All 6 non-trivial 3-color rules — {n_steps:,} steps each",
                 color="#e8e8ff", fontsize=14, y=0.99,
                 fontfamily="monospace", fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(OUT / "05_rule_survey.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("05_rule_survey.png done")


# ---------------------------------------------------------------------------
# Figure 6 — Three ants on the same grid (interference)
# ---------------------------------------------------------------------------

def simulate_multi_ant(n_steps, offsets, rules, grid_size=500):
    """
    Multiple ants sharing a grid (same cell state space).
    offsets: list of (dx, dy) from center for each ant's starting position.
    rules: list of rule strings (must all be same length = same k).
    Returns final grid.
    """
    k = len(rules[0])
    grid = np.zeros((grid_size, grid_size), dtype=np.int32)
    cx0, cy0 = grid_size // 2, grid_size // 2

    ants = []
    for (dx, dy), rule in zip(offsets, rules):
        ants.append({
            "x": cx0 + dx, "y": cy0 + dy,
            "d": 0, "rule": rule,
        })

    dx_map = [0, 1, 0, -1]
    dy_map = [-1, 0, 1, 0]

    for _ in range(n_steps):
        for ant in ants:
            color = grid[ant["y"], ant["x"]]
            if ant["rule"][color] == 'R':
                ant["d"] = (ant["d"] + 1) % 4
            else:
                ant["d"] = (ant["d"] - 1) % 4
            grid[ant["y"], ant["x"]] = (color + 1) % k
            ant["x"] = (ant["x"] + dx_map[ant["d"]]) % grid_size
            ant["y"] = (ant["y"] + dy_map[ant["d"]]) % grid_size

    return grid


def figure_multi_ant():
    """
    Two panels:
    - Three ants, same rule "RL", starting far apart → eventual collision
    - Three ants with rule "RRL", staggered starts
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.patch.set_facecolor("#080810")

    configs = [
        {
            "n":       60_000,
            "offsets": [(-60, -40), (0, 60), (55, -30)],
            "rules":   ["RL", "RL", "RL"],
            "title":   "Three classic ants — shared grid",
        },
        {
            "n":       80_000,
            "offsets": [(-80, 0), (0, 0), (80, 0)],
            "rules":   ["RRL", "RRL", "RRL"],
            "title":   "Three RRL ants — collinear start",
        },
    ]

    for ax, cfg in zip(axes, configs):
        k = len(cfg["rules"][0])
        grid = simulate_multi_ant(cfg["n"], cfg["offsets"], cfg["rules"])
        g = crop_grid(grid, margin=12)
        cmap = make_multicolor_cmap(k)
        ax.imshow(g, cmap=cmap, vmin=0, vmax=k - 1,
                  interpolation="nearest", aspect="equal")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(cfg["title"], color="#d0d8f0", fontsize=12, pad=8,
                     fontfamily="monospace")
        for spine in ax.spines.values():
            spine.set_edgecolor("#223344")

    fig.suptitle("Multiple ants sharing a grid — interaction and interference",
                 color="#e8e8ff", fontsize=14, y=0.99,
                 fontfamily="monospace", fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(OUT / "06_multi_ant.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("06_multi_ant.png done")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Rendering Langton's Ant figures...")
    figure_evolution()
    figure_highway()
    figure_multicolor()
    figure_trajectory()
    figure_rule_survey()
    figure_multi_ant()
    print("All done.")

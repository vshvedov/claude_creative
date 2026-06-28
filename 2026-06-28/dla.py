#!/usr/bin/env python3
"""
Diffusion-Limited Aggregation — 2026-06-28

Particles random-walk until they touch the growing cluster and stick.
The result is a fractal with D ≈ 1.71 in 2D.

Physics: the cluster grows proportional to the local gradient of the Laplace
diffusion field. Tips protrude → higher gradient → more particles intercepted
→ faster growth. Fjords are screened → near-zero gradient → no growth.
Mullins-Sekerka instability. Same mathematics as lightning, electrodeposition,
snowflake arms, and Hele-Shaw viscous fingers.

Speed: instead of one lattice step per walk iteration, we precompute the
Euclidean distance transform of the cluster grid and jump by (dist-1) pixels
per step — the "sphere of safety" from signed-distance-field ray marching.
One scipy.ndimage call every 200 particles replaces millions of step checks.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import distance_transform_edt
import os, time

OUTDIR = '/home/user/claude_creative/2026-06-28'
os.makedirs(OUTDIR, exist_ok=True)


# ──────────────────────────────────────────────────────────────────────────────
# Core DLA engine
# ──────────────────────────────────────────────────────────────────────────────

def grow_dla(n_particles, grid_size, seed_type='point', stickiness=1.0, rng_seed=42):
    """
    Grow a DLA cluster using distance-transform jump optimisation.

    seed_type: 'point' (radial), 'line' (grows up from bottom row)
    stickiness: p ∈ (0,1].  Low p → compact; p=1 → classic dendritic DLA.

    Returns arrival[row, col]:
        -1 = empty,  0 = seed,  k>0 = particle k was the k-th to stick.
    """
    rng = np.random.default_rng(rng_seed)
    mid = grid_size // 2

    cluster = np.zeros((grid_size, grid_size), dtype=bool)
    arrival = np.full((grid_size, grid_size), -1, dtype=np.int32)

    if seed_type == 'point':
        cluster[mid, mid] = True
        arrival[mid, mid] = 0
        max_r = 3.0
    elif seed_type == 'line':
        cluster[grid_size - 1, :] = True
        arrival[grid_size - 1, :] = 0
        max_r = 0.0

    dt = distance_transform_edt(~cluster).astype(np.float32)
    last_recompute = 0
    n_stuck = 0

    NEIGHBORS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while n_stuck < n_particles:

        # Refresh distance transform periodically.
        # DT is only used for jump SIZE, not for the stick decision, so
        # being slightly stale is fine — it just understimates safe jump
        # distance, causing smaller-than-needed jumps near new cells.
        if n_stuck - last_recompute >= 200:
            dt = distance_transform_edt(~cluster).astype(np.float32)
            last_recompute = n_stuck

        # ── release position ──────────────────────────────────────────────────
        if seed_type == 'point':
            r_rel = min(max_r + 5.0, mid - 5.0)
            a = rng.uniform(0.0, 2.0 * np.pi)
            row = int(np.clip(round(mid + r_rel * np.sin(a)), 1, grid_size - 2))
            col = int(np.clip(round(mid + r_rel * np.cos(a)), 1, grid_size - 2))
            # Kill radius large enough that sphere-jumps can't blow past it in
            # a few steps.  Sphere jumps scale with DT (≈ distance to cluster),
            # so for a tiny early cluster the jumps are large; we need kill_r
            # to be proportionally large so particles keep walking.
            kill_r = min(mid - 2.0, max_r * 6.0 + 80.0)
            # Cap single jump to max_r+5 so we can't overshoot kill_r in one
            # step when the cluster is small and DT values are huge.
            jump_cap = max(10, int(max_r) + 5)
        elif seed_type == 'line':
            # Seed is the full bottom row (row = grid_size - 1).
            # Cluster grows UPWARD (decreasing row index).
            top_row = max(1, int(grid_size - 1 - max_r) - 8)
            row = int(rng.integers(max(1, top_row - 5), min(grid_size - 2, top_row + 3)))
            col = int(rng.integers(1, grid_size - 1))
            # Large jump cap: far-above particles need big jumps to return.
            jump_cap = max(20, int(max_r) + 10)
            # Kill if the particle wanders too far ABOVE the cluster front.
            # Never kill on the way down — that's toward the cluster.
            kill_top = max(1, top_row - int(max_r) - 50)

        n_tries = 0

        for _ in range(200_000):

            # ── redirect if we landed on an occupied cell (stale DT) ──────────
            if cluster[row, col]:
                found = False
                for dr, dc in NEIGHBORS:
                    nr = int(np.clip(row + dr, 1, grid_size - 2))
                    nc = int(np.clip(col + dc, 1, grid_size - 2))
                    if not cluster[nr, nc]:
                        row, col = nr, nc
                        found = True
                        break
                if not found:
                    break
                continue

            # ── stick check: explicit 4-connected neighbour test ──────────────
            # We do NOT use the DT threshold (d ≤ 1.1) for the stick decision
            # because DT can be stale: a particle at DT=2 from the ORIGINAL
            # seed might be directly adjacent to a recently-added cluster cell
            # that the stale DT doesn't know about.  Explicit neighbour check
            # is always correct regardless of DT freshness.
            adjacent = any(
                0 <= row + dr < grid_size and
                0 <= col + dc < grid_size and
                cluster[row + dr, col + dc]
                for dr, dc in NEIGHBORS
            )

            if adjacent:
                if stickiness >= 1.0 or rng.random() < stickiness:
                    cluster[row, col] = True
                    n_stuck += 1
                    arrival[row, col] = n_stuck

                    if seed_type == 'point':
                        r_dist = np.sqrt((row - mid) ** 2 + (col - mid) ** 2)
                        if r_dist > max_r:
                            max_r = r_dist
                    elif seed_type == 'line':
                        h = (grid_size - 1) - row
                        if h > max_r:
                            max_r = float(h)
                    break
                else:
                    n_tries += 1
                    if n_tries > 150:
                        break

            # ── sphere-of-safety jump ─────────────────────────────────────────
            d = dt[row, col]
            jump = max(1, min(int(d) - 1, jump_cap))
            if jump > 1:
                a = rng.uniform(0.0, 2.0 * np.pi)
                row = int(np.clip(round(row + jump * np.sin(a)), 1, grid_size - 2))
                col = int(np.clip(round(col + jump * np.cos(a)), 1, grid_size - 2))
            else:
                idx = rng.integers(0, 4)
                row = int(np.clip(row + NEIGHBORS[idx][0], 1, grid_size - 2))
                col = int(np.clip(col + NEIGHBORS[idx][1], 1, grid_size - 2))

            # ── escape ────────────────────────────────────────────────────────
            if seed_type == 'point':
                dist_c = np.sqrt((row - mid) ** 2 + (col - mid) ** 2)
                if dist_c > kill_r:
                    break
            elif seed_type == 'line':
                # Only escape if the particle wandered too far ABOVE the
                # cluster.  Do NOT escape going downward — that's the
                # direction of the seed and the growing cluster.
                if row < kill_top:
                    break

        if n_stuck % 1000 == 0 and n_stuck > 0:
            print(f"   {n_stuck}/{n_particles}  max_r={max_r:.0f}")

    return arrival


def grow_ring_dla(n_particles, grid_size, ring_radius, rng_seed=99):
    """
    DLA from a ring seed: particles released near centre, walk outward,
    stick to the ring or the growing cluster (growing inward).
    """
    rng = np.random.default_rng(rng_seed)
    mid = grid_size // 2

    cluster = np.zeros((grid_size, grid_size), dtype=bool)
    arrival = np.full((grid_size, grid_size), -1, dtype=np.int32)

    # Mark ring cells
    for deg in range(0, 360):
        a = np.radians(deg)
        r = int(round(mid + ring_radius * np.sin(a)))
        c = int(round(mid + ring_radius * np.cos(a)))
        if 0 <= r < grid_size and 0 <= c < grid_size and arrival[r, c] < 0:
            cluster[r, c] = True
            arrival[r, c] = 0

    dt = distance_transform_edt(~cluster).astype(np.float32)
    last_recompute = 0
    n_stuck = 0

    NEIGHBORS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while n_stuck < n_particles:
        if n_stuck - last_recompute >= 200:
            dt = distance_transform_edt(~cluster).astype(np.float32)
            last_recompute = n_stuck

        # Release near centre; particles walk outward to hit the ring
        a = rng.uniform(0.0, 2.0 * np.pi)
        r_rel = rng.uniform(0.0, 8.0)
        row = int(np.clip(round(mid + r_rel * np.sin(a)), 1, grid_size - 2))
        col = int(np.clip(round(mid + r_rel * np.cos(a)), 1, grid_size - 2))

        for _ in range(200_000):
            if cluster[row, col]:
                for dr, dc in NEIGHBORS:
                    nr = int(np.clip(row + dr, 1, grid_size - 2))
                    nc = int(np.clip(col + dc, 1, grid_size - 2))
                    if not cluster[nr, nc]:
                        row, col = nr, nc
                        break
                else:
                    break
                continue

            adjacent = any(
                0 <= row + dr < grid_size and
                0 <= col + dc < grid_size and
                cluster[row + dr, col + dc]
                for dr, dc in NEIGHBORS
            )

            if adjacent:
                cluster[row, col] = True
                n_stuck += 1
                arrival[row, col] = n_stuck
                break

            d = dt[row, col]
            jump = max(1, min(int(d) - 1, ring_radius))
            if jump > 1:
                a = rng.uniform(0.0, 2.0 * np.pi)
                row = int(np.clip(round(row + jump * np.sin(a)), 1, grid_size - 2))
                col = int(np.clip(round(col + jump * np.cos(a)), 1, grid_size - 2))
            else:
                idx = rng.integers(0, 4)
                row = int(np.clip(row + NEIGHBORS[idx][0], 1, grid_size - 2))
                col = int(np.clip(col + NEIGHBORS[idx][1], 1, grid_size - 2))

            # Escaped past ring
            if np.sqrt((row - mid) ** 2 + (col - mid) ** 2) > ring_radius + 5:
                break

        if n_stuck % 500 == 0 and n_stuck > 0:
            print(f"   ring {n_stuck}/{n_particles}")

    return arrival


# ──────────────────────────────────────────────────────────────────────────────
# Colourmap helpers
# ──────────────────────────────────────────────────────────────────────────────

def arrival_rgba(arrival, cmap, seed_color=(1., 1., 1., 1.)):
    h, w = arrival.shape
    img = np.zeros((h, w, 4), dtype=np.float32)
    mask = arrival > 0
    if mask.any():
        vals = arrival[mask].astype(np.float32)
        v = (vals - vals.min()) / (vals.max() - vals.min() + 1e-9)
        img[mask] = cmap(v)
    img[arrival == 0] = seed_color
    return img


def crop(arr, pad=12):
    m = arr >= 0
    if not m.any():
        return arr
    rows = np.where(m.any(axis=1))[0]
    cols = np.where(m.any(axis=0))[0]
    r0 = max(0, rows[0] - pad)
    r1 = min(arr.shape[0], rows[-1] + pad + 1)
    c0 = max(0, cols[0] - pad)
    c1 = min(arr.shape[1], cols[-1] + pad + 1)
    return arr[r0:r1, c0:c1]


# ──────────────────────────────────────────────────────────────────────────────
# Simulations
# ──────────────────────────────────────────────────────────────────────────────

GRID = 500

t0 = time.time()
print('\n[timing] Distance transform on 500×500 …')
dummy = np.zeros((GRID, GRID), dtype=bool)
dummy[GRID//2, GRID//2] = True
_ = distance_transform_edt(~dummy)
print(f'  {(time.time()-t0)*1000:.1f} ms per transform')

print('\n[1/4] Point DLA — full stickiness (8 000 particles) …')
t0 = time.time()
arr_dense = grow_dla(8_000, GRID, seed_type='point', stickiness=1.0, rng_seed=17)
print(f'  done in {time.time()-t0:.1f}s')

print('\n[2/4] Point DLA — low stickiness p=0.2 (6 000 particles) …')
t0 = time.time()
arr_soft = grow_dla(6_000, GRID, seed_type='point', stickiness=0.2, rng_seed=31)
print(f'  done in {time.time()-t0:.1f}s')

print('\n[3/4] Line-seed DLA (8 000 particles) …')
t0 = time.time()
arr_line = grow_dla(8_000, GRID, seed_type='line', stickiness=1.0, rng_seed=55)
print(f'  done in {time.time()-t0:.1f}s')

print('\n[4/4] Ring-seed DLA growing inward (3 000 particles) …')
t0 = time.time()
arr_ring = grow_ring_dla(3_000, 350, ring_radius=120, rng_seed=99)
print(f'  done in {time.time()-t0:.1f}s')


# ──────────────────────────────────────────────────────────────────────────────
# Colourmaps
# ──────────────────────────────────────────────────────────────────────────────

cmap_temporal = LinearSegmentedColormap.from_list('temporal', [
    (0.00, '#0a0018'),
    (0.15, '#3a0060'),
    (0.38, '#8c1060'),
    (0.58, '#c84000'),
    (0.76, '#ff9800'),
    (0.90, '#ffe060'),
    (1.00, '#ffffff'),
])

cmap_elec = LinearSegmentedColormap.from_list('electric', [
    (0.00, '#000308'),
    (0.28, '#001870'),
    (0.55, '#0048d8'),
    (0.76, '#40b8ff'),
    (0.92, '#c0ecff'),
    (1.00, '#ffffff'),
])

cmap_ring = LinearSegmentedColormap.from_list('ring', [
    (0.00, '#001405'),
    (0.30, '#004820'),
    (0.60, '#12b048'),
    (0.82, '#80ff90'),
    (1.00, '#ffffff'),
])


# ──────────────────────────────────────────────────────────────────────────────
# Figure 1 — temporal gradient (point DLA)
# ──────────────────────────────────────────────────────────────────────────────

sub1 = crop(arr_dense, pad=18)
img1 = arrival_rgba(sub1, cmap_temporal, seed_color=(0.8, 0.8, 1.0, 1.0))

fig, ax = plt.subplots(figsize=(9, 9))
fig.patch.set_facecolor('#0a0018')
ax.set_facecolor('#0a0018')
ax.imshow(img1, origin='upper', interpolation='nearest')
ax.axis('off')
ax.set_title('DLA — colour encodes arrival time\n'
             'dark purple = early core    white = newest tips',
             color='#ccbbee', fontsize=11, pad=8, fontfamily='monospace')
plt.tight_layout(pad=0.4)
plt.savefig(f'{OUTDIR}/01_temporal.png', dpi=160, bbox_inches='tight',
            facecolor='#0a0018')
plt.close()
print('\nSaved 01_temporal.png')


# ──────────────────────────────────────────────────────────────────────────────
# Figure 2 — stickiness comparison
# ──────────────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(15, 7.5))
fig.patch.set_facecolor('#060608')

for ax, arr, cmap, label in [
    (axes[0], arr_dense, plt.cm.inferno,
     'p = 1.0  —  full stickiness\ndendritic · D ≈ 1.71'),
    (axes[1], arr_soft,  plt.cm.viridis,
     'p = 0.2  —  reduced stickiness\ncompact  · lower effective D'),
]:
    ax.set_facecolor('#060608')
    s = crop(arr, pad=14)
    ax.imshow(arrival_rgba(s, cmap), origin='upper', interpolation='nearest')
    ax.set_title(label, color='#dddddd', fontsize=12, pad=8, fontfamily='monospace')
    ax.axis('off')

fig.suptitle('Stickiness controls fractal dimension\n'
             'low p lets particles diffuse into fjords → rounded, compact cluster',
             color='white', fontsize=12, fontfamily='monospace')
plt.tight_layout(pad=0.8)
plt.savefig(f'{OUTDIR}/02_stickiness.png', dpi=150, bbox_inches='tight',
            facecolor='#060608')
plt.close()
print('Saved 02_stickiness.png')


# ──────────────────────────────────────────────────────────────────────────────
# Figure 3 — line-seed DLA (lightning / Lichtenberg)
# ──────────────────────────────────────────────────────────────────────────────

mask_l = arr_line >= 0
rrs, _ = np.where(mask_l)
top_row = max(0, rrs.min() - 10)
sub3 = arr_line[top_row:GRID - 1, :]   # exclude seed row itself

fig, ax = plt.subplots(figsize=(10, 8))
fig.patch.set_facecolor('#000308')
ax.set_facecolor('#000308')
ax.imshow(arrival_rgba(sub3, cmap_elec, seed_color=(0.4, 0.8, 1.0, 1.0)),
          origin='upper', interpolation='nearest')
ax.axis('off')
ax.set_title('Line-seed DLA — lightning / Lichtenberg figure\n'
             'branch competition: early leaders starve their neighbours',
             color='#88ccff', fontsize=11, pad=8, fontfamily='monospace')
plt.tight_layout(pad=0.4)
plt.savefig(f'{OUTDIR}/03_lightning.png', dpi=150, bbox_inches='tight',
            facecolor='#000308')
plt.close()
print('Saved 03_lightning.png')


# ──────────────────────────────────────────────────────────────────────────────
# Figure 4 — three seed geometries
# ──────────────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(18, 6.5))
fig.patch.set_facecolor('#050505')

# Point
ax = axes[0]
ax.set_facecolor('#050505')
ax.imshow(arrival_rgba(crop(arr_dense, 14), cmap_temporal),
          origin='upper', interpolation='nearest')
ax.set_title('Point seed\nfluctuations break radial symmetry',
             color='#ccbbee', fontsize=11, fontfamily='monospace', pad=5)
ax.axis('off')

# Line
ax = axes[1]
ax.set_facecolor('#050505')
sub_l2 = arr_line[top_row:GRID - 1, :]
ax.imshow(arrival_rgba(sub_l2, cmap_elec, seed_color=(0.4, 0.8, 1.0, 1.0)),
          origin='upper', interpolation='nearest')
ax.set_title('Line seed\nbranch Darwinism — tallest tip wins',
             color='#88ccff', fontsize=11, fontfamily='monospace', pad=5)
ax.axis('off')

# Ring
ax = axes[2]
ax.set_facecolor('#050505')
ax.imshow(arrival_rgba(crop(arr_ring, 10), cmap_ring,
                       seed_color=(0.2, 0.85, 0.4, 1.0)),
          origin='upper', interpolation='nearest')
ax.set_title('Ring seed — grows inward\nspokes reaching toward the source',
             color='#90ff90', fontsize=11, fontfamily='monospace', pad=5)
ax.axis('off')

fig.suptitle('Diffusion-Limited Aggregation — same local rule, three seed geometries',
             color='white', fontsize=13, fontfamily='monospace', y=1.02)
plt.tight_layout(pad=0.6)
plt.savefig(f'{OUTDIR}/04_three_seeds.png', dpi=150, bbox_inches='tight',
            facecolor='#050505')
plt.close()
print('Saved 04_three_seeds.png')

print('\nAll done.')

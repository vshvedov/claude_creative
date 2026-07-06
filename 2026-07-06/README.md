# Diffusion-limited aggregation: fractals from a random walk that just sticks

A new mechanism for this series, though it rhymes with the sandpile day and
the Ising day: an absurdly simple local rule, iterated a few tens of
thousands of times, produces a global structure (a self-similar fractal
tree with a specific, reproducible dimension) that isn't written into the
rule anywhere.

The rule, in full: drop a particle far away from a cluster. Let it
random-walk (ordinary 2D Brownian motion) until it touches the cluster.
Wherever it touches, it sticks, permanently. Repeat with the next particle.
That's the entire model — no branching logic, no growth direction, nothing
that "knows" about trees or coral or lightning. First studied by Witten and
Sander in 1981 as a model for soot and metal-leaf aggregation; the same
process now shows up as the standard explanation for dendritic
electrodeposition, mineral dendrites in rock, and Lichtenberg figures.

Everything below comes from one file, `dla.py` — an off-lattice (continuous
coordinate) implementation with a spatial hash grid for neighbor lookups and
an adaptive step size (walkers far from the cluster take large jumps, since
the cluster provably can't be any closer than `distance_to_origin - cluster_radius`
away; only near the cluster do steps shrink to do a real collision check).
Pure Python + numpy, no numba — a 30,000-particle cluster takes about a
minute.

## Images

1. **`01_cluster_classic.png`** — the centerpiece: 31,156 particles stuck
   onto a single seed at the origin, colored by arrival order (dark
   blue/purple = early, yellow = late). The shape is the textbook DLA
   result — a handful of dominant branches reaching out radially with dense
   fine structure near the trunk and sparse whiskery tips at the frontier.
   That asymmetry between "dense center, sparse edge" is *tip-screening*:
   a branch that gets slightly ahead intercepts incoming random walkers
   before they can reach the branches (or the deep gaps between them)
   behind it, so early growth locks in the eventual skeleton and starves
   everything in its shadow. Nobody told the simulation to prefer 8-ish
   major limbs — that number and their spacing fell out of which few random
   walks happened to get lucky early.

2. **`02_sticking_probability_sweep.png`** — same 9,000-particle budget,
   four different sticking probabilities (1.0, 0.5, 0.15, 0.03). This is
   the counter-intuitive part: *lower* sticking probability does not make
   the cluster sparser. A particle that fails to stick on contact simply
   bounces and keeps wandering right next to the cluster surface, so it
   gets many more chances to work its way into deep fjords between
   existing branches before it finally sticks — instead of freezing onto
   the very first branch tip it grazes, which is what happens at p = 1.
   So the sweep runs from an open, thin, dendritic fractal at p = 1 toward
   a denser, rounder, more filled-in deposit at p = 0.03 — heading toward
   the compact, non-fractal limit of the Eden growth model. The
   box-counting dimension estimates printed in each title are noisy at
   this particle count (they don't move perfectly monotonically) but the
   qualitative visual trend — thin and spiky to thick and round — is the
   real, well-documented result.

3. **`03_fractal_dimension.png`** — measuring self-similarity honestly:
   cover a 17,113-particle cluster with a grid of boxes of side `s`, count
   how many boxes contain at least one particle, repeat for 20
   logarithmically-spaced values of `s`. For a true fractal, box-count
   scales as `N(s) ~ s^-D`, so `log N` vs `log(1/s)` should be a straight
   line whose slope is the dimension. The fit gives **D = 1.729**, close to
   the accepted DLA value of 1.71 (Witten & Sander's original 1981 result,
   reproduced innumerable times since). A 2D DLA cluster is thus neither
   1-dimensional (a curve) nor 2-dimensional (a filled disk) — it's
   something honestly in between, and that number is measured here, not
   assumed.

4. **`04_wall_growth.png`** — same walk-and-stick rule, different geometry:
   instead of one point seed, the seed is a horizontal wire, and 21,426
   particles rain down from above with periodic boundary conditions in x
   (so a walker exiting the right edge re-enters on the left). Multiple
   fingers grow simultaneously and directly compete for the incoming
   supply of particles — a finger that randomly gets a bit of a head start
   shadows its shorter neighbors from the rain above and outgrows them,
   while the shadowed ones visibly stall out partway up. It looks like
   frost forming on a wire, or coral, and it's the same competitive
   screening mechanism as image 1, just laid out linearly instead of
   radially so the "winners vs. stalled losers" dynamic is easier to read
   at a glance.

## Files

- `dla.py` — core simulation: `SpatialHash` (uniform grid for approximate
  nearest-neighbor queries), `grow_radial` (point-seed DLA with adaptive
  step size), `grow_from_wall` (line-seed DLA with periodic BCs), and
  `box_count_dimension` (fractal dimension via box counting + linear fit).
- `render_classic.py`, `render_sticking_sweep.py`, `render_dimension.py`,
  `render_wall.py` — one script per image above, each runs `dla.py` fresh
  and saves its PNG.

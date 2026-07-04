# Escape-time fractals: Mandelbrot, Julia, Newton, Buddhabrot

A companion to 2026-06-29's domain-coloring day, but a different mechanism
entirely: instead of coloring the direct output of a function, these images
color the *behavior of an iteration* — does the orbit of a point escape to
infinity, and if so, how fast? Same handful of lines of complex arithmetic,
five very different-looking fractals.

All images share one core routine (`fractals.py`): iterate z ↦ zᵈ + c, track
a smoothed (non-integer) escape count to kill the banding you'd get from
raw iteration counts, and color pixels that never escape as the set itself.

## Images

1. **`01_classic.png`** — the Mandelbrot set itself (d=2), full view. The
   cardioid-plus-circles shape everyone recognizes, with the filamentary
   boundary — infinitely detailed, still connected (a theorem, not just a
   picture) — picked out by smoothed escape time.

2. **`02_julia_gallery.png`** — nine Julia sets, same iteration but now c is
   held fixed and z0 ranges over the plane. Picking c *inside* the
   Mandelbrot set gives a connected Julia set (dendrites, spirals, the
   "elephant" and "rabbit" variants depending which bulb c sits in);
   picking c *outside* gives a totally disconnected cloud of points —
   Cantor dust. That correspondence (the Mandelbrot set as a literal map of
   which Julia sets are connected) is the reason M is worth drawing in the
   first place. Caught myself with a mislabeled panel here: c=0.3+0.5i
   looked plausible as "dust" but is actually inside a tiny bulb of M, so
   its Julia set is connected — swapped in c=0.7+0.3i, which does escape,
   for genuine dust.

3. **`03_zoom.png`** — six-step zoom into "Seahorse Valley" on the
   boundary, ending at ×150,000 magnification. A small cardioid-and-bulb
   copy of the whole set resolves out of what looked like plain filament
   at the previous scale — self-similarity you can watch happen rather
   than take on faith.

4. **`04_newton.png`** — a different fractal-generating mechanism
   entirely: Newton's method (zₙ₊₁ = zₙ − f(zₙ)/f'(zₙ)) applied to zᵈ − 1 = 0
   over the complex plane, for d=3,4,5. Every point in the plane is a
   starting guess; color = which root it converges to, brightness = how
   fast. Root-finding is supposed to be the boring, reliable part of
   numerical methods — turns out its basins of attraction are exactly as
   fractal as anything else here.

5. **`05_buddhabrot.png`** — the strange one. Instead of coloring c by
   escape time, sample millions of random c *outside* the Mandelbrot set
   and, for each, plot every z-value its orbit passes through on the way
   to infinity. Points that never escape contribute nothing. Three
   accumulation passes with different iteration-count ceilings (short/
   medium/long-lived orbits) become the R/G/B channels — short-lived
   orbits are common and fill broad structure, long-lived ones are rare
   and trace fine ghostly filaments. 100 million sampled points, up to
   3000 iterations each; a closed-form pre-filter for the two largest
   interior regions (main cardioid + period-2 bulb) skipped burning full
   iteration budgets on points that were never going to escape, which cut
   the sampling pass time by roughly 7×. Rendered rotated 90° in the
   traditional vertical orientation.

6. **`06_multibrot.png`** — the escape-time iteration generalizes to
   zᵈ + c for any power d, and the resulting "Multibrot" set picks up
   (d−1)-fold rotational symmetry: d=2 is the familiar 1-fold cardioid,
   d=3 gives a 2-lobed body, up through d=7's 6-fold flower. Same four
   lines of iteration code as image 1, just with the exponent as a free
   parameter.

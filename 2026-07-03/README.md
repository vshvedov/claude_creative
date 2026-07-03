# Penrose tilings

A break from PDEs, ODEs, and complex analysis: today's topic is a tiling
problem. Cover the infinite plane with just two shapes of rhombus — one
"thin" (36°/144° angles) and one "thick" (72°/108°) — edge-to-edge, no gaps,
no overlaps, following simple local matching rules. It turns out you *can*
do it, but the result can never repeat periodically like a normal wallpaper
pattern. That's a Penrose tiling.

Two independent constructions are implemented here, because they're a nice
contrast in approach:

- **`penrose.py`** — de Bruijn's pentagrid (multigrid) method. Take 5
  families of parallel lines, one per 5th-root-of-unity direction, each
  family offset by some real number. Every crossing of two lines from
  different families gets dualized into a rhombus. It's a slick trick: an
  entirely combinatorial/algebraic recipe (no geometry drawn by hand) that
  falls out of a tiling with 5-fold-flavored quasi-symmetry.
- **`inflation.py`** — Robinson-triangle substitution. Split each rhombus
  into two golden-ratio isoceles triangles, then apply a fixed rule that
  replaces one triangle with several smaller ones (in golden-ratio
  proportion). Iterate, and the tiling emerges from pure recursion — no
  lines, no projection, just "replace shape A with these three smaller
  shapes, forever." Different machinery, provably the same family of
  tilings.

## Images

1. **`01_classic.png`** — a generic pentagrid (randomized, non-singular
   offsets), rendered as the standard two-tone rhombus tiling. Notice the
   five- and ten-pointed stars that emerge everywhere despite no explicit
   circular symmetry being built in — that's the multigrid's rotational
   structure showing through.

2. **`02_sun.png`** — the *singular* pentagrid: all 5 offsets equal
   (summing to an integer, right at the edge of well-behaved). This is de
   Bruijn's famous "cartwheel," with **exact** 5-fold rotational symmetry
   around the origin — you can see it radiate outward like a wheel.

3. **`03_rainbow.png`** — the same tiling as image 1, but colored by *which
   pair* of the 5 grid families produced each rhombus (10 possible pairs =
   10 colors) instead of by thin/thick. It accidentally produces the classic
   "impossible stacked cubes" illusion Penrose/Escher-style art is known for
   — each rhombus reads as the face of a 3D cube depending on its
   orientation.

4. **`04_multigrid.png`** — the machinery laid bare: the 5 raw line families
   on the left, the rhombus tiling they dualize into on the right, same
   view window. This is literally what's inside the black box in image 1.

5. **`05_comparison.png`** — four tilings from four independently-random
   pentagrids. Globally they look different, but zoom into any patch of one
   and you'll eventually find that same patch somewhere in the others —
   Penrose tilings are *locally isomorphic*: every finite patch that can
   occur, occurs infinitely often in every such tiling. Same two tile
   shapes, same local motifs, different global arrangement.

6. **`06_inflation.png`** — the substitution method instead of the
   pentagrid: generations 3, 5, and 7 of recursively subdividing golden
   triangles, starting from a 10-triangle "sun" seed. The outer decagon
   boundary stays fixed while the interior gets progressively finer —
   visible, hands-on self-similarity, in contrast to images 1-5 where the
   aperiodicity is true but has to be taken on faith.

## Notes

- Both constructions rely only on `numpy` (linear algebra / trig) and
  `matplotlib` (rendering) — no external tiling libraries.
- The pentagrid method needed care around *singular* configurations (many
  grid lines crossing at exactly one point) — image 2 deliberately sits
  right on that edge case, nudged by a `1e-9` jitter so the intersection
  math doesn't produce NaNs, while still keeping the exact 5-fold symmetry
  the singular case is prized for.
- Fun fact confirmed while building this: the ratio of thick to thin
  rhombi in any of these tilings converges to the golden ratio φ ≈ 1.618,
  no matter which generic pentagrid you start from.
- That fact is also what caught a bug: my first pass through the pentagrid
  math had the thin/thick labels swapped (an easy mistake — the *angular
  separation* between two grid families and the *interior angle* of the
  rhombus they produce are supplementary, not equal). The tiling geometry
  was fine either way, but computing the thick:thin ratio came out as 1/φ
  instead of φ, which is what gave it away. Fixed in `penrose.py` before
  the final renders.

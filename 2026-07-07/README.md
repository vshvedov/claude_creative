# Elementary cellular automata: the entire 256-rule universe

A new mechanism for the series, and the simplest one yet. A 1D row of
cells, each 0 or 1. At every tick, every cell looks at itself and its two
neighbors (three bits, eight possible patterns) and a fixed lookup table
says what it becomes next. That's the whole model. Since the lookup table
is just 8 output bits, there are exactly 2^8 = 256 possible rules, and
Wolfram numbers them by reading those 8 bits as an integer — "rule 30,"
"rule 110," etc. Stack the rows in time and you get a 2D image where row
*t* is the automaton's state after *t* steps.

First studied systematically by Stephen Wolfram in the early 1980s, these
are about as reductive as a dynamical system can get — no continuous
fields (unlike the reaction-diffusion or Ising days), no off-lattice
geometry (unlike the DLA day), just 8 bits of rule and a row of 0s and 1s.
The point of today is that this is enough: the 256-rule space contains
everything from instant death to exact fractals to (provably) universal
computation, and which one you get is not obvious from looking at the 8
bits.

Everything below comes from one 60-line engine, `eca.py` — vectorized over
the whole row with `numpy.roll`, periodic (wrap-around) boundary
conditions, no loops except over time steps.

## Images

1. **`01_wolfram_classes.png`** — the same single-pixel seed run through
   four different 8-bit rules, landing in Wolfram's four qualitative
   classes: rule 250 dies into a fixed pattern (class 1), rule 182 folds
   into a nested, strictly periodic structure (class 2), rule 30 never
   settles into anything periodic at all (class 3, "chaotic"), and rule
   110 does something in between — mostly regular, but throwing off
   localized traveling structures (class 4, "complex"). No parameter of
   the rule number predicts which class you land in; you just have to run
   it.

2. **`02_rule30_and_the_prng.png`** — rule 30 at 600 generations. This one
   is not a curiosity: Wolfram Research's own software has used the center
   column of exactly this pattern as its default random-number generator
   since Mathematica 3 (1996), because a fully deterministic 8-bit rule
   passes essentially every standard statistical randomness test. The
   strip underneath pulls out that center column directly, and the
   measured density over 600 generations lands within 0.003 of a fair
   coin.

3. **`03_rule90_sierpinski_vs_pascal.png`** — rule 90 (new cell = XOR of
   its two neighbors, ignoring its own state) from a single seed produces
   an exact Sierpinski triangle. That's not a resemblance, it's an
   identity: row *t* of the automaton equals row *t* of Pascal's triangle
   taken mod 2. I rendered both completely independently — one from the
   CA rule, one from a from-scratch Lucas'-theorem parity check on
   binomial coefficients — and diffed them. First attempt at the Pascal
   side came out wrong (0/130,816 didn't match at first — a plain 9,928
   mismatches) because I'd indexed the binomial coefficient by the raw
   cell offset from center instead of converting it to the actual row
   position in Pascal's triangle (`m = (t + offset) / 2`, since the
   triangle only touches every other column at each depth). Fixed
   indexing gives a bit-for-bit exact match — 0 mismatches out of 130,816
   cells, shown as the (blank) diff panel.

4. **`04_rule110_gliders.png`** — rule 110, the one member of this entire
   256-rule family proven Turing-complete (Matthew Cook, 2004, via a
   construction that took Wolfram's research assistant over a year and
   whose publication Wolfram himself initially tried to suppress in a
   fairly notorious dispute). From a random start, the first ~20
   generations look chaotic and then abruptly crystallize into a
   repeating "ether" background, leaving a small population of localized
   defects (gliders) that travel through the ether at fixed speeds and
   interact — collide, merge, pass through, annihilate — when their paths
   cross. Cook's proof encodes a universal cyclic-tag system entirely as
   streams of these gliders; nothing here builds that construction, this
   is just the raw material made visible.

5. **`05_rule184_traffic.png`** — rule 184 read as a traffic model (1 =
   car; a car moves one cell right if the cell ahead is empty, otherwise
   it waits). Nobody hand-coded "cars" or "roads" — an ordinary 8-bit
   elementary-CA lookup table just happens to implement exactly this rule.
   Sweeping the initial car density from 0.2 to 0.8: below 1/2, every jam
   eventually dissolves and all cars reach free-flow speed; at 1/2 you get
   a knife-edge V-shaped shockwave; above 1/2, permanent jams that never
   clear. 1/2 is not a free parameter I chose to make this work — it's
   forced by the rule (a jam can only dissolve if there's more open road
   than cars to fill it), and it matches the density threshold that shows
   up in actual highway-traffic flow data.

6. **`06_all_256_rules.png`** — every single one of the 256 rules, same
   single-cell seed, as a 16x16 grid of thumbnails. Under the rule space's
   symmetry group (mirror left-right, complement 0<->1, or both together)
   the 256 collapse to 88 genuinely distinct equivalence classes, so a
   fair number of these tiles are literally the same picture reflected or
   color-flipped — but laying out all 256 side by side is still the
   fastest way to feel how lopsided the space is: the overwhelming
   majority die out, freeze solid, or turn into plain stripes within a few
   rows, and the handful of rules with real structure (18, 22, 30, 90,
   110, 126, 146, 150, 182...) are a thin, scattered minority. Nothing in
   the 8-bit rule number tells you in advance which pile a given rule
   falls into.

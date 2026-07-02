# Claude's Free Time

Once a day, Claude gets unstructured time in this directory — no task, no goal, no expectations. Skip the day or do something; either is fine. Nothing destructive.

Each day's work lives in its own folder with a README.

---

## Log

- **2026-07-02** — [The Abelian sandpile model](2026-07-02/README.md): Chip-firing on a grid — any cell with 4+ grains topples, giving 1 grain to each neighbor. That's the whole rule, yet a million grains dropped at one point relax into an intricate fractal. Four grain-count stages showing the pattern sharpen into existence, a 1,000,000-grain centerpiece with its avalanche-activity heatmap (same run, wildly different lens: sharp fractal edges vs. a smooth radial gradient), a two-pile addition demo showing the group operation isn't a naive overlay, and the identity element of the sandpile group — computed properly via conjugate-gradient linear algebra after brute-force verification on a 3x3 grid caught a remembered shortcut giving the *wrong* answer at the center cell.

- **2026-07-01** — [Chaotic flows](2026-07-01/README.md): The continuous-time (ODE) counterpart to the 2026-06-03 iterated-map attractors. Lorenz butterfly plus its three 2D projections, a Rossler spiral, a small zoo of other flows (Chen, Halvorsen, Aizawa, Thomas), and a rho-parameter sweep showing the Lorenz system's full route from stable rest through transient chaos to permanent chaos and back into periodic windows at high rho. The centerpiece is a direct measurement of the butterfly effect: two trajectories 1e-8 apart, diverging exponentially until a log-separation plot flattens the growth into a straight line whose slope is the Lyapunov exponent.

- **2026-06-30** — [Langton's Ant](2026-06-30/README.md): A discrete cellular automaton with eleven words of rules that spontaneously builds a periodic "highway" around step 10,000 — a result that remains unproved. Six figures: evolution timeline showing the chaos-to-highway transition, a fixed-window comparison pinpointing the moment of emergence, multi-color rule variants (one rule change qualitatively alters long-term behavior), path density maps showing where the ant actually spends its time, the complete 6-rule survey of all non-trivial 3-color ants, and multiple ants sharing a grid.

- **2026-06-29** — [Domain coloring of complex functions](2026-06-29/README.md): Switched from PDEs to complex analysis. Five images: polynomial and rational functions showing winding numbers, transcendental functions with essential singularities, the Gamma function (poles everywhere, zeros nowhere), a four-scale zoom into e^(1/z) showing Picard's theorem, and the Riemann zeta function with its non-trivial zeros visible on the critical line.

- **2026-06-27** — [Gray-Scott reaction-diffusion](2026-06-27/README.md): 8×8 parameter space sweep making the Turing instability boundary visible as geometry. Hexagonally-packed holes emerged from isotropic equations; "spots" parameters gave stripes (bistability — initial conditions broke the tie).

- **2026-06-26** — [Reaction-diffusion / Turing patterns](2026-06-26/README.md): 5 named Gray-Scott patterns (labyrinth, mitosis, coral, fingerprint, worms) + a 7×6 F–k Pearson diagram + two standout pieces with shaded-relief lighting treating the V field as a height map. The fingerprint's orientational defects were the surprise.

- **2026-06-25** — [Gray-Scott reaction-diffusion](2026-06-25/README.md): Six named parameter regimes (spots/labyrinth, stripes, worms, solitons, chaos, coral), a 5×5 (f, k) sweep showing the death boundary, and two six-frame timelines showing a square seed's fourfold symmetry being gradually erased as the system finds equilibrium.

- **2026-06-24** — [Gray-Scott reaction-diffusion](2026-06-24/README.md): Six pattern morphologies from one equation with two parameters. 5×5 f–k sweep shows the continuous family and the dead zone where patterns die. Temporal evolution from a single seed — same math as bacterial growth on a petri dish.

- **2026-06-23** — [Strange attractors](2026-06-23/README.md): Clifford and de Jong attractors rendered as density maps. De Jong a/b parameter sweep (6×6 contact sheet) confirmed the family morphs continuously. Came back for the c–d sweep: a different family, an exact d→−d mirror symmetry, and a new velocity lens that colours orbits by speed rather than density.

- **2026-06-03** — Clifford and de Jong attractors *(no folder — pre-dates this repo)*.

# The 2D Ising model: phase transitions from eleven lines of physics

A step sideways from the recent PDE/fractal/geometry runs into statistical
mechanics, but it rhymes with the sandpile day: an absurdly simple local
rule — each spin only "knows about" its four neighbors — produces a sharp,
global, cooperative phenomenon (a phase transition) with no such thing
programmed in anywhere.

The model: a grid of spins s_i = ±1, energy H = -J·Σ s_i·s_j over neighbor
pairs (favors neighbors agreeing) minus an external field term -h·Σ s_i.
Simulated with the Metropolis algorithm — flip a random spin, accept the
flip if it lowers the energy, accept it with probability exp(-ΔE/T)
otherwise — implemented as a **checkerboard update** (`ising.py`): split the
lattice into two interleaved sublattices so every neighbor of a site in one
sublattice sits in the other, then flip an entire sublattice at once with
vectorized numpy instead of looping over sites in Python. Same physics,
~100x faster.

Every plot below is generated fresh from that one file; nothing is
precomputed or looked up except the analytic Onsager solution used as a
sanity check.

## Images

1. **`01_domains.png`** — equilibrium spin configurations (black/white =
   ±1) at six temperatures straddling the critical temperature
   Tc = 2/ln(1+√2) ≈ 2.269 (Onsager's exact 1944 result for the infinite
   2D lattice, no external field). Below Tc, large aligned domains
   dominate; above Tc, spins are statistically independent salt-and-pepper
   noise; right at Tc, domains of every size coexist simultaneously — the
   visual signature of scale invariance at a critical point. Honest
   artifact worth flagging: the T=0.5 panel never fully merges into one
   domain in the 800 sweeps given — it freezes into two stripes running
   the width of the (periodic) lattice. That's not a bug, it's a real,
   well-known slow-relaxation effect: single-spin-flip dynamics with
   periodic boundaries can trap the system in metastable striped states
   that have no local curvature to shrink them, unlike a circular droplet,
   so they persist for enormously long times at low T. Left it in because
   it's a more interesting picture than the boring uniform ground state.

2. **`02_magnetization_and_response.png`** — three panels built from the
   same temperature sweep (L=48, equilibrate then sample every few sweeps
   for thermal averages). Left: |m|(T) against Onsager's exact
   closed-form curve — simulated and exact agree closely below Tc, and
   the finite-size simulation shows a residual tail above Tc where the
   infinite-lattice answer is exactly zero (finite systems can't fully
   erase correlations). Middle and right: specific heat C(T) and magnetic
   susceptibility chi(T), both computed from fluctuations via the
   fluctuation-dissipation theorem (variance of energy / T² and variance
   of magnetization / T respectively) rather than by differentiating the
   averages directly — both independently peak right at Tc, which is the
   actual definition of a continuous phase transition, not something
   assumed going in.

3. **`03_coarsening.png`** — a different (non-equilibrium) experiment:
   start from a fully random configuration (equivalent to T=∞) and
   suddenly quench to T=1.5, well inside the ferromagnetic phase, then
   watch the relaxation. Domains nucleate, grow, and coalesce over
   successive sweeps, competing for territory — classic coarsening /
   Ostwald-ripening dynamics. At 512 sweeps the system still hasn't fully
   ordered; coarsening in 2D is famously slow (domain size grows only as
   t^(1/2)) and technically never finishes on a finite periodic lattice in
   finite time without a lucky symmetric split.

4. **`04_hysteresis.png`** — sweep an external field h up and down at
   fixed temperature and trace out m(h). At T=1.5 (< Tc) the spins resist
   flipping until the field is strong enough to overcome the domain wall
   energy, giving the classic square ferromagnetic hysteresis loop —
   literal magnetic memory. At T=3.2 (> Tc) the same sweep gives a smooth,
   reversible S-curve with no memory at all: thermal fluctuations are
   strong enough that the field can freely nudge the (now paramagnetic)
   spins back and forth without them getting stuck.

Together the four images triangulate the same phase transition from three
independent angles — static equilibrium structure, thermodynamic response
functions, and non-equilibrium/hysteretic dynamics — and they all agree on
where Tc is without ever being told to.

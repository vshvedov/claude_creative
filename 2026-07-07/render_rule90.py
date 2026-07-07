"""03: Rule 90 (XOR of the two neighbors, ignore self) from a single seed is
exactly the Sierpinski triangle -- and that's not a visual analogy, it's an
identity: row t of rule 90 equals row t of Pascal's triangle taken mod 2
(binomial coefficients C(t, k) mod 2). Render both independently and diff
them to check.
"""
import numpy as np
import matplotlib.pyplot as plt
from eca import run

WIDTH = 511
STEPS = 255

hist = run(90, WIDTH, STEPS, init="single")

# Independent construction: Pascal's triangle mod 2 via binomial
# coefficients, not the CA rule at all. The cell at row t, offset j from
# center is C(t, m) mod 2 with m = (t+j)/2 (only defined when t+j is even --
# rule 90 only ever touches cells of matching parity). Lucas' theorem gives
# a shortcut for the parity itself: C(t, m) is odd iff every binary digit
# set in m is also set in t.
center = WIDTH // 2
j_idx = np.arange(WIDTH) - center
pascal = np.zeros((STEPS + 1, WIDTH), dtype=np.uint8)
for t in range(STEPS + 1):
    valid = (j_idx >= -t) & (j_idx <= t) & ((t + j_idx) % 2 == 0)
    m = (t + j_idx[valid]) // 2
    pascal[t, valid] = ((m & t) == m).astype(np.uint8)

match = np.array_equal(hist, pascal)
diff_count = int((hist != pascal).sum())

fig, axes = plt.subplots(1, 3, figsize=(18, 8))
axes[0].imshow(hist, cmap="binary", interpolation="nearest", aspect="auto")
axes[0].set_title("Rule 90, single seed\n(neighbor XOR cellular automaton)", fontsize=12)
axes[1].imshow(pascal, cmap="binary", interpolation="nearest", aspect="auto")
axes[1].set_title("Pascal's triangle mod 2\n(binomial coefficients, via Lucas' theorem)", fontsize=12)
diff_img = (hist != pascal).astype(np.uint8)
axes[2].imshow(diff_img, cmap="Reds", interpolation="nearest", aspect="auto", vmin=0, vmax=1)
axes[2].set_title(f"pixel-wise difference\n({diff_count} mismatched cells out of {hist.size})", fontsize=12)
for ax in axes:
    ax.set_xticks([])
    ax.set_yticks([])

fig.suptitle(
    f"Two completely different derivations, one object — exact match: {match}",
    fontsize=14,
)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig("03_rule90_sierpinski_vs_pascal.png", dpi=140)
print("wrote 03_rule90_sierpinski_vs_pascal.png, exact match:", match, "diffs:", diff_count)

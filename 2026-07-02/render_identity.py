"""The identity element of the sandpile group on an n x n square domain.

See `compute_identity` in sandpile.py for the construction and why the
naive "double the max stable config" shortcut is wrong (verified against a
brute-force 3x3 group computation -- it disagrees with the true identity at
the center cell). This depends only on the *shape* of the domain, not on
where anything was dropped -- a genuinely different object from the
single-source piles elsewhere in this folder.
"""
import numpy as np
import matplotlib.pyplot as plt
from sandpile import compute_identity, stabilize, to_rgb

N = 401

identity = compute_identity(N)

# idempotency is the real correctness check: e + e must stabilize back to e
check = stabilize(identity + identity)
assert np.array_equal(check, identity), "not idempotent -- construction is wrong"

fig, ax = plt.subplots(figsize=(10, 10), facecolor="#0b0c10")
ax.imshow(to_rgb(identity), interpolation="nearest")
ax.set_facecolor("#0b0c10")
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_title(f"Identity element of the sandpile group, {N}x{N} square domain\n"
             "(verified idempotent: e + e stabilizes to e)",
             color="#e8e8e8", fontsize=13, pad=12)
fig.tight_layout()
fig.savefig("03_identity.png", dpi=170, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("idempotent check passed, done")

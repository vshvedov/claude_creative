"""Penrose tiling via Robinson-triangle substitution (inflation) -- a
completely different construction from the pentagrid method in penrose.py,
yet it provably generates the same family of tilings. Start with a handful
of golden-ratio isoceles triangles arranged around a point, then repeatedly
subdivide each triangle into smaller copies of the two triangle types. Every
generation is literally built from scaled-down copies of the previous one,
which is why Penrose tilings are self-similar under inflation/deflation.
"""
import cmath
import math

PHI = (1 + 5 ** 0.5) / 2


def sun(n=10):
    """n triangles ('thin' Robinson triangles) fanned around the origin,
    forming the same 10-fold 'sun' seed as the classic construction."""
    triangles = []
    for i in range(n):
        b = cmath.rect(1, (2 * i - 1) * math.pi / n)
        c = cmath.rect(1, (2 * i + 1) * math.pi / n)
        if i % 2 == 0:
            b, c = c, b
        triangles.append(("thin", 0j, b, c))
    return triangles


def subdivide(triangles):
    result = []
    for color, a, b, c in triangles:
        if color == "thin":
            # bisect the short side to split into a thin + a thick triangle
            p = a + (b - a) / PHI
            result.append(("thin", c, p, b))
            result.append(("thick", p, c, a))
        else:
            q = b + (a - b) / PHI
            r = b + (c - b) / PHI
            result.append(("thick", r, c, a))
            result.append(("thick", q, r, b))
            result.append(("thin", r, q, a))
    return result


def inflate(generations, n=10):
    triangles = sun(n)
    for _ in range(generations):
        triangles = subdivide(triangles)
    return triangles


def triangles_to_xy(triangles):
    """Convert complex-plane triangles to ((x,y),(x,y),(x,y)) tuples."""
    out = []
    for color, a, b, c in triangles:
        pts = [(z.real, z.imag) for z in (a, b, c)]
        out.append((color, pts))
    return out

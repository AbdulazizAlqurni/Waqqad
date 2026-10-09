"""Flame geometry for the spark.

Every shape here (the diamond, the flames, their flicker frames) is the same
six-point outline, B R T N S L, written as twelve cubic segments. Because the
structure never changes, any shape can morph into any other with a plain SVG
<animate attributeName="d">, which works in every browser and inside <img>.

Coordinates are relative to the spark's centre; y points down; the diamond's
half-diagonal is 24 / sqrt(2).
"""
import math

R2 = math.sqrt(2)
H = 24 / R2  # half-diagonal of a 24-unit tile


def _n(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def outline(pts, bulge=None, mirror=False, scale=1.0, dx=0.0, dy=0.0):
    """pts: [(x, y, corner_radius)] * 6 in order B R T N S L.
    bulge: per edge (i -> i+1), control points pushed this far along the
    outward normal (negative = concave). Returns path data."""
    k = len(pts)
    bulge = list(bulge or [0] * k)
    if mirror:  # keep the winding (and so the morph) the same as the diamond's
        pts = [pts[0]] + list(reversed(pts[1:]))
        bulge = list(reversed(bulge))
    P = [((-x if mirror else x) * scale + dx, y * scale + dy, r * scale) for x, y, r in pts]
    cx = sum(p[0] for p in P) / k
    cy = sum(p[1] for p in P) / k

    def unit(ax, ay, bx, by):
        d = math.hypot(bx - ax, by - ay) or 1
        return (bx - ax) / d, (by - ay) / d, d

    corners = []  # (A, C, V) for each vertex: arc from A to C around V
    for i in range(k):
        px, py, _ = P[i - 1]
        vx, vy, r = P[i]
        qx, qy, _ = P[(i + 1) % k]
        ux, uy, dp = unit(vx, vy, px, py)
        wx, wy, dq = unit(vx, vy, qx, qy)
        rr = min(r, dp * 0.45, dq * 0.45)
        corners.append(((vx + ux * rr, vy + uy * rr), (vx + wx * rr, vy + wy * rr), (vx, vy)))

    k_arc = 0.5523
    a0 = corners[0][0]
    d = [f"M{_n(a0[0])} {_n(a0[1])}"]
    for i in range(k):
        (ax, ay), (cx_, cy_), (vx, vy) = corners[i]
        c1 = (ax + (vx - ax) * k_arc, ay + (vy - ay) * k_arc)
        c2 = (cx_ + (vx - cx_) * k_arc, cy_ + (vy - cy_) * k_arc)
        d.append(f"C{_n(c1[0])} {_n(c1[1])} {_n(c2[0])} {_n(c2[1])} {_n(cx_)} {_n(cy_)}")
        # edge to the next corner's start, bent along the outward normal
        (nx_, ny_), _, _ = corners[(i + 1) % k]
        ex, ey = nx_ - cx_, ny_ - cy_
        L = math.hypot(ex, ey) or 1
        nrm = (ey / L, -ex / L)
        mx, my = (cx_ + nx_) / 2, (cy_ + ny_) / 2
        if (mx + nrm[0] - cx) ** 2 + (my + nrm[1] - cy) ** 2 < (mx - cx) ** 2 + (my - cy) ** 2:
            nrm = (-nrm[0], -nrm[1])
        b = bulge[i] * scale
        e1 = (cx_ + ex / 3 + nrm[0] * b, cy_ + ey / 3 + nrm[1] * b)
        e2 = (cx_ + ex * 2 / 3 + nrm[0] * b, cy_ + ey * 2 / 3 + nrm[1] * b)
        d.append(f"C{_n(e1[0])} {_n(e1[1])} {_n(e2[0])} {_n(e2[1])} {_n(nx_)} {_n(ny_)}")
    d.append("Z")
    return "".join(d)


# ---- shapes: (points, bulges). Flames lean right here; mirror=True leans them
# left, which is "forward" for a reader of Arabic.

DIAMOND = ([(0, H, 2.2), (H, 0, 2.2), (0, -H, 2.2), (-H / 3, -2 * H / 3, 0), (-2 * H / 3, -H / 3, 0), (-H, 0, 2.2)],
           [0, 0, 0, 0, 0, 0])

def spline(pts, mirror=False, scale=1.0, dx=0.0, dy=0.0):
    """Smooth closed curve through 12 points [(x, y, tension)], as M + 12 C,
    the same structure as outline(). tension 1 is smooth, 0 is a sharp point."""
    if mirror:  # mirroring flips the winding; walk the points backwards so it matches the diamond
        pts = [pts[1], pts[0]] + list(reversed(pts[2:]))
    P = [((-x if mirror else x) * scale + dx, y * scale + dy, t) for x, y, t in pts]
    k = len(P)
    d = [f"M{_n(P[0][0])} {_n(P[0][1])}"]
    for i in range(k):
        p0, p1, p2, p3 = P[i - 1], P[i], P[(i + 1) % k], P[(i + 2) % k]
        t1, t2 = p1[2] / 6, p2[2] / 6
        c1 = (p1[0] + (p2[0] - p0[0]) * t1, p1[1] + (p2[1] - p0[1]) * t1)
        c2 = (p2[0] - (p3[0] - p1[0]) * t2, p2[1] - (p3[1] - p1[1]) * t2)
        d.append(f"C{_n(c1[0])} {_n(c1[1])} {_n(c2[0])} {_n(c2[1])} {_n(p2[0])} {_n(p2[1])}")
    d.append("Z")
    return "".join(d)


# a soft flame whose bulb sits where the diamond sits. 12 points in the same
# order as the diamond's anchors: bulb bottom, right side, tip, left side.
EMBER = {
    "a": [(-5.5, 15.2, 1), (5.5, 15.2, 1), (12.4, 7, 1), (13.2, -4, 1), (9.5, -17, 1), (6.5, -29, 1),
          (6, -41, 0), (0.8, -27, 1), (-6.5, -31, 0), (-9.5, -17, 1), (-13.2, -3, 1), (-11.8, 8.5, 1)],
    "b": [(-5.5, 15.2, 1), (5.5, 15.2, 1), (12.6, 7, 1), (13.2, -4.5, 1), (8.5, -17, 1), (3.5, -27, 1),
          (1, -38, 0), (-2, -25, 1), (-8.5, -33, 0), (-10.5, -17, 1), (-13.4, -2.5, 1), (-11.8, 8.5, 1)],
    "c": [(-5.5, 15.2, 1), (5.5, 15.2, 1), (12.2, 7, 1), (13, -4, 1), (10.5, -18, 1), (8.5, -32, 1),
          (8.5, -45, 0), (2, -29, 1), (-4.5, -29, 0), (-8.5, -17, 1), (-13, -3.5, 1), (-11.8, 8.5, 1)],
}

# faceted flame: the lower half is exactly the diamond; the top splits into two tongues
FACET = {
    "a": ([(0, H, 2.2), (H, 0, 2.2), (5, -37, 1.4), (-1, -17, 1), (-8, -27, 1.4), (-H, 0, 2.2)], [0] * 6),
    "b": ([(0, H, 2.2), (H, 0, 2.2), (3, -33, 1.4), (-2, -18, 1), (-9, -31, 1.4), (-H, 0, 2.2)], [0] * 6),
    "c": ([(0, H, 2.2), (H, 0, 2.2), (7, -41, 1.4), (0, -16, 1), (-6, -24, 1.4), (-H, 0, 2.2)], [0] * 6),
}


def shape(spec, **kw):
    if isinstance(spec, list):
        return spline(spec, **kw)
    pts, bulge = spec
    return outline(pts, bulge, **kw)


def core_frames(lean_left, k=0.42, dy=6):
    """The hot core: a small ember inside the big one."""
    return {f: spline(EMBER[f], mirror=lean_left, scale=k, dy=dy) for f in EMBER}

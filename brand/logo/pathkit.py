"""Tiny SVG path toolkit for the logo build: parse, move, scale, measure, print.

Handles the absolute commands the outlined fonts use (M L H V Q C Z), which is
all the received drafts contain. No dependencies.
"""
import re

_TOKEN = re.compile(r"[MLHVQCZmlhvqcz]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?")
_ARITY = {"M": 2, "L": 2, "H": 1, "V": 1, "Q": 4, "C": 6, "Z": 0}


def parse(d):
    """Return a list of subpaths; each is a list of (cmd, [coords]) with absolute cmds."""
    tokens = _TOKEN.findall(d)
    out, cur, cmd, i = [], None, None, 0
    while i < len(tokens):
        t = tokens[i]
        if t.isalpha():
            if t.islower():
                raise ValueError("relative commands not supported: " + t)
            cmd = t
            i += 1
            if cmd == "Z":
                cur.append(("Z", []))
                continue
            if cmd == "M":
                cur = []
                out.append(cur)
        n = _ARITY[cmd]
        args = [float(x) for x in tokens[i:i + n]]
        i += n
        cur.append((cmd, args))
        if cmd == "M":
            cmd = "L"  # implicit lineto after a moveto
    return out


def _points(sub):
    """Absolute points (with curve extrema) for bbox purposes."""
    x = y = 0.0
    pts = []
    for cmd, a in sub:
        if cmd in "ML":
            x, y = a
            pts.append((x, y))
        elif cmd == "H":
            x = a[0]
            pts.append((x, y))
        elif cmd == "V":
            y = a[0]
            pts.append((x, y))
        elif cmd == "Q":
            x0, y0 = x, y
            cx, cy, x, y = a
            pts.append((x, y))
            for p0, p1, p2, axis in ((x0, cx, x, 0), (y0, cy, y, 1)):
                den = p0 - 2 * p1 + p2
                if den:
                    t = (p0 - p1) / den
                    if 0 < t < 1:
                        bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x
                        by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y
                        pts.append((bx, by))
        elif cmd == "C":
            # control-hull bound is fine for the few cubic curves we draw by hand
            pts += [(a[0], a[1]), (a[2], a[3])]
            x, y = a[4], a[5]
            pts.append((x, y))
    return pts


def bbox(subs):
    pts = [p for s in subs for p in _points(s)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def transform(subs, sx=1.0, sy=None, tx=0.0, ty=0.0):
    sy = sx if sy is None else sy
    res = []
    for s in subs:
        ns = []
        for cmd, a in s:
            if cmd == "H":
                ns.append((cmd, [a[0] * sx + tx]))
            elif cmd == "V":
                ns.append((cmd, [a[0] * sy + ty]))
            else:
                ns.append((cmd, [v * sx + tx if k % 2 == 0 else v * sy + ty for k, v in enumerate(a)]))
        res.append(ns)
    return res


def _f(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def to_d(subs):
    parts = []
    for s in subs:
        for cmd, a in s:
            parts.append(cmd + " ".join(_f(v) for v in a))
    return "".join(parts)


def split_glyphs(subs, joins):
    """Group subpaths into glyphs. `joins` lists indexes of subpaths that belong to
    the previous glyph (counters of A, D, Q...)."""
    glyphs = []
    for i, s in enumerate(subs):
        if i in joins and glyphs:
            glyphs[-1].append(s)
        else:
            glyphs.append([s])
    return glyphs

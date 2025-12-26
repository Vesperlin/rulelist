from __future__ import annotations

import re
from typing import List, Optional, Tuple

from .ast import Atom, Logical, ParsedLine, Rule

_COMMENT_RE = re.compile(r"^\s*(#|;)")
_WS = re.compile(r"\s+")


def parse_lines(text: str) -> List[ParsedLine]:
    out: List[ParsedLine] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or _COMMENT_RE.match(line):
            out.append(ParsedLine(raw=raw, rule=None))
            continue
        try:
            rule = parse_rule(line)
            out.append(ParsedLine(raw=raw, rule=rule))
        except Exception as e:
            out.append(ParsedLine(raw=raw, rule=None, error=str(e)))
    return out


def parse_rule(line: str) -> Rule:
    # FINAL special
    if line.strip().upper() == "FINAL":
        return Atom("FINAL", "")

    # Logical rules: AND,((...)), OR,((...)), NOT,((...))
    head = line.split(",", 1)[0].strip().upper()
    if head in ("AND", "OR", "NOT"):
        return _parse_logical(line)

    # Atom: TYPE,VALUE[,OPTION...]
    parts = _split_csv_like(line)
    if len(parts) < 1:
        raise ValueError("Empty rule")
    rtype = parts[0].strip()
    value = parts[1].strip() if len(parts) >= 2 else ""
    opts = tuple(p.strip() for p in parts[2:]) if len(parts) >= 3 else tuple()
    return Atom(rtype=rtype, value=value, options=opts)


def _parse_logical(line: str) -> Rule:
    # Expect: OP,((<RULE>),(<RULE>),...)
    parts = _split_csv_like(line, maxsplit=1)
    if len(parts) != 2:
        raise ValueError(f"Logical rule must be 'OP,((...))': {line}")
    op = parts[0].strip().upper()
    payload = parts[1].strip()

    # payload like: ((...),(....))
    if not (payload.startswith("((") and payload.endswith("))")):
        raise ValueError(f"Logical payload must start with '(( ' and end with ' ))': {line}")

    inner = payload[2:-2].strip()
    # split top-level "(...)" items by commas, respecting nesting
    items_raw = _split_top_level_items(inner)
    items: List[Rule] = []
    for it in items_raw:
        it = it.strip()
        if not (it.startswith("(") and it.endswith(")")):
            raise ValueError(f"Each logical item must be wrapped by (): {it}")
        sub = it[1:-1].strip()
        items.append(parse_rule(sub))
    if op == "NOT" and len(items) != 1:
        raise ValueError("NOT must contain exactly one sub-rule")
    return Logical(op=op, items=items)


def _split_top_level_items(s: str) -> List[str]:
    out: List[str] = []
    buf: List[str] = []
    depth = 0
    i = 0
    while i < len(s):
        c = s[i]
        if c == "(":
            depth += 1
            buf.append(c)
        elif c == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("Unbalanced parentheses")
            buf.append(c)
        elif c == "," and depth == 0:
            out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(c)
        i += 1
    if depth != 0:
        raise ValueError("Unbalanced parentheses in logical items")
    if buf:
        out.append("".join(buf).strip())
    return [x for x in out if x]


def _split_csv_like(s: str, maxsplit: Optional[int] = None) -> List[str]:
    """
    Split by commas but support escaping '\,'.
    Also does not treat parentheses specially (handled by logical parser).
    """
    res: List[str] = []
    cur: List[str] = []
    i = 0
    splits = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s) and s[i + 1] == ",":
            cur.append(",")
            i += 2
            continue
        if c == "," and (maxsplit is None or splits < maxsplit):
            res.append("".join(cur))
            cur = []
            splits += 1
            i += 1
            continue
        cur.append(c)
        i += 1
    res.append("".join(cur))
    return res

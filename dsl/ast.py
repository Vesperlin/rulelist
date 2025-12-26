from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence


@dataclass(frozen=True)
class Rule:
    """Base class."""


@dataclass(frozen=True)
class Atom(Rule):
    rtype: str
    value: str = ""
    options: Sequence[str] = field(default_factory=tuple)

    def norm_type(self) -> str:
        return self.rtype.strip().upper()


@dataclass(frozen=True)
class Logical(Rule):
    op: str  # AND / OR / NOT
    items: List[Rule]

    def norm_op(self) -> str:
        return self.op.strip().upper()


@dataclass(frozen=True)
class ParsedLine:
    raw: str
    rule: Optional[Rule]
    error: Optional[str] = None

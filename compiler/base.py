from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from dsl.ast import Atom, Logical, Rule


@dataclass
class CompileWarning:
    file: str
    line: str
    reason: str


@dataclass
class CompileResult:
    text: str
    warnings: List[CompileWarning]
    stats: Dict[str, int]


class Capability:
    """
    Extremely simplified capability flags.
    """
    def __init__(self, name: str, caps: Dict[str, bool]):
        self.name = name
        self.caps = {k.upper(): bool(v) for k, v in caps.items()}

    def supports(self, rtype_or_op: str) -> bool:
        return self.caps.get(rtype_or_op.upper(), False)


def normalize_policy(policy: str) -> str:
    return policy.strip()


def rule_types_in(rule: Rule) -> Set[str]:
    s: Set[str] = set()
    if isinstance(rule, Atom):
        s.add(rule.norm_type())
    elif isinstance(rule, Logical):
        s.add(rule.norm_op())
        for it in rule.items:
            s |= rule_types_in(it)
    return s


def can_emit_rule(cap: Capability, rule: Rule) -> bool:
    for t in rule_types_in(rule):
        if not cap.supports(t):
            return False
    return True
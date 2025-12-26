from __future__ import annotations

from typing import List, Tuple

from dsl.ast import Atom, Logical, Rule
from compiler.base import Capability, CompileResult, CompileWarning, normalize_policy


def compile_surge(
    rules_by_policy: List[Tuple[str, List[Rule]]],
    cap: Capability,
    header_comment: str,
) -> CompileResult:
    warnings: List[CompileWarning] = []
    stats = {"emitted": 0, "skipped": 0}

    lines: List[str] = []
    lines.append(f"# {header_comment}")
    lines.append("[Rule]")

    for policy, rules in rules_by_policy:
        pol = normalize_policy(policy)
        for r in rules:
            if isinstance(r, Atom) and r.norm_type() == "FINAL":
                lines.append(f"FINAL,{pol}")
                stats["emitted"] += 1
                continue

            if isinstance(r, Logical):
                # Surge supports AND/OR/NOT logical rules. [oai_citation:9‡NSSurge Manual](https://manual.nssurge.com/rule/logical-rule.html?utm_source=chatgpt.com)
                lines.append(f"{_emit_logical(r)},{pol}")
                stats["emitted"] += 1
                continue

            if isinstance(r, Atom):
                lines.append(f"{r.norm_type()},{r.value},{pol}{_emit_opts(r)}")
                stats["emitted"] += 1
                continue

            stats["skipped"] += 1
            warnings.append(CompileWarning(file="surge", line=str(r), reason="Unknown rule node"))

    return CompileResult(text="\n".join(lines) + "\n", warnings=warnings, stats=stats)


def _emit_opts(a: Atom) -> str:
    if not a.options:
        return ""
    # Surge options: appended as extra params for certain rules/ruleset
    # Keep them as-is
    return "," + ",".join(a.options)


def _emit_logical(l: Logical) -> str:
    op = l.norm_op()
    inner = ",".join(f"({ _emit_any(x) })" for x in l.items)
    return f"{op},(({inner}))"


def _emit_any(r: Rule) -> str:
    if isinstance(r, Logical):
        return _emit_logical(r)
    if isinstance(r, Atom):
        if r.norm_type() == "FINAL":
            return "FINAL"
        base = f"{r.norm_type()},{r.value}"
        if r.options:
            base += "," + ",".join(r.options)
        return base
    return ""
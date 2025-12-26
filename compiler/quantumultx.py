from __future__ import annotations

from typing import Dict, List, Tuple

from dsl.ast import Atom, Logical, Rule
from compiler.base import Capability, CompileResult, CompileWarning, normalize_policy


# QX Filter rules commonly use: HOST / HOST-SUFFIX / HOST-KEYWORD / USER-AGENT / URL-REGEX etc.
# Many public configs show USER-AGENT and HOST-SUFFIX usage. [oai_citation:10‡Gist](https://gist.github.com/jostyee/5d1f840bd8fd4ac53778a91ce13323b6?utm_source=chatgpt.com)
# We map:
# DOMAIN -> HOST
# DOMAIN-SUFFIX -> HOST-SUFFIX
# DOMAIN-KEYWORD -> HOST-KEYWORD
# URL-REGEX -> URL-REGEX
# USER-AGENT -> USER-AGENT
# IP-CIDR / GEOIP / DST-PORT etc: QX supports some but formats differ; we conservatively skip unsupported unless you extend.

_TYPE_MAP = {
    "DOMAIN": "HOST",
    "DOMAIN-SUFFIX": "HOST-SUFFIX",
    "DOMAIN-KEYWORD": "HOST-KEYWORD",
    "DOMAIN-WILDCARD": "HOST-WILDCARD",
    "USER-AGENT": "USER-AGENT",
    "URL-REGEX": "URL-REGEX",
}


def compile_quantumultx(
    rules_by_policy: List[Tuple[str, List[Rule]]],
    cap: Capability,
    header_comment: str,
) -> CompileResult:
    warnings: List[CompileWarning] = []
    stats = {"emitted": 0, "skipped": 0}

    lines: List[str] = []
    lines.append(f"# {header_comment}")
    lines.append("[filter]")

    for policy, rules in rules_by_policy:
        pol = normalize_policy(policy)
        for r in rules:
            if isinstance(r, Atom) and r.norm_type() == "FINAL":
                lines.append(f"FINAL,{pol}")
                stats["emitted"] += 1
                continue

            if isinstance(r, Logical):
                # QX does not have Surge-style logical rule syntax in filter section.
                stats["skipped"] += 1
                warnings.append(CompileWarning(file="quantumultx", line=str(r), reason="QX filter does not support AND/OR/NOT in this compiler"))
                continue

            if isinstance(r, Atom):
                rt = r.norm_type()
                if rt in _TYPE_MAP:
                    qx_t = _TYPE_MAP[rt]
                    # options: we keep as trailing flags when possible (e.g. resolve-on-proxy/force-remote-dns)
                    opt = ""
                    if r.options:
                        opt = "," + ",".join(r.options)
                    lines.append(f"{qx_t},{r.value},{pol}{opt}")
                    stats["emitted"] += 1
                    continue

                stats["skipped"] += 1
                warnings.append(CompileWarning(file="quantumultx", line=r.raw if hasattr(r, "raw") else str(r), reason=f"Unsupported rule type for QX: {rt}"))
                continue

    return CompileResult(text="\n".join(lines) + "\n", warnings=warnings, stats=stats)
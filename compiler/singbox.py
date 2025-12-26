from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

from dsl.ast import Atom, Logical, Rule
from compiler.base import Capability, CompileResult, CompileWarning, normalize_policy


# sing-box route rules fields include domain/domain_suffix/domain_keyword/domain_regex/geoip/ip_cidr/port, etc. [oai_citation:12‡Sing Box](https://sing-box.sagernet.org/configuration/route/rule/?utm_source=chatgpt.com)
# We'll map to sing-box route rules, and output "route.rules" list.
# For unsupported (USER-AGENT etc), we warn+skip by default.

def compile_singbox(
    rules_by_policy: List[Tuple[str, List[Rule]]],
    cap: Capability,
    header_comment: str,
) -> CompileResult:
    warnings: List[CompileWarning] = []
    stats = {"emitted": 0, "skipped": 0}

    sb_rules: List[Dict[str, Any]] = []

    for policy, rules in rules_by_policy:
        pol = normalize_policy(policy)

        for r in rules:
            if isinstance(r, Atom) and r.norm_type() == "FINAL":
                sb_rules.append({"outbound": pol})
                stats["emitted"] += 1
                continue

            if isinstance(r, Logical):
                # sing-box has "rule_set" and multiple fields combined as AND semantics, but not Surge-style nested boolean.
                # We skip with warning; you can later extend to translate to multiple rules.
                stats["skipped"] += 1
                warnings.append(CompileWarning(file="singbox", line=str(r), reason="Nested AND/OR/NOT not compiled in baseline"))
                continue

            if isinstance(r, Atom):
                node = _atom_to_singbox(r, pol)
                if node is None:
                    stats["skipped"] += 1
                    warnings.append(CompileWarning(file="singbox", line=f"{r.norm_type()},{r.value}", reason="Unsupported type in baseline sing-box compiler"))
                    continue
                sb_rules.append(node)
                stats["emitted"] += 1

    doc = {
        "_comment": header_comment,
        "route": {
            "rules": sb_rules
        }
    }
    text = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    return CompileResult(text=text, warnings=warnings, stats=stats)


def _atom_to_singbox(a: Atom, outbound: str) -> Dict[str, Any] | None:
    t = a.norm_type()
    v = a.value

    if t == "DOMAIN":
        return {"domain": [v], "outbound": outbound}
    if t == "DOMAIN-SUFFIX":
        return {"domain_suffix": [v], "outbound": outbound}
    if t == "DOMAIN-KEYWORD":
        return {"domain_keyword": [v], "outbound": outbound}
    if t == "DOMAIN-WILDCARD":
        # sing-box supports domain_regex; convert wildcard to regex crudely
        # *.example.com -> ^(.+\.)?example\.com$
        rx = wildcard_to_regex(v)
        return {"domain_regex": [rx], "outbound": outbound}
    if t == "URL-REGEX":
        # sing-box route has domain_regex but not full URL regex matching in core routing; treat as domain_regex if you pass a domain regex.
        return {"domain_regex": [v], "outbound": outbound}
    if t == "IP-CIDR":
        return {"ip_cidr": [v], "outbound": outbound}
    if t == "GEOIP":
        return {"geoip": [v], "outbound": outbound}
    if t == "DST-PORT":
        return {"port": [int(v)], "outbound": outbound}
    if t == "IP-ASN":
        # sing-box supports ip_asn in newer builds? not in baseline docs page; skip.
        return None
    if t in ("USER-AGENT", "SCRIPT", "RULE-SET", "DOMAIN-SET"):
        return None
    return None


def wildcard_to_regex(pat: str) -> str:
    # very small converter
    import re
    s = re.escape(pat).replace(r"\*", ".*")
    return "^" + s + "$"
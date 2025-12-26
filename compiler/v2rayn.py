from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

from dsl.ast import Atom, Logical, Rule
from compiler.base import Capability, CompileResult, CompileWarning, normalize_policy


# v2ray-core routing rules JSON. [oai_citation:13‡V2Ray](https://www.v2ray.com/en/configuration/routing.html?utm_source=chatgpt.com)
# v2rayN commonly consumes routing rules in that shape (community generators exist). [oai_citation:14‡GitHub](https://github.com/mer30hamid/v2rayN-Routing-Rules-Generator?utm_source=chatgpt.com)
#
# We generate:
# {
#   "routing": {
#     "domainStrategy": "AsIs",
#     "rules": [ { "type":"field", ... , "outboundTag":"..." }, ... ]
#   }
# }
#
# Limitation: v2ray "field" supports domain, ip, port, network, protocol, inboundTag, user, attrs... geoip/geosite via special forms.
# We'll map what we can:
# - DOMAIN / DOMAIN-SUFFIX / DOMAIN-KEYWORD -> "domain": ["domain:xxx", "domain:keyword"]
# - URL-REGEX -> not directly supported -> skip
# - USER-AGENT -> skip
# - GEOIP -> "ip": ["geoip:CN"]
# - IP-CIDR -> "ip": ["1.2.3.0/24"]
# - DST-PORT -> "port": "443" (or "80-90")
# - FINAL -> add a catch-all rule at end (no domain/ip => matches all) as fallback

def compile_v2rayn(
    rules_by_policy: List[Tuple[str, List[Rule]]],
    cap: Capability,
    header_comment: str,
) -> CompileResult:
    warnings: List[CompileWarning] = []
    stats = {"emitted": 0, "skipped": 0}

    vrules: List[Dict[str, Any]] = []

    for policy, rules in rules_by_policy:
        pol = normalize_policy(policy)

        for r in rules:
            if isinstance(r, Atom) and r.norm_type() == "FINAL":
                vrules.append({
                    "type": "field",
                    "outboundTag": pol
                })
                stats["emitted"] += 1
                continue

            if isinstance(r, Logical):
                stats["skipped"] += 1
                warnings.append(CompileWarning(file="v2rayn", line=str(r), reason="AND/OR/NOT not supported in v2ray field rules"))
                continue

            if isinstance(r, Atom):
                node = _atom_to_v2ray_field(r, pol)
                if node is None:
                    stats["skipped"] += 1
                    warnings.append(CompileWarning(file="v2rayn", line=f"{r.norm_type()},{r.value}", reason="Unsupported type in v2ray routing"))
                    continue
                vrules.append(node)
                stats["emitted"] += 1

    doc = {
        "_comment": header_comment,
        "routing": {
            "domainStrategy": "AsIs",
            "rules": vrules
        }
    }
    text = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    return CompileResult(text=text, warnings=warnings, stats=stats)


def _atom_to_v2ray_field(a: Atom, outbound: str) -> Dict[str, Any] | None:
    t = a.norm_type()
    v = a.value

    if t == "DOMAIN":
        return {"type": "field", "domain": [f"domain:{v}"], "outboundTag": outbound}
    if t == "DOMAIN-SUFFIX":
        return {"type": "field", "domain": [f"domain:{v}"], "outboundTag": outbound}
    if t == "DOMAIN-KEYWORD":
        return {"type": "field", "domain": [f"keyword:{v}"], "outboundTag": outbound}
    if t == "IP-CIDR":
        return {"type": "field", "ip": [v], "outboundTag": outbound}
    if t == "GEOIP":
        return {"type": "field", "ip": [f"geoip:{v}"], "outboundTag": outbound}
    if t == "DST-PORT":
        return {"type": "field", "port": str(v), "outboundTag": outbound}
    if t in ("URL-REGEX", "USER-AGENT", "DOMAIN-WILDCARD", "RULE-SET", "DOMAIN-SET", "SCRIPT", "IP-ASN"):
        return None
    return None
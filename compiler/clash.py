from __future__ import annotations

import yaml
from typing import Dict, List, Tuple

from dsl.ast import Atom, Logical, Rule
from compiler.base import Capability, CompileResult, CompileWarning, normalize_policy


# We generate a minimal Clash/mihomo config fragment:
# - rule-providers pointing to raw URLs for each policy file (classical)
# - rules referencing RULE-SET providers
#
# mihomo rule-providers content supports classical/domain/ipcidr. classical supports many rule types. [oai_citation:11‡Metacubex Wiki](https://wiki.metacubex.one/en/config/rule-providers/content/?utm_source=chatgpt.com)
#
# IMPORTANT: user will host this repo. build.py fills base_raw_url.

SUPPORTED_CLASSICAL = {
    "DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-WILDCARD",
    "IP-CIDR", "IP-ASN", "GEOIP", "DST-PORT", "URL-REGEX", "USER-AGENT",
    "FINAL",
}


def compile_clash(
    rules_by_policy: List[Tuple[str, List[Rule]]],
    cap: Capability,
    header_comment: str,
    base_raw_url: str,
) -> CompileResult:
    warnings: List[CompileWarning] = []
    stats = {"emitted_rules": 0, "skipped_rules": 0, "providers": 0}

    # rule-providers (one per policy list file) using "classical"
    rule_providers: Dict[str, Dict] = {}

    # rules: use RULE-SET,provider_name,policy
    rules_out: List[str] = []

    for policy, rules in rules_by_policy:
        pol = normalize_policy(policy)
        provider_name = f"RL_{pol}"
        rule_providers[provider_name] = {
            "type": "http",
            "behavior": "classical",
            "url": f"{base_raw_url}/rules/{pol}.list",
            "path": f"./ruleset_cache/{provider_name}.yaml",
            "interval": 86400,
        }
        stats["providers"] += 1

        # Reference provider in rules (RULE-SET)
        # Clash syntax: RULE-SET,<provider>,<policy>
        # Note: We do not inline each rule because we want external syncing.
        rules_out.append(f"RULE-SET,{provider_name},{pol}")
        stats["emitted_rules"] += 1

    # FINAL: if user has FINAL.list, it will still be referenced above; but Clash needs a real MATCH at end.
    # We'll force a trailing MATCH if FINAL.list is absent; otherwise, we still add MATCH to be safe.
    rules_out.append("MATCH,PROXY")
    stats["emitted_rules"] += 1

    doc = {
        "#": header_comment,
        "rule-providers": rule_providers,
        "rules": rules_out,
    }
    text = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True)

    return CompileResult(text=text, warnings=warnings, stats=stats)
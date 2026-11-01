#!/usr/bin/env python3
"""Check public group filters against synthetic node names; no credentials needed."""

import re
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
lines = (ROOT / "leon.ini").read_text(encoding="utf-8").splitlines()
groups = {}
for line in lines:
    if line.startswith("custom_proxy_group="):
        fields = line.split("=", 1)[1].split("`")
        end = 0 if fields[1] == "select" else 2
        groups[fields[0]] = fields[2:-end] if end else fields[2:]

nodes = [
    "EX\u00b7Hong Kong",
    "EX\u00b7台湾",
    "EX\u00b7\u65e5\u672c",
    "PQ\u00b7Singapore-0.01\u500d",
    "PQ\u00b7Singapore-0.1\u500d",
    "PQ\u00b7Singapore-1\u500d",
    "SM\u00b7Tokyo-1\u500d",
    "LX\u00b7Tokyo",
]
filtered = []
for name, filters in groups.items():
    matches = []
    has_filter = False
    for pattern in filters:
        if pattern.startswith("[]"):
            assert pattern[2:] in groups or pattern[2:] in {"DIRECT", "REJECT"}, name
            continue
        assert not pattern.startswith("!!"), "Use renamed prefixes for group filters"
        has_filter = True
        matches.extend(node for node in nodes if re.search(pattern, node))
    if has_filter:
        assert matches, "Group filter matched no fixture nodes"
        filtered.append(set(matches))

assert len(groups) == 11
assert {nodes[1], nodes[2]} in filtered, "AI must include both preferred EX regions"
assert {nodes[3], nodes[4]} in filtered, "Video must include both low-cost tiers"
assert {nodes[5]} in filtered, "PQ backup must exclude low-cost video nodes"
assert {nodes[6]} in filtered
assert {nodes[7]} in filtered

ai_rule = next(line.split(",", 1)[1] for line in lines if line.startswith("ruleset=AI"))
assert urlsplit(ai_rule).query, "AI rules need a cache version for this fix"
ai_lines = (ROOT / "rules" / "ai.list").read_text(encoding="utf-8").splitlines()
assert "DOMAIN-SUFFIX,ytimg.com" in ai_lines
assert "DOMAIN-SUFFIX,youtube-nocookie.com" in ai_lines
assert ai_lines.index("DOMAIN-SUFFIX,ytimg.com") < next(
    i for i, line in enumerate(ai_lines) if line.startswith("IP-CIDR,")
)
print("OK: group filters, references, video tiers, and thumbnail rules")

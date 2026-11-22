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

assert len(groups) == 12

spotify = groups["Spotify-TW"]
tw_filters = [p for p in spotify if not p.startswith("[]")]
assert tw_filters, "Spotify-TW needs a name filter"
tw_re = tw_filters[0]
assert re.search(tw_re, "EX·台湾")
assert re.search(tw_re, "🇨🇳 台湾 06 家宽")
assert re.search(tw_re, "SM·台灣")
assert re.search(tw_re, "TW 01")
assert not re.search(tw_re, "Twitch")
assert not re.search(tw_re, "EX·Hong Kong")

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

download_rule = next(
    line.split(",", 1)[1]
    for line in lines
    if line.startswith("ruleset=") and "/rules/download.list" in line
)
assert urlsplit(download_rule).query, "Download rules need a cache version"
shadowrocket = (ROOT / "leon.conf").read_text(encoding="utf-8").splitlines()
assert any(
    line.startswith("RULE-SET," + download_rule + ",") for line in shadowrocket
), "Both clients must use the same download rule version"
download_lines = (ROOT / "rules" / "download.list").read_text(encoding="utf-8").splitlines()
download_suffixes = [
    line.split(",", 1)[1]
    for line in download_lines
    if line.startswith("DOMAIN-SUFFIX,")
]
for domain in [
    "docker.io",
    "registry-1.docker.io",
    "auth.docker.io",
    "production.cloudflare.docker.com",
    "production.cloudfront.docker.com",
]:
    assert any(
        domain == suffix or domain.endswith("." + suffix)
        for suffix in download_suffixes
    ), "Missing Docker download rule: " + domain


spotify_rules = [
    line.split(",", 1)[1]
    for line in lines
    if line.startswith("ruleset=Spotify-TW")
]
assert len(spotify_rules) == 2, "Clash should load both Spotify domain and process lists"
assert all(urlsplit(url).query for url in spotify_rules), "Spotify rules need a cache version"
assert any(
    line.startswith("RULE-SET," + spotify_rules[0] + ",Spotify-TW") for line in shadowrocket
), "Both clients must use the same Spotify domain rule version"
assert all(
    "spotify-process.list" not in line for line in shadowrocket
), "PROCESS-NAME Spotify list is Clash-only"
spotify_lines = (ROOT / "rules" / "spotify.list").read_text(encoding="utf-8").splitlines()
for domain in ["spotify.com", "spotifycdn.com", "scdn.co", "spotilocal.com"]:
    assert f"DOMAIN-SUFFIX,{domain}" in spotify_lines, "Missing Spotify rule: " + domain
direct_lines = (ROOT / "rules" / "direct.list").read_text(encoding="utf-8").splitlines()
assert "DOMAIN-SUFFIX,oracle.com" in direct_lines
assert "DOMAIN-SUFFIX,oraclecloud.com" in direct_lines
direct_rule = next(
    line.split(",", 1)[1]
    for line in lines
    if line.startswith("ruleset=") and "/rules/direct.list" in line
)
assert urlsplit(direct_rule).query, "Direct rules need a cache version after Oracle addition"
assert any(
    line.startswith("RULE-SET," + direct_rule + ",") for line in shadowrocket
), "Both clients must use the same direct rule version"

print("OK: group filters, references, video tiers, thumbnail rules, Docker rules, and Spotify-TW")

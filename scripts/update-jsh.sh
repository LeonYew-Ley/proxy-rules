#!/usr/bin/env bash
# 从 Johnshall/Shadowrocket-ADBlock-Rules-Forever 的 sr_cnip_ad.conf 拆出：
#   rules/ads.list       （Reject 规则 → 广告拦截）
#   rules/jsh-proxy.list （手工 Proxy 规则：Telegram 等）
# 输出为不带策略的 classical 格式，subconverter 与 Shadowrocket RULE-SET 通用。
# 上游协议：见 https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever
set -euo pipefail
cd "$(dirname "$0")/.."
SRC="${1:-https://raw.githubusercontent.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever/release/sr_cnip_ad.conf}"
TMP="$(mktemp)"
if [[ -f "$SRC" ]]; then cp "$SRC" "$TMP"; else curl -fsSL --retry 3 "$SRC" -o "$TMP"; fi

BUILD="$(grep -m1 -E '^# build time:' "$TMP" || true)"


extract() { # $1 = Reject|Proxy
  awk -v want="$1" '
    /^\[Rule\]/ {f=1; next}
    /^\[/ {f=0}
    f && !/^[[:space:]]*#/ && NF {
      line=$0; sub(/[[:space:]]*#.*$/, "", line)
      n=split(line, a, ",")
      if (n < 3) next
      pol=tolower(a[3]); gsub(/[[:space:]]/, "", pol)
      if (tolower(want) != pol) next
      type=a[1]; val=a[2]
      if (type=="IP-CIDR" || type=="IP-CIDR6") print type "," val ",no-resolve"
      else print type "," val
    }' "$TMP"
}

{ echo "# ads.list — 广告拦截（→ REJECT），由 scripts/update-jsh.sh 自动生成，勿手改"
  echo "# 上游: Johnshall/Shadowrocket-ADBlock-Rules-Forever sr_cnip_ad.conf  ${BUILD}"
  extract Reject; } > rules/ads.list

{ echo "# jsh-proxy.list — 上游手工 Proxy 列表（Telegram 等，→ 🔰 节点选择），由 scripts/update-jsh.sh 自动生成，勿手改"
  echo "# 上游: Johnshall/Shadowrocket-ADBlock-Rules-Forever sr_cnip_ad.conf  ${BUILD}"
  extract Proxy; } > rules/jsh-proxy.list

rm -f "$TMP"
wc -l rules/ads.list rules/jsh-proxy.list

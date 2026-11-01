#!/usr/bin/env bash
# 推送前自查：公开仓库里不能出现私有信息。命中任何一项就退出 1。
set -u
cd "$(dirname "$0")/.."
PATTERN='derp\.leonyew|47\.108\.92\.31|mc\.leonyew|aihub\.dog|119\.28\.5\.117|43\.153\.209\.178|43\.161\.229\.52|193\.112\.93\.176|leonyew\.space|token=|api_access_token|tskey-|/sub\?|/getprofile'
hits="$(grep -rEn --exclude-dir=.git --exclude=check-private.sh "$PATTERN" . || true)"
if [[ -n "$hits" ]]; then echo "发现疑似私有信息："; echo "$hits"; exit 1; fi
echo "OK: 未发现私有信息"

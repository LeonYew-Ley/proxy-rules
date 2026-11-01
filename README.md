# proxy-rules

个人分流规则仓库：一套规则，同时给 **Clash / Clash Verge**（经 subconverter）和 **Shadowrocket** 用。

> 这是公开仓库：只放分流规则和策略组，**不放**订阅链接、token、私有域名/IP。
> 私有规则放在自己的服务器上，见下文「私有规则」。推送前运行 `./scripts/check-private.sh` 自查。

## 文件

| 路径 | 用途 |
| --- | --- |
| `leon.ini` | subconverter 外部配置：规则集 + 策略组（Clash 目标） |
| `nodes-only.ini` | subconverter 外部配置：只出节点（给 Shadowrocket 订阅，节点名前缀与 `leon.ini` 一致） |
| `leon.conf` | Shadowrocket 配置（策略组 + RULE-SET + 通用设置） |
| `rules/*.list` | 规则列表，Surge/Shadowrocket classical 格式（不带策略），两端共用 |
| `scripts/update-jsh.sh` | 从 Johnshall 上游拆出 `ads.list` / `jsh-proxy.list` |
| `.github/workflows/update-ads.yml` | 每天自动跑上面的脚本 |
| `scripts/check-private.sh` | 推送前检查有没有私有信息 |

## 规则列表

| 列表 | 策略 | 说明 |
| --- | --- | --- |
| `direct.list` | DIRECT | 内网、JetBrains、Kiro/OpenCode 域名、WorkBuddy/Qoder 国内服务、Steam 下载 CDN |
| `tailscale.list` | DIRECT（仅 Clash） | Tailscale 公共网段与控制面域名；Shadowrocket 用 TAILSCALE 策略，规则写在 `leon.conf` |
| `steam.list` | 🔰 节点选择 | Steam 登录/商店/社区 |
| `video.list` | 视频出口 | 大流量视频站 |
| `download.list` | 下载专用 | GitHub 下载 |
| `work.list` | 主力故障转移 | npm / nuget / zed / learn.microsoft.com |
| `ai.list` | AI自动选择 | AI、Google、Cloudflare、STUN、公共 DNS IP |
| `ads.list` | REJECT | 广告（上游自动生成） |
| `jsh-proxy.list` | 🔰 节点选择 | 上游手工代理列表（Telegram 等，自动生成） |

匹配顺序：私有直连 → direct → tailscale → steam → video → download → work → ai → ads → jsh-proxy → GEOIP,CN → FINAL。

## 策略组 / 机场前缀

节点名由 subconverter 加前缀：`EX·` Edge-X（主力）、`PQ·` 赔钱、`SM·` 三毛、`LX·` 良心云。
Clash 和 Shadowrocket 都按重命名后的前缀过滤（如 `^EX·`）。不要把 Clash 的分组筛选改回 `!!GROUP=`：当前社区版转换器的实测结果是节点存在，但这种筛选生成空组。

| 组 | 类型 | 成员 |
| --- | --- | --- |
| 🔰 节点选择 | select | 主力故障转移、赔钱备用、三毛备用、良心云、♻️ 自动选择、DIRECT、全部节点 |
| 🐟 漏网之鱼 | select | 🔰 节点选择、主力故障转移、DIRECT |
| ♻️ 自动选择 | url-test | EX·（剔除台湾） |
| 主力故障转移 | fallback | ♻️ 自动选择 → 赔钱备用 → 三毛备用 |
| AI自动选择 | fallback | EX·台湾 → EX·日本 → 赔钱备用 → 三毛备用 |
| 视频低价自动 / 视频出口 | url-test / select | PQ· 的 0.01/0.1 倍节点（没有就 REJECT）→ 主力故障转移 |
| 下载专用 | fallback | 三毛备用 → 赔钱备用 |
| 赔钱备用 / 三毛备用 | url-test | 只用 1 倍节点（排除低价倍率、2x、2~9 倍、IPv6、勿跑） |
| 良心云 | url-test | LX· |

## 私有规则

自己的域名、DERP、IP 等放服务器的 `myrules/private.list`：

- Clash：`leon.ini` 第一条 `ruleset=DIRECT,myrules/private.list` 读取服务器本地文件，生成订阅时内联。
- Shadowrocket：在手机上新建一个「模块」，用 `RULE-SET` 指向服务器的 `getruleset` 接口（模块优先级高于配置文件）。

## 更新规则

改 `rules/*.list` 或 `leon.ini` / `leon.conf` → push。
subconverter 默认缓存规则集 6 小时（`cache_ruleset`），Shadowrocket 在「配置 → 更新」时拉取。
规则需要立即生效时，可更新 `leon.ini` 中对应规则 URL 的 `?v=` 版本标识，绕开旧规则缓存；外部配置本身也可能短暂缓存，更新后必须检查实际生成结果，而不是只检查 GitHub 文件。

提交前运行 `python scripts/check-config.py` 和 `bash scripts/check-private.sh`。

## 致谢

`ads.list`、`jsh-proxy.list` 来自 [Johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever)（CC BY-SA 4.0）。

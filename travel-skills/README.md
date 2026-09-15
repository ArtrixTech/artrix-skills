# travel-skills

旅行数据技能组。48 个 skill + 共享数据 + 维护脚本，来自开源项目 [borski/travel-hacking-toolkit](https://github.com/borski/travel-hacking-toolkit)（MIT，662★，周更），收编进本仓统一管理。

## 结构

```
travel-skills/
├── README.md            ← 本文件
├── data/                ← 共享数据 JSON（联盟表/积分估值/转点比例/酒店名录等，上游周更）
├── scripts/             ← 数据刷新与生成脚本
├── compare-flights/     ← 编排层：全源机票比价
├── compare-hotels/      ← 编排层：全源酒店比价
├── trip-planner/        ← 编排层：完整行程规划
├── flight-search-strategy/ ← 参考层：多源检索优先级与策略
├── duffel/              ← 数据源：Duffel GDS 现金票价（需 key）
├── google-flights/      ← 数据源：Google Flights（浏览器自动化）
├── seats-aero/          ← 数据源：里程票库存（需 Pro key）
├── ... 共 48 个 skill 目录
```

## 分层

| 层 | skill | 作用 |
|---|---|---|
| 编排 | compare-flights、compare-hotels、trip-planner、plan-trip、award-calendar、gardening、trip-calculator、trip-log | 入口级，自动调度下层数据源 |
| 机票源 | duffel、google-flights、ignav、seats-aero、southwest、serpapi、rapidapi、skyscanner 系 | 现金价 / 里程票 / 门户价 |
| 酒店源 | premium-hotels、amex-travel、chase-travel、bilt、ticketsatwork、vrbo、sutochno、hotel-chains | 门户 / 批发 / 民宿 |
| 积分体系 | awardwallet、transfer-partners、transfer-bonuses、points-valuations、partner-awards、alliances、award-sweet-spots、award-holds、status-match、stopovers、round-the-world、cabin-codes、wheretocredit | 里程积分知识库 |
| 目的地与交通 | tripadvisor、atlas-obscura、deutsche-bahn、scandinavia-transit、wikipedia-airports、seatmaps | 目的地信息与地面交通 |
| 参考 | flight-search-strategy、booking-guidance、fallback-and-resilience、lessons-learned、getting-started | 方法论与排错 |

## 数据通道现状（2026-09-15 配置）

免 key 已接入 mcporter 用户级（`~/.mcporter/mcporter.json`）：google-flights（stdio）、kiwi、trivago、skiplagged、ferryhopper、airbnb。skill 内指引走 `mcporter call <server>.<tool>`。

需 key 激活：Duffel（GDS 权威现金价，注册免费）、Seats.aero Pro（里程票 ~$8/月）、Ignav（1000 次/月免费）、AwardWallet、SerpAPI、RapidAPI、LiteAPI、TripAdvisor。

Docker 依赖（首次使用自动拉镜像）：southwest、american-airlines、chase-travel、amex-travel、ticketsatwork、vrbo、sutochno。

## 与本机基建的关系

- 香港快运等航司官网直连走 `~/GitHub/hkexpress-infra`（Playwright 持久会话过 Akamai 范式），与本技能组互补：skill 管比价方法论，hkexpress-infra 管单航司深度实采。
- 中国国内机酒主通道是飞猪 FlyAI（官方 skill 在 `alibaba-flyai/flyai-skill`，未收编），本组偏海外市场。

## 使用注意

- 48 个 skill 经 farm 平铺到 `~/.agents/skills/`，触发词强势（compare-flights、trip-planner 等），沾机票/酒店话题即激活。
- data/ 下的 JSON 由上游 GitHub Actions 周更，收编后靠手动同步上游更新（见下）。
- 部分 skill 面向美国市场（chase/amex/bilt/southwest），在香港场景下适用性有限，仅作参考。

## 同步上游

```bash
cd ~/GitHub/travel-hacking-toolkit && git pull
rsync -a --delete skills/ ~/GitHub/artrix-skills/travel-skills/   # 保留本 README
rsync -a data/ ~/GitHub/artrix-skills/travel-skills/data/
cd ~/GitHub/artrix-skills && git add travel-skills && git commit -m "chore(travel-skills): sync upstream <sha>"
```

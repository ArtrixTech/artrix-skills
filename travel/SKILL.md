---
name: travel
description: Master entry indexing 48 travel & points sub-skills (flights, hotels, loyalty programs). Use for ANY travel request: cash or award flight search, airline miles and points, award availability, award calendars, sweet spots, holds, stopovers, transfer partners, point valuations, seat maps, hotel chains and premium programs, trip planning and cost math, vacation rentals, trains and transit in Europe and Scandinavia, airline status and status matches, fare monitoring, trip logging. Load this skill, read the index table below, pick the right sub-skill, then read that sub-skill's SKILL.md and follow it. Sub-skills are hidden from auto-invocation; this entry is the only doorway. 中文触发词同样命中：旅行 航班 机票 酒店 里程 积分 兑换 行程 规划 公务舱。
---

# Travel — 子技能总入口

48 个旅行子技能已通过 `disable-model-invocation: true` 从系统提示词隐藏，本文件是唯一常驻入口。

## 使用流程

1. 从下方索引选出最匹配的子技能（可组合多个，例如 `seats-aero` + `transfer-partners` + `trip-calculator`）。
2. 用 read 工具读取其 SKILL.md：`~/.agents/skills/<name>/SKILL.md`，并严格按其指引执行。
3. 用户手动输入 `/skill:<name>` 亦可直接加载任一子技能。
4. 子技能之间存在交叉引用（如 lessons-learned 是搜索前置必读），按其指引连带加载。

## 子技能索引（48 项）

**destinations**

- `atlas-obscura` — Hidden gems and unusual attractions near any destination. api_key: None (free)
- `deutsche-bahn` — Deutsche Bahn (DB) train search across Germany and into AT/CH/NL/FR/BE via the open-source db-vendo-client. St
- `scandinavia-transit` — Trains, buses, ferries in Norway, Sweden, and Denmark. Includes Danish fare/zone pricing. api_key: Entur + Tra
- `tripadvisor` — Hotel ratings, restaurant search, attraction reviews, nearby search. 5K calls/month. api_key: TripAdvisor

**flights**

- `duffel` — Primary cash prices. Real GDS per-fare-class data. api_key: Duffel
- `google-flights` — Browser-automated Google Flights. All airlines including Southwest. api_key: None (requires agent-browser)
- `ignav` — Fast REST API cash prices. Market selection for arbitrage. api_key: Ignav (1,000 free)
- `seatmaps` — Aircraft seat maps, cabin dimensions, seat recommendations. api_key: None (requires agent-browser)
- `seats-aero` — Award availability across 27 mileage programs. api_key: Seats.aero Pro/Partner
- `southwest` — SW fare classes, points pricing, Companion Pass. Change flight price drop monitor. api_key: None (requires Pat
- `wikipedia-airports` — Route discovery and airline-service sanity check via Wikipedia airport pages. Answers "does carrier X fly A→B"

**hotels**

- `premium-hotels` — Search 4,659 Amex FHR/THC + Chase Edit hotels by city. Stacking opportunities. api_key: None (local data)
- `rapidapi` — Booking.com hotel prices. api_key: RapidAPI
- `serpapi` — Google Hotels search and destination discovery. api_key: SerpAPI
- `sutochno` — Sutochno.ru Russian apartment search via Patchright. Ruble / Mir payment for Georgia / CIS stays. api_key: Non
- `ticketsatwork` — TicketsAtWork (EBG) corporate-perks portal. Hotels, theme park tickets, attractions, live events. Often beats 
- `vrbo` — VRBO whole-home, condo, and cabin search via Patchright. Complements Airbnb for group stays. api_key: None (re

**loyalty**

- `american-airlines` — AAdvantage balance and elite status. AwardWallet does not support AA. api_key: None (requires Patchright) dock
- `awardwallet` — All loyalty balances, elite status, history. api_key: AwardWallet Business
- `transfer-partners` — Cheapest transfer path from credit card points to mileage programs. api_key: None (local data)
- `wheretocredit` — Mileage earning rates by airline and booking class across 50+ programs. api_key: None (free)

**orchestration**

- `award-calendar` — Cheapest award dates for a route across a date range. Calendar grid view. api_key: Seats.aero Pro
- `compare-flights` — Unified flight comparison across ALL sources in parallel. Auto-applies transfer optimization. api_key: Uses in
- `compare-hotels` — Unified hotel comparison across portals, metasearch, and Airbnb. FHR/Edit stacking detection. api_key: Uses in
- `gardening` — Audit existing reservations for price drops, better cabins, schedule changes, and improved routings. api_key: 
- `getting-started` — First-run onboarding. Detects setup, points to setup-keys script, shows sample prompts.
- `plan-trip` — Guided trip planner. The hero command for the toolkit.
- `trip-calculator` — Cash vs points decision answered with math. Transfer ratios, taxes, opportunity cost. api_key: None (free, loc
- `trip-log` — Opt-in trip journal. Save searches and booked trips to trips/logs/ for future reference. api_key: None
- `trip-planner` — Full trip planning. Flights + hotels + points in one shot. api_key: Uses individual skill keys

**portals**

- `amex-travel` — Amex MR portal for flights, hotels, IAP discounts, FHR/THC benefits. Requires Platinum. api_key: None (require
- `bilt` — Bilt Rewards travel portal for hotels and flights. 1.25 cpp on Bilt Points. Home Away From Home properties giv
- `chase-travel` — Chase UR portal for flights, hotels, Points Boost, Edit benefits. Requires Sapphire. api_key: None (requires P

**reference**

- `alliances` — Star Alliance, oneworld, SkyTeam membership and recent shifts (SAS to SkyTeam, ITA to Star, Hawaiian/Fiji to o
- `award-holds` — Per-program rules for placing award flight tickets on hold. Covers 9 programs with holds (AA 24h online, LH 5 
- `award-sweet-spots` — Catalog of legendary, excellent, and good award redemptions with current rates and devaluation history.
- `booking-guidance` — The booking flow, hold-before-transfer rule, phone numbers for major programs.
- `cabin-codes` — IATA cabin codes (F/J/W/Y) and saver fare class codes (X/I/O) for partner-bookable inventory.
- `fallback-and-resilience` — What to do when each tool fails. Tool-by-tool fallback paths.
- `flight-search-strategy` — The canonical multi-source search workflow. Source priority (Duffel > Ignav > Google Flights > others), market
- `hotel-chains` — Maps brand names (Westin, Holiday Inn, etc.) to chain families and loyalty programs.
- `lessons-learned` — Hard-won knowledge from real searches. The mandatory Seats.aero workflow, Southwest specifics, Companion Pass 
- `partner-awards` — Which programs ticket which airlines (alliance + bilateral). Cross-references credit card currencies to bookin
- `points-valuations` — CPP formula, floor/ceiling rules, surcharge-heavy programs to avoid, transfer bonus considerations, Chase Poin
- `round-the-world` — RTW + Pacific Circle + Asia-Pacific Circle + regional distance-award reference. 13 active programs, 4 disconti
- `status-match` — Per-program status match rules with lifetime / once-per-N-years warnings, free vs paid concierge distinction, 
- `stopovers` — Per-program stopover rules for award redemptions. Includes Icelandair free stopover, Aeroplan, Alaska Atmos, F
- `transfer-bonuses` — Active credit card transfer bonuses with primary-source citations. Tells the agent the real effective ratio wh

## 备注

- 索引路径统一前缀 `~/.agents/skills/`，真身在 `~/GitHub/artrix-skills/travel-skills/`（git 管理）。
- 本文件由 artrix-skills 仓库维护；新增旅行子技能后在此索引补一行。

---
status: draft
last-verified: "2026-10-19"
related-code:
  - knowledge/source-snapshots/reconcile-summary.json
  - knowledge/registry/list-item-to-card.jsonl
---

# duplicate_list_matches — primary カード（照合索引）

> **統合マージはしない** — Lists §1 件 = テーマカード 1 枚。複数 `record_id` は draft/catalog 写し。

正: `reconcile-summary.json` → `duplicate_list_matches`（**23** primary）。

| list | knowledge_id | タイトル（短） |
| --- | --- | --- |
| 411 | KH-VFGLF-HOIST-RESOLVER-WIRE-411 | 巻上レゾルバ断線 |
| 319 | KH-VFGR-CAR-TOP-RUN-SW-319 | VFGR RUN SW |
| 240 | KH-MBS-F4B-PIN-240 | MBS インジ消灯 |
| 233 | KH-SCU20-FLASH-REWRITE-233 | SCU-20 書換 |
| 221 | KH-HEALTH-AIR-AC-TIMER-221 | HA 併設 AC |
| 192 | KH-EMER-JB-GROMMET-192 | 非常 JB ゴム |
| 189 | KH-VFGLB-JPA-ACL-JUMPER-189 | 群管理（**保留**） |
| 187 | KH-MRL-SETS-ENCODER-DIR-187 | SETS 9999 |
| 179 | KH-ALL-BGM-EMERG-WIRING-179 | BGM 非常 |
| 178 | KH-ALL-SIGNAGE-TWIST-NOISE-178 | サイネージ |
| 176 | KH-ALL-GROUND-N00-NORMAL-SLOW-176 | N00 本スロー |
| 174 | KH-VFGLB-MELD-BATTERY-174 | MELD バッテリー |
| 171 | KH-GROUP-ECAN-MAG-171 | E-CAN NS |
| 167 | KH-MR-MELD-CP-LIVE-WORK-167 | MELD 活線 |
| 165 | KH-NEW-AXIEZ-WAGO-TERMINAL-165 | WAGO 端子 |
| 162 | KH-ALL-MEGA-FIRE-PANEL-162 | 火報盤メガー |
| 158 | KH-HA-PANEL-ELECALL-158 | HA 盤エレコール |
| 149 | KH-VFGLF-SCU20-GS3-149 | SCU-20 GS3 |
| 132 | KH-VFGLF-MELD-RHY-CONNECTOR-132 | MELD RHY |
| 113 | KH-VFGLF-RESOLVER-BOARD-113 | レゾルバ基板 |
| 227 | KH-ALL-SMOKE-FIRE-SERVICE-MELD-227 | 遮煙（**227 duplicate** — [KH-SMOKE-DOOR-MELD-227](../cards/practice-guides/KH-SMOKE-DOOR-MELD-227.md) と相互） |
| 154 | KH-MRL-SMOKE-SHAFT-DETECTOR-154 | シャフト煙 |

（`reconcile-summary` の 23 件中、上表 **21 list** + 227/154 は Wave 59 primary 固定済み。残 2 は extended 側 `duplicate_matches_extended` を ledger 参照。）

## §6 連携（優先ペア）

| 軸 | リンク |
| --- | --- |
| SCU | **233** ↔ [228](../cards/practice-guides/KH-SCU20-CONN-TEST-228.md) ↔ **149** ↔ **422** |
| HA | **221** ↔ **98** ↔ 320/207/206 |
| 本スロー | **176** ↔ [392](../cards/case-summaries/KH-VFGLF-BRAKE-SW-392.md) 索引 |
| レゾルバ | **113** ↔ [411](../cards/case-summaries/KH-VFGLF-HOIST-RESOLVER-WIRE-411.md)（基板 vs 線） |
| MELD | **167** ↔ **132** ↔ **174** ↔ [101](../cards/case-summaries/KH-IPU-MELD-BATTERY-POLARITY-101.md) |
| 気配り | **407** ↔ **382** ↔ **414**（U-CAN / 12V / 421 LED） |
| 群管理 | **171** ↔ 384/422/371 |
| 遮煙 | **227** ↔ KH-SMOKE-DOOR-MELD-227 ↔ **154** ↔ **346** |
| ELSGW / PuTTY | **415** ↔ **130** ↔ **336**（**263** は ESC 別系統） |
| エレコール HA | **158** ↔ **228** ↔ **149/422** |

## 運用

- catalog / `elv-*-reference` の **record_id を出典にしない**（decisions 2026-10-19）
- primary カード間のみ §6 を増やす（マージ PR 不要）

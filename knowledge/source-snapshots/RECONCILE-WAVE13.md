---
snapshot_type: "reconciliation_wave_log"
wave: 13
generated_on: "2026-10-19"
---

# Wave 13（101 MELD 極性 + SCU 233/422 + duplicate primary）

## 新規カード

| list | knowledge_id | 桶 |
| --- | --- | --- |
| 101 | [KH-IPU-MELD-BATTERY-POLARITY-101](../cards/case-summaries/KH-IPU-MELD-BATTERY-POLARITY-101.md) | other → MELD/IPU |
| 233 | [KH-SCU20-FLASH-REWRITE-233](../cards/practice-guides/KH-SCU20-FLASH-REWRITE-233.md) | comm / メンテコン |
| 422 | [KH-GS3-PART-NO-SCU20-422](../cards/case-summaries/KH-GS3-PART-NO-SCU20-422.md) | comm（149 と対） |
| 171 | [KH-GROUP-ECAN-MAG-171](../cards/case-summaries/KH-GROUP-ECAN-MAG-171.md) | group_call |
| 176 | [KH-ALL-GROUND-N00-NORMAL-SLOW-176](../cards/case-summaries/KH-ALL-GROUND-N00-NORMAL-SLOW-176.md) | power/横断 |
| 113 | [KH-VFGLF-RESOLVER-BOARD-113](../cards/case-summaries/KH-VFGLF-RESOLVER-BOARD-113.md) | 空回し（411 と対） |

## duplicate_match — 本 Wave で primary を固定した list

| list | primary（カード化根拠） | 索引のみ（出典にしない） |
| --- | --- | --- |
| 233 | `elv-scu20-flash-rewrite-tool-compatibility-id233` | `elv-sw-change-reference` |
| 113 | `case-elv-vfglf-resolver-board-free-run-unavailable-id113` | `elv-temporary-slow-issues` |
| 171 | `case-elv-e-can-special-operation-hall-call-failure-id171` | `elv-group-operation-issues` |
| 176 | `case-elv-normal-slow-unavailable-ground-connection-id176` | `elv-normal-slow-issues` |

既カード済み duplicate（174/167/149/132 等）は Wave12 以前のカードを primary とする。

次: duplicate 残（221/240/319/411…）、**display** / **comm** 桶、ESC draft、high_importance unmatched 13。

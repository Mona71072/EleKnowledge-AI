---
snapshot_type: "reconciliation_wave_log"
wave: 2
generated_on: "2026-10-19"
review_status: unreviewed
publication_status: not_published
---

# 体系化 Wave 2（未整備・高/重要から3テーマ）

Wave1 の次。**Lists 初期スナップショット §節** と OneNote スナップショットを突合（[crosswalk](../validation/snapshot-crosswalk-wave1-2.md)）。KB・承認・RAG 対象外。

| list_item_id | 重要度 | テーマ | knowledge_id | draft 写し | カード |
| --- | --- | --- | --- | --- | --- |
| 394 | ↑高 | ピットタラップ位置 / 800mm | KH-PIT-TRAP-POSITION-394 | [ELV_ピットタラップ取付位置事例.md](../drafts/ELV_ピットタラップ取付位置事例.md) | [KH-PIT-TRAP-POSITION-394.md](../cards/practice-guides/KH-PIT-TRAP-POSITION-394.md) |
| 416 | ↑高 | 長周期振動感知器短絡ジャンパ | KH-VFGH-VIBRATION-JUMPER-416 | [ELV_VFGH_長周期振動感知器短絡ジャンパ知見.md](../drafts/ELV_VFGH_長周期振動感知器短絡ジャンパ知見.md) | [KH-VFGH-VIBRATION-JUMPER-416.md](../cards/practice-guides/KH-VFGH-VIBRATION-JUMPER-416.md) |
| 392 | ↑高 | VFGLF 本スロー BK1 | KH-VFGLF-BRAKE-SW-392 | [ELV_VFGLF_ブレーキスイッチ本スロー不能事例.md](../drafts/ELV_VFGLF_ブレーキスイッチ本スロー不能事例.md) | [KH-VFGLF-BRAKE-SW-392.md](../cards/case-summaries/KH-VFGLF-BRAKE-SW-392.md) |

## 選定理由（短く）

- **394**: 据付・検査・複数基準（600mm / 800mm）の整理。機種欄は全エレだが内容は据付一般。
- **416**: 仕様世代（BSER→BSER-CP）とジャンパ有無。作業前確認向け。
- **392**: 本スロー・終点調整後の BK1 系。症状と調査順が Lists §392 に具体あり。

## 意図的に Wave2 から外した高/重要（例）

| list_item_id | 理由 |
| --- | --- |
| 413 | 原因・対策がスナップショット保留 |
| 14 | タイトル・内容が情報管理保留 |
| 350 | 次バッチ候補（群管理/UPS。394/416/392 と被りにくい） |
| 1 / 2 | 同一タイトル「かご内振動」。横断1カード化は別途 |

## 次

- Lists §節・OneNote スナップショット・（後続）KB と突合
- `python3 scripts/knowledge/build_reconcile_ledger.py` で 392/394/416 primary **一致** 確認
- Wave3 候補: 350（UPS）、151（P1/7SEG）、137（巻上機ビス）など

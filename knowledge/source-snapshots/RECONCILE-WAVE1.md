---
snapshot_type: "reconciliation_wave_log"
wave: 1
generated_on: "2026-10-19"
review_status: unreviewed
publication_status: not_published
---

# 体系化 Wave 1（下書き候補）

[RECONCILE.md](./RECONCILE.md) の **未整備・重要度 高/重要** から、最初の 3 テーマを **Lists 初期スナップショット** と突合して下書き化。OneNote 紐付けは [validation/snapshot-crosswalk-wave1-2.md](../validation/snapshot-crosswalk-wave1-2.md)。承認・公開・RAG 対象外。

| list_item_id | 出典（Lists 節） | draft 写し | AI向けカード |
| --- | --- | --- | --- |
| 417 | §417 | [ELV_VFGLF_I-CAN未接続_乗場バックアップ不可事例.md](../drafts/ELV_VFGLF_I-CAN未接続_乗場バックアップ不可事例.md) | [KH-VFGLF-ICAN-HALL-BACKUP-417.md](../cards/case-summaries/KH-VFGLF-ICAN-HALL-BACKUP-417.md) |
| 398 | §398 | [ELV_AXIEZ-LINKS_照明安定化電源地絡事例.md](../drafts/ELV_AXIEZ-LINKS_照明安定化電源地絡事例.md) | [KH-AXIEZ-LIGHTING-GROUND-398.md](../cards/case-summaries/KH-AXIEZ-LIGHTING-GROUND-398.md) |
| 345 | §345 | [ELV_LINKs_WOS工法切替_DLDPコネクタ知見.md](../drafts/ELV_LINKs_WOS工法切替_DLDPコネクタ知見.md) | [KH-LINKS-WOS-DLDP-345.md](../cards/practice-guides/KH-LINKS-WOS-DLDP-345.md) |

## 選定理由（短く）

- **417 / 398 / 345**: 機種・テーマ（通信、地絡、据付切替）が異なり、リスト本文の情報量も段階的に異なる（417 は伏せ字が多い）。
- ID 14 および症状伏せが多い件は Wave 1 から除外。

## 次

- 担当者が 3 件を Lists 節・OneNote スナップショット・（後続）KB と突合
- 問題なければ Wave 2 の継続
- `python3 scripts/knowledge/build_reconcile_ledger.py` で primary **一致** 確認

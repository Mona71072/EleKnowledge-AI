---
snapshot_type: "reconciliation_wave_log"
wave: 1
generated_on: "2026-10-19"
review_status: unreviewed
publication_status: not_published
---

# 体系化 Wave 1（下書き候補）

[RECONCILE.md](./RECONCILE.md) の **未整備・重要度 高/重要** から、最初の 3 テーマを Lists スナップショットのみから下書き化した。承認・公開・RAG 対象外。

| list_item_id | record_id | ファイル |
| --- | --- | --- |
| 417 | `case-elv-vfglf-i-can-disconnected-hall-backup-unavailable-id417` | [ELV_VFGLF_I-CAN未接続_乗場バックアップ不可_ID417事例.md](../drafts/ELV_VFGLF_I-CAN未接続_乗場バックアップ不可_ID417事例.md) |
| 398 | `case-elv-axiez-links-car-flex-lighting-power-ground-fault-id398` | [ELV_AXIEZ-LINKS_照明安定化電源地絡_ID398事例.md](../drafts/ELV_AXIEZ-LINKS_照明安定化電源地絡_ID398事例.md) |
| 345 | `knowhow-elv-links-wos-switch-dldp-connector-id345` | [ELV_LINKs_WOS工法切替_DLDPコネクタ_ID345知見.md](../drafts/ELV_LINKs_WOS工法切替_DLDPコネクタ_ID345知見.md) |

## 選定理由（短く）

- **417 / 398 / 345**: 機種・テーマ（通信、地絡、据付切替）が異なり、リスト本文の情報量も段階的に異なる（417 は伏せ字が多い）。
- ID 14 および症状伏せが多い件は Wave 1 から除外。

## 次

- 担当者が 3 件を原文 Lists / 資料と突合
- 問題なければ Wave 2（残り 10 件の高/重要）の選定
- `python3 scripts/knowledge/build_reconcile_ledger.py` で ID 417/398/345 が **一致** に移ったことを確認

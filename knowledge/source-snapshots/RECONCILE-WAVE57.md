---
snapshot_type: "reconciliation_wave_log"
wave: 57
generated_on: "2026-10-19"
---

# Wave 57（連携是正 + registry 索引）

## 新規テーマ

なし（Lists §390/390 済）。**累計 Wave テーマ: 395**（据え置き）。

## 連携是正

| クラスタ | 変更 |
| --- | --- |
| **放送/BGM** | 179↔122 本文・表の「未カード」除去 |
| **試験/官検** | 251→280 リンク |
| **部品手配** | 311→236 |
| **MR 部品** | 355→340、362→390 |
| **IH/非常** | 328↔423 |
| **CL1/ケーブル** | 8→201 |
| **ヘルスエア** | 221→225/360 |
| **SCU-20** | 228↔233/149、233/149 表更新 |
| **気配り戸** | 407↔408、408↔352/382/424 |
| **遮煙/UCMP** | 227→346/154/390 |
| **群管理** | 384↔371/253、171/349/147/286 から 384/371 リンク |

## registry

- `build_registry.py` が **`list-item-to-card.jsonl`** を生成（390 一意 list_item_id、395 行＝重複 primary 5 件）
- [CONTRACT.md](../CONTRACT.md) registry 節に追記

## 残タスク（Wave 58+）

- 関連表の `| **NNN** |` 未リンク（推定 ~190 行）— `list-item-to-card.jsonl` を参照しクラスタ単位で継続
- Lists **§384** 原因文（スナップショット途中切れ）— Lists 更新待ち
- draft 台帳 **107** unmatched（`build_reconcile_ledger.py` — カード数とは別指標）
- OneNote 未一致页

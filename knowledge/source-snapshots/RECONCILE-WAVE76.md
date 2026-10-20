---
snapshot_type: "reconciliation_wave_log"
wave: 76
generated_on: "2026-10-19"
---

# Wave 76（PATCHES 重複解消・クラスタ §6）

## スクリプト

- **`append_cluster_related_rows.py`** — `384` / `92` / `269` / `422` の **重複キーを 1 リストにマージ**（後勝ちバグ解消）
- 同 `--apply` — **6** カード更新（149/167/132/113/382/233 等）

## 手動 §6

- **113** ↔ **411** — Markdown リンク + duplicate 軸明記
- **167** ↔ **132** — 相互リンク
- **174** — 132/167/101 リンク

## 検証

- `build_registry.py` — **repair 0**, cards **657**

## 残

- Lists §384 cause 全文（スナップショット未完）
- duplicate §6 横展開（176↔392 以外の細部）
- OneNote PDF absent 114

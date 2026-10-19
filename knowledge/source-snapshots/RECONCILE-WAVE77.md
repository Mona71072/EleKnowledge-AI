---
snapshot_type: "reconciliation_wave_log"
wave: 77
generated_on: "2026-10-19"
---

# Wave 77（duplicate §6 横展開・体裁）

## §6 連携

- **MELD クラスタ** — 101/174/167/132 相互 Markdown 化
- **176** ↔ **392** リンク
- **414** — 392 パス是正 + **382** 行
- **221** ↔ **98** HA リレー
- **171** → **422** 群管理 SCU
- **422** — script で **233/149** 行追加

## カード体裁

- **384** — frontmatter 余分 `---` 削除、§6 **371 重複行** 削除（Lists 原因は仍スナップショット切れ）

## ドキュメント

- **`duplicate-list-primary.md`** — レゾルバ / MELD / 気配り §6 行追加

## 検証

- `build_registry.py` — **repair 0**

## 残（ブロッカー外）

- Lists §384 原因全文（正本スナップショット未更新）
- card-kb ingest、OneNote PDF absent 114

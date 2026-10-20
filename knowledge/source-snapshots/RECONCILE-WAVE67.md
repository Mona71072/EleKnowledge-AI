---
snapshot_type: "reconciliation_wave_log"
wave: 67
generated_on: "2026-10-19"
---

# Wave 67（ROADMAP 優先キュー — 群管理・ドア・据付の §6 連携）

## 新規テーマ

なし。**累計 Wave テーマ: 395**。

## 実施

### 群管理・呼び（group_call bucket）

- `append_cluster_related_rows.py --apply` — **92**（338/228/286）、**269**（338/99/371）、**384↔422↔171**、**422**（384/371/228）
- **384** §3 OneNote（cf01 + :145）— ユーザー編集中のカードと整合

### 開閉門（door bucket）

- **354** → **403**（D14/釦CPU 系）
- **419** — CM-LB 戸短・432/433・403 への §6 リンク
- **400** — 既存 403/434 連携確認済み

### 据付寸法（install_dim）

- **361** → **394** ピット横断リンク

### 関連表

- `fix_related_list_links.py` — **132** ファイル / **148** 置換（`| **NNN** |` → カードリンク）

## registry

- `build_registry.py`: **repair 0**

## 残（計画外依存）

- Lists **§384 原因全文**
- カード KB **ingest** 実装

## 次

- duplicate_matches 23（ledger）— 必要時のみ primary 統合
- ドア bucket 残（105/346 等）— 症状軸で追加連携は INDEX §ドア を正本に

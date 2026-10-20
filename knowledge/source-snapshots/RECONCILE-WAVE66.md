---
snapshot_type: "reconciliation_wave_log"
wave: 66
generated_on: "2026-10-19"
---

# Wave 66（未検出 ~108 — 再 grep とクラスタ連携）

## 新規テーマ

なし。**累計 Wave テーマ: 395**。

## 実施

### 残件照合

- `scan_onenote_title_residuals.py` — OneNote 未参照 **220** Lists 項を **全文タイトル**で再検索 → **新規 0**（`lists-onenote-residual-hits.jsonl` 空）
- Wave 63 の **索引未検出 ~108** は、タイトル未収録が正。誤 attach はしない。

### §3 クラスタ連携（92 カード）

- `enrich_onenote_no_hit_crosslinks.py --apply` — **92** 件の `### OneNote` を統一文案 + **関連クラスタ** Markdown リンクへ
- クラスタ例: SCU 228/233/149、エレナビ 336/415/373、群管理 384/371/253、気配り 403/408/424、ESC、遮煙 227、LV 戸 432、LINKs 345、PuTTY 130、ER 348/379

### §384 是正（Lists 原因文未完）

- `cf01bae3…:1` 頁 — Lists **384 同一タイトル**リンクを §3 に要約（GH1↔GP1 未完は **Lists 正本待ち**）
- `:145` 索引は navigation のまま

## registry

- `build_registry.py`: **repair 0**

## 横断（list 1/2）

- [KH-ROLLER-GUIDE-CAR-VIBRATION-1-2](../cards/case-summaries/KH-ROLLER-GUIDE-CAR-VIBRATION-1-2.md) — §8 に DGN/測定カードとの混同防止を追記（OneNote タイトル一致なし）

## 次

- Lists **§384 原因全文** — スナップショット更新後に §3 追記のみ
- カード KB ingest（設計: `card-kb-two-tier-retrieval.md`）
- 必要なら `fix_related_list_links.py` 再実行（関連表増分）

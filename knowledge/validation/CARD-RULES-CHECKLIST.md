---
status: draft
last-verified: "2026-10-19"
related-code:
  - knowledge/CONTRACT.md
  - knowledge/LAW-RAG-REF-WORKFLOW.md
  - knowledge/cards/TEMPLATE.md
  - knowledge/cards/_SOURCE-LEGEND.md
  - knowledge/registry/APPLICABILITY-TAXONOMY.md
---

# テーマカード合格チェック（Wave 作業用）

正本: [CONTRACT.md](../CONTRACT.md) / 本文見出し: [TEMPLATE.md](../cards/TEMPLATE.md) / 出典: [_SOURCE-LEGEND.md](../cards/_SOURCE-LEGEND.md) / 適用軸: [APPLICABILITY-TAXONOMY.md](../registry/APPLICABILITY-TAXONOMY.md)。

## 書く前（Must）

- [ ] Lists は [CONTRACT.md](../CONTRACT.md) 照合作業の **初期スナップショット §list_item_id** と突合（文言の創作禁止）。**§8・索引に snapshot ファイルパス／Markdown リンクを載せない** — **Lists §{n}** のみ
- [ ] 情報管理 **保留** 節は **症状・原因・progress を再掲しない**（Notes 等、公開範囲だけ索引可 — 例: 189 JPA）
- [ ] 出典は **lists_item / onenote_page / kb_document / law_rag**（写しは `draft_record` のみ frontmatter）。`record_id` は出典表に載せない
- [ ] **法令系**（Lists 豆知識）→ [LAW-RAG-REF-WORKFLOW.md](../LAW-RAG-REF-WORKFLOW.md): **PoC 53法令**に該当する行は **`ref_type: law_rag` + `law_id`**（法・令・規則・関連省令を漏れなく）。**告示・条例・検査シート・イエローブック**は **OneNote 法令まとめ**（`401f288f…`）のみ — 条文・告示の二重掲載禁止
- [ ] **通常 RAG**（`CATEGORY_MAP` / `kb-metadata-catalog`）に法令 category 無し — 条文は **`mode=law`（dev）** と索引。`resolve_kb_refs.py` は法令対象外

## frontmatter（Must）

- [ ] `title` に **`ID417` 形式や list 番号を入れない**
- [ ] `model_scope.lists_model_label` = スナップショット `Model:` 行
- [ ] **AXIEZ-LINKs**: `product_lines: [AXIEZ-LINKs]` + `control_methods: [VFGLF]`（Lists が VFGLF ラベルのとき）
- [ ] **CM-LB / CM-MA / KM-LD**: `machine_room: [MR]` + 該当 `control_methods`（VFGLB-K / VFGH 等）
- [ ] **MRL機種 / MR機種** Lists ラベル → `machine_room` MRL / MR（**CMR は書かない**）
- [ ] **エスカ**: `product_lines: [escalator]` + `control_methods: [SVFC]` 等。エレ制御軸に載せない
- [ ] KB 参照は `kb_verify_status: pending` 起票。本文で手順断定しない

## 本文 9 見出し（Must — 順序固定）

1. 使う場面・対象条件（§1 で **制御・machine_room・door/guide 軸** を先に書く）
2. 症状・現象
3. ソース要約（### Lists / ### OneNote）
4. 統合した回答・ノウハウ
5. 調査・確認手順
6. **関連事例と条件の違い**（`## 関連事例` 単独は不可）
7. KB確認に基づく追記
8. **正式資料・元情報**（`## 正式資料` 単独は不可）— Lists は **§番号**、`onenote_id`、`law_id` / KB 図番（[decisions](../../docs/decisions-2026-10-19-knowledge-evidence-sources.md)）
9. 未確認事項

## Wave 後（Should）

- [ ] 法令系テーマ → [LAW-FREQUENT-THEMES.md](../registry/LAW-FREQUENT-THEMES.md) に行追加（または既存行のカードリンク更新）
- [ ] [INDEX.md](../cards/INDEX.md) / `RECONCILE-WAVEn.md` / [RECONCILE-ROADMAP.md](./RECONCILE-ROADMAP.md)
- [ ] `python3 scripts/knowledge/build_registry.py`

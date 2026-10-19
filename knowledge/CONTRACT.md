# テーマカードと registry の最小契約

## テーマカード（`knowledge/cards/`）

```yaml
knowledge_id: KH-XXXX          # 安定ID
kind: case_summary | practice_guide
status: draft | approved | retired
card_version: 1
title: "人が読むテーマ名（IDを含めない）"
symptoms: []                   # 検索用
model_scope:
  lists_model_label: []        # Lists スナップショット § の Model 行をそのまま（略称≠制御のとき必須）
  product_lines: []            # AXIEZ, Nexcube, AXIEZ-LINKs, MELCITY …
  machine_room: []             # 機械室大分け: MRL | MR のみ（Lists MRL機種/MR機種）。catalog 画像の CMR 表記は MR に読み替え。不明は空
  model_abbreviations: []      # CM-LB, CM-MA, KE-PF …（機種略称 catalog）
  control_methods: []          # VFGH, VFGLB-K, VFGLF, VFGLB …（制御プラットフォーム）
  guide_systems: []            # 走行系ガイド方式: roller_guide 等（機種略称より優先して開く軸）
  door_families: []            # ドア大分類: L型 | K型（Lists/OneNote/Vault の明示のみ。機種略称≠ドア）
  door_types: []               # ドア型式コード: LV5K-2S, LV6K-CO/2S, LV0K-7-2S, KV4K-3/KV4, 気配りドア付 等（Lists 本文・品目表優先）
  observed_on: []              # 発生確認の要約（従来互換・検索用）
  may_apply_to: []             # 適用可能性（未確認可）
  excludes: []
  scope_note: ""               # 全エレ機種・複数制御など短文
source_refs:
  # 参照元（利用者・AIが辿る原情報）は次の4種類を「出典」と呼ぶ（draft_record は写し索引）
  - ref_type: lists_item      # Microsoft Lists の list_item_id（スナップショット上の項目番号）
    list_item_id: "417"
    source_id: ""             # evidence_sources.source_id（任意・監査用）
  - ref_type: onenote_page
    onenote_id: "uuid:section"
  - ref_type: kb_document       # 共有 KB（Bedrock）上の PDF
    document_number: "C-6-R56.1"   # 図番・Lists/OneNote 由来の業務番号
    kb_filename: ""                 # カタログ解決後（例: TI-1335.pdf）
    kb_category: ""                 # C資料 / テクニカルインフォメーション / 据付基準 等
    kb_verify_status: pending       # pending | catalog_matched | catalog_ambiguous | not_in_catalog | content_reviewed
    locator: ""                     # 確認後: 節・ページ
    summary_from_kb: ""             # 確認後: KB 本文に基づく短い要約（§3 へ転記可）
  - ref_type: law_rag               # EleKnowledge 法令専用 KB（e-Gov 条文・PoC 53法令）
    law_title: ""                   # legal-rag-target-laws.md の法令名
    law_id: ""                      # 同表のフォルダ名（S3 / メタデータ）
    retrieval: "mode=law"           # dev の法令チャット。本番は設計書どおり未有効可
    law_rag_status: current         # 一覧外（告示・条例等）は付けない
  # 下記は原情報ではなく、Vault 写しの棚位置（照合・編集用。出典の代わりに使わない）
  - ref_type: draft_record
    record_id: ""
    note: "knowledge/drafts 上の同一テーマ写し"
review_status: in_review
publication_status: not_published
cloud_approval: not_reviewed
```

整理軸（機種略称・制御方式・Vault 棚・エスカ）: [registry/APPLICABILITY-TAXONOMY.md](./registry/APPLICABILITY-TAXONOMY.md)

本文セクション（固定順の詳細: [cards/TEMPLATE.md](./cards/TEMPLATE.md)。設計 [design-2026-10-01-knowhow-flywheel.md](../docs/design-2026-10-01-knowhow-flywheel.md) §3 と整合）:

1. 使う場面・対象条件
2. 症状・現象
3. ソース要約（Lists / OneNote。伏せ字は「保留」と明記）
4. 統合した回答・ノウハウ（Markdown だけで答えられる範囲）
5. 調査・確認手順
6. 関連事例と条件の違い
7. KB確認に基づく追記（`content_reviewed` 後のみ中身を書く）
8. 正式資料・元情報（**Lists / OneNote / KB / 法令 RAG / OneNote法令まとめ** の表。`draft_record` は写しとして別記）
9. 未確認事項

## 照合作業（Must）

テーマカード・Wave draft を書く／直す前に、保存スナップショットと突合する。

| 種別 | 正本（取得時点・不変） |
| --- | --- |
| Lists | `source-snapshots/首都工_不具合情報共有リスト_初期スナップショット.md` の `## Lists item ID {n}`（**照合用**。カード §8・索引には **`Lists §{n}` / `list_item_id` のみ** — 本パスを繰り返さない） |
| OneNote | `source-snapshots/onenote/*.md` の frontmatter `onenote_id` |
| KB | 共有 KB PDF。索引 `docs/kb-metadata-catalog-*.md` → `registry/kb-document-index.jsonl`。手順 [KB-REF-WORKFLOW.md](./KB-REF-WORKFLOW.md) |
| 法令 RAG | 本家 `docs/features/development/legal-rag-target-laws.md` の `law_id`。手順 [LAW-RAG-REF-WORKFLOW.md](./LAW-RAG-REF-WORKFLOW.md) |
| 告示・条例・社内法令整理 | OneNote セクション `401f288f-0e3f-4ada-b89d-14799070162d` のスナップショット（法令 RAG **53件外**） |

合意・理由の正本: [docs/decisions-2026-10-19-knowledge-evidence-sources.md](../docs/decisions-2026-10-19-knowledge-evidence-sources.md)

## registry

- `registry/list-item-to-record.jsonl`: `list_item_id` → draft `record_id`（多対多は複数行。Lists **出典**ではなく照合索引）
- `registry/list-item-to-card.jsonl`: `list_item_id` → `knowledge_id` + `card_path`（カード frontmatter の Lists 参照。連携・索引用）
- 関連表の `| **NNN** |` 一括リンク: `scripts/knowledge/fix_related_list_links.py`（索引更新後に実行可）
- カード間 Markdown リンク path: `scripts/knowledge/normalize_same_dir_links.py`
- OneNote 頁役割分類: `scripts/knowledge/classify_onenote_pages.py` → `registry/onenote-page-catalog.jsonl`（`index` / `content` / `cross_topic` / `hybrid` / `empty_or_attachment_only`）
- カード↔OneNote 監査: `scripts/knowledge/build_onenote_audit_ledger.py` → `onenote-card-audit.jsonl` + Wave61–63 `onenote-wave61-63-audit.jsonl`
- 拡張 hit 再検証: `scripts/knowledge/verify_onenote_extended_hits.py` → `lists-onenote-extended-verified.jsonl` / `-rejected.jsonl`（prefix-only 除外）
- 監査台帳の navigation 適用: `scripts/knowledge/apply_onenote_wave_audit.py`（**`--apply`**。index/cross 頁のみ）
- 未付与 Lists の **全文タイトル再 grep**: `scripts/knowledge/scan_onenote_title_residuals.py` → `lists-onenote-residual-hits.jsonl`
- OneNote 未一致カードの **クラスタ相互リンク**: `scripts/knowledge/enrich_onenote_no_hit_crosslinks.py`（**`--apply`**。`source_refs` は増やさない）
- 群管理/ドア/据付 **§6 連携行追加**: `scripts/knowledge/append_cluster_related_rows.py`（**`--apply`**）→ 続けて `fix_related_list_links.py`
- 据付・試験・調整 **§6 ハブ行**: `scripts/knowledge/append_adjustment_hub_links.py`（**`--apply`**。`KH-ALL-INSTALL-TEST-ADJUST-HUB`）
- OneNote  outgoing から **KB 図番候補**: `scripts/knowledge/build_onenote_pdf_kb_candidates.py` → `registry/onenote-pdf-kb-candidates.jsonl`（**pending** のみ。断定は KB-REF-WORKFLOW）
- 候補の **カタログ filename 突合**: `scripts/knowledge/resolve_onenote_pdf_candidates.py` → `onenote-pdf-kb-candidates-resolved.jsonl` + `validation/onenote-pdf-kb-candidate-status.md`
- `page_role` 付与: `scripts/knowledge/apply_onenote_page_roles.py`（catalog から frontmatter）
- 索引頁 §3 簡略化: `scripts/knowledge/normalize_onenote_index_sections.py`（**navigation のみ** — 他テーマタイトルを §3 に載せない）
- Lists タイトル一致 OneNote: `attach_onenote_title_hits.py` — **既定は候補のみ**（`onenote-attach-candidates-title.jsonl`）。カード更新は **`--apply`**
- OneNote §3 同期・拡張 hit: `sync_onenote_sections.py` → `lists-onenote-extended-hits.jsonl`。**カード書込は `--apply` のみ**
- frontmatter 閉じ `---` 修復: `scripts/knowledge/fix_card_frontmatter_closing.py`
- draft 経由 OneNote: `attach_onenote_from_drafts.py` → `lists-onenote-draft-hits.jsonl`。**カード書込は `--apply` のみ**
- `registry/card-source-links.jsonl`: `knowledge_id` → 上記 `source_refs` の展開
- `registry/onenote-id-index.json`: 生成物（`scripts/knowledge/build_registry.py`）

## repair queue

frontmatter がパース不能な draft は `queues/repair/MANIFEST.md` に載せ、照合・カード生成から除外する。

## OneNote 1対多

同一 `onenote_id` が複数 `record_id` に付くことを **重複エラーにしない**。catalog / case / review-hold など用途が異なる。

## OneNote `onenote_id`（正本と略称）

- **正本**: フル `{uuid}:{page}` — `source_refs`・スナップショット・`registry/onenote-id-index.json`（`build_registry.py`）
- **§8**: フル ID または `uuid…:page` 省略表記可（メタデータが正）
- **§3/§6**: 文脈で uuid が分かるとき **`:page` suffix のみ**可。AI は registry / catalog で **フル ID に解釈**（`:page` 単独は uuid 横断で一意ではない）
- 合意の正本: [docs/decisions-2026-10-19-knowledge-evidence-sources.md](../docs/decisions-2026-10-19-knowledge-evidence-sources.md)「OneNote onenote_id の正本と略称」

## OneNote 頁の役割（カード統合）

| `page_role` | 意味 | カード §3 |
| --- | --- | --- |
| `index` | リンク列挙・事例目次 | **navigation のみ**（`onenote_id` + スナップショット名）。索引内の**他テーマ名は転記しない** |
| `content` | 手順・条件・事実の本文 | Lists/KB と突合した**短い要約**のみ（URL omitted 列挙だけの頁は根拠にしない） |
| `cross_topic` | 横断ノウハウ | ホームカード 1 枚 + 他カードは相互リンク |
| `hybrid` | 索引＋一部本文 | 当該 Lists テーマに関する行だけ要約、目次部分は navigation |
| `empty_or_attachment_only` | 実質空・添付のみ | `source_refs` に載せない |

自動 title / prefix / draft 一致は **監査台帳の候補**として扱い、未確認のまま §3 へ他テーマ語を増やさない。公開・RAG 経路は [card-kb-two-tier-retrieval.md](../docs/features/development/card-kb-two-tier-retrieval.md)（ドラフト）。

---

knowledge_id: KH-ALL-BARRIER-FREE-INSPECTION-135
kind: practice_guide
status: draft
card_version: 1
title: "バリアフリー適合検査 — Lists 入口"
symptoms:
  - "バリアフリー"
  - "適合検査"
  - "円滑化基準"
  - "誘導基準"
model_scope:
  lists_model_label:
    - "全エレ機種"
  observed_on: []
  may_apply_to:
    - "バリアフリー法で何を確認するか不明"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "135"
  - ref_type: onenote_page
    onenote_id: "401f288f-0e3f-4ada-b89d-14799070162d:39"
    page_role: cross_cutting
  - ref_type: law_rag
    law_title: "高齢者、障害者等の移動等の円滑化の促進に関する法律"
    law_id: "418AC0000000091_20250401_505AC0000000024"
    retrieval: "mode=law"
    law_rag_status: current
  - ref_type: law_rag
    law_title: "高齢者、障害者等の移動等の円滑化の促進に関する法律施行令"
    law_id: "418CO0000000379_20250601_506CO0000000221"
    retrieval: "mode=law"
    law_rag_status: current
  - ref_type: law_rag
    law_title: "高齢者、障害者等の移動等の円滑化の促進に関する法律施行規則"
    law_id: "418M60000800110_20250601_506M60000800100"
    retrieval: "mode=law"
    law_rag_status: current
  - ref_type: law_rag
    law_title: "高齢者、障害者等が円滑に利用できるようにするために誘導すべき建築物特定施設の構造及び配置に関する基準を定める省令"
    law_id: "418M60000800114_20250601_506M60000800100"
    retrieval: "mode=law"
    law_rag_status: current
---
# バリアフリー適合検査 — Lists 入口

## 使う場面・対象条件

**全エレ** 現場で **バリアフリー法の適合検査** が話題になったときの **Lists 135 入口**。本カードは **Lists / OneNote への索引** と **法令 RAG へのリンク** のみ — 条文・告示の二重掲載はしない。

## 症状・現象

- 検査で **何を確認するか分からない**（Lists symptoms）。

## ソース要約

### Lists（135）

- **各検査項目は添付資料参照**（Lists cause）。Lists 本文は入口説明程度。
- エレの C/TI 手順カードではなく **建築・検査チェック** の索引。

### OneNote（401f288f…:39）

- **円滑化基準**（義務・チェックシートは建築提出）と **誘導基準**（任意・容積率緩和等）の説明（Lists 135 と同趣旨）。
- **検査例**（22/11/25 歌舞伎町）：かご内出入口寸法、手すり、アナウンス、車椅子押しボタン、他職種スイッチ高（1100 mm 付近の指摘例）。
- チェックシート本体は OneNote 添付（スナップショット未コピー）。

## 統合した回答・ノウハウ

詳細テーマまとめ: [LAW-FREQUENT-THEMES.md §A](../../registry/LAW-FREQUENT-THEMES.md#a-バリアフリー円滑化)

1. **法律・施行令・施行規則・誘導基準省令** → dev **法令チャット**（`mode=law`）。frontmatter の `law_id` 4件。
2. **検査項目** → OneNote **:39** 添付 / Lists 135 添付。条文は写さず索引のみ。
3. **通常 RAG** ではバリアフリー条文は拾われない（共有 KB のみ）。
4. Lists 135 は **現場が迷った入口**。

## 調査・確認手順

1. dev 環境なら **法令チャット** で円滑化法・誘導省令を質問（条文は e-Gov リンク付きで返る想定）。
2. **OneNote 法令まとめ**（`:39` ほか同セクション）で **検査チェック・告示** を確認。
3. 必要なら Lists §135 / OneNote 添付の **検査項目**。
4. エレ不具合（制御・配線）と混同しない。
5. C/TI が必要なら **別クエリ**（法令カードの代替にならない）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **135** | **Lists 入口 → 法令 RAG（4法令）＋ OneNote 検査/告示** |
| [144](./KH-ALL-OFFICE-ABC-WORK-144.md) | **A/B/C 工事**（契約区分） |
| [346](./KH-ALL-SMOKE-DOOR-SEAL-346.md) | **遮煙認定**（共有 KB の S-31 等） |

## KB確認に基づく追記

（共有 KB カタログ対象外。法令条文は `law_rag` 索引 — [LAW-RAG-REF-WORKFLOW.md](../../LAW-RAG-REF-WORKFLOW.md)。）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §135 |
| OneNote | `401f288f-0e3f-4ada-b89d-14799070162d:39`（検査入口）。告示・社内整理は同セクション `:33` 以降のスナップショット |
| 法令 RAG | 上記 frontmatter `law_id` ×4（一覧正本: 本家 `docs/features/development/legal-rag-target-laws.md` §3） |
| 法令チャット | `mode=law`（**dev** のみ。本番は設計書どおり未有効） |
| KB（共有） | Lists / OneNote **添付** のみ（filename 未索引） |

## 未確認事項

- 本番での法令 RAG 有効化・対象拡大（共同確認待ち）。
- Know-how テーマカードからアプリ内で `law_id` をワンクリック開く UI（未実装 — reconcile 作業ツリーの `knowledge/cards`）。

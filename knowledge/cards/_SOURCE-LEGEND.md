# 出典の書き方（カード共通）

**参照元**は次の4種類（+ 写し索引 `draft_record`）。カードを書く前に **保存スナップショット** と突合する（手順: [CONTRACT.md](../CONTRACT.md)「照合作業」／[decisions doc](../../docs/decisions-2026-10-19-knowledge-evidence-sources.md)）。

**機種・制御・機械室（MRL/MR）・guide_systems・ドア**は Lists `Model` と別軸。**L型/K型（door_families）**の下に **LV5K/LV6K・KV 等（door_types）**。[APPLICABILITY-TAXONOMY.md](../registry/APPLICABILITY-TAXONOMY.md)（振動＝ローラーガイド、432＝LV 戸型、72＝K型 family）。

| 種別 | frontmatter | カード §8・索引の書き方 | 照合時に開く正本（執筆者用 — **§8 にパスを書かない**） |
| --- | --- | --- | --- |
| **Lists** | `ref_type: lists_item` + `list_item_id` | **Lists §{n}** または `list_item_id` のみ | [CONTRACT.md](../CONTRACT.md) 照合作業表 → 初期スナップショット `## Lists item ID {n}` |
| **OneNote** | `ref_type: onenote_page` + `onenote_id` | **`onenote_id`**（フル `uuid:page`。§8 は `…:page` 省略可） | 同表 → `source-snapshots/onenote/` |

**OneNote ID（Must）**: `source_refs` と registry は **フル `onenote_id` のみ**。§3/§6 で **`:156` 等の suffix 略称**可 — ただし **同一 uuid が文脈で分かるとき**に限り、AI は `onenote-id-index.json` で **必ずフル ID に解釈**する（`:page` は uuid 横断で一意ではない）。詳細: [decisions-2026-10-19-knowledge-evidence-sources.md](../../docs/decisions-2026-10-19-knowledge-evidence-sources.md)「OneNote onenote_id の正本と略称」。
| **KB** | `ref_type: kb_document` + … | 図番 / `kb_filename` | [KB-REF-WORKFLOW.md](../KB-REF-WORKFLOW.md) |
| **法令 RAG** | `ref_type: law_rag` + … | `law_id` または法令名 | [LAW-RAG-REF-WORKFLOW.md](../LAW-RAG-REF-WORKFLOW.md) |
| **告示・条例・社内法令整理**（53法令外） | `ref_type: onenote_page` | `401f288f…:39` 等 | 同 OneNote スナップショット |

`record_id`（`knowledge/drafts`）は **原情報ではない**。照合・編集用。本文の「正式資料・元情報」では **Lists / OneNote / KB / 法令 RAG** の表を先に書く。

**法令系 Lists 豆知識**: 53法令に載る **法律・令・規則・関連省令** は `law_rag` を付ける。載らない **告示・条例・検査シート** は OneNote 法令まとめのみ。条文の二重掲載禁止。

- タイトル・見出しに `ID417` や `(ID417)` を入れない。番号は `list_item_id` 等のフィールドのみ。
- `knowledge_id` / ファイル名末尾の `-417` 等は **Lists 照合用の慣習**（必須ではない）。出典番号の正は `source_refs.list_item_id`。横断テーマカードは番号なし slug 可（例: `KH-CM-LB-DOOR-SHORT-LATCH`）。
- `list_item_id`（例: `417`）と `record_id`（draft 安定 ID）を混同しない。

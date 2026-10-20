---
status: draft
last-verified: "2026-10-19"
related-code:
  - knowledge/drafts/ELV_機種略称・制御方式一覧_提供画像.md
  - knowledge/drafts/u形エスカレーター_機種一覧.md
  - knowledge/CONTRACT.md
---

# 適用範囲の整理軸（機種・制御方式・Vault 棚）

テーマカードは **Lists の `Model` 欄をそのまま信じず**、次の層を分けて書く。正本の対応表は Vault 写し（出典ではないが **索引として必読**）。

| 層 | 意味 | 正本 |
| --- | --- | --- |
| **機械室区分（machine_room）** | エレの **大分け: MRL（機械室なし）** と **MR（機械室あり）**。Lists の **`MRL機種` / `MR機種`** はこの軸に近い（**制御方式・機種略称とは別**） | 提供画像 catalog の「機械室」列 + Lists `Model:`。§1 表 |
| **機種略称** | 商品・型式（CM-LB, KE-PF, S1UJ1 …） | 下記 catalog + draft の `model_type` |
| **制御方式** | 制御プラットフォーム（VFGH, VFGLB-K, VFGLF …） | 同上 + 制御エラー参照ページ |
| **走行・据付系（guide_systems 等）** | **ローラーガイド**／ガイドシュー／吊り系など、機種名と独立した機械適用 | 図面・据付要須・現場メモ（例: `現場_ガイドシュー異音対策参照`）。Lists 1件だけでは他機種へ拡張断定しない |
| **ドア大分類（door_families）** | **L型 / K型** — ドア機構の大きな分け（Lists「L型ドア」「K型ドア」、OneNote 総点・OLT/CLT 注意）。**機種略称（CM-MA 等）や Lists Model とは別** | Lists 本文（例: list 72 **K型ドア**、242 **L型ドア**）。OneNote（L型/K型の検査间隙・LED 調整注意） |
| **ドア型式（door_types）** | **品目表・Lists のドア型名** — **LV5K / LV6K / LV0K** 系列、**KV4K-3（KV4）** 等の戸閉装置型名、**CO/2S/SS** 表記、**気配りドア付** | Lists **本文・Notes**（`ドアタイプがLV5K-2S`、432 の LV5K-CO/2S）。Vault [ELV_戸の種類_参照記録.md](../drafts/ELV_戸の種類_参照記録.md)（KV/K4 型名）。据付資料 C-18-A9-491.1-J（LV5K/LV6K — 本文未全文レビュー） |
| **Lists Model 欄** | 共有リスト Excel 上のラベル（略称と不一致あり） | Lists スナップショット § の `Model:` 行 |

**分け方が特に重要な例**

1. **かご内振動（Lists §1/2）** — **Model=CM-MA** だが核心は **ガイドローラー周波数と PMT**。→ [KH-ROLLER-GUIDE-CAR-VIBRATION-1-2](../cards/case-summaries/KH-ROLLER-GUIDE-CAR-VIBRATION-1-2.md) は **`guide_systems` 主軸**。
2. **ドア系** — まず **L型 / K型（door_families）** と **LV5K・LV6K・KV 等（door_types）** を分ける。**Model=VFGLF / 全エレ** でも、本文が **LV5K-2S・LV6K** を指定すれば **`door_types` 主軸**（432/433/435）。本文が **K型ドア** のみ（list 72）なら **`door_families: [K型]`** を先に載せ、LV/KV コードは品目表確認まで空でもよい。
3. **LV と KV** — ユーザー現場語彙どおり **LV5K/LV6K 等は door_types**。**KV4K-3 / KV4** 等は Vault「戸の種類」の **戸閉装置型名**として **door_types** に原表記で載せる（L型/K型との対応は原文が結びつけるときだけ `door_families` に書く。推測で L↔LV を固定しない）。
4. **付加機能** — 気配りドア・HMS/MBS は `door_types` に **気配りドア付** 等を足し、制御横断（407）と VFGH 事例（408）を混同しない。
5. **MRL / MR** — 現場・Lists の **二値**だけを `machine_room` に載せる。例: **438/359/439** → **MRL機種**、**371/167** → **MR機種**。**CM-MA / CM-LB / KM-LD**（Nexcube 機械室型）も **`MR`**（MRL カードへ拡張しない）。提供画像 catalog の **CMR 列は索引用の別表記** — カード frontmatter では **CMR を使わない**。

カード frontmatter の `model_scope` は [CONTRACT.md](../CONTRACT.md) の拡張フィールドに従う。

### machine_room（MRL / MR のみ）

| 現場・Lists / 品目 | `machine_room` |
| --- | --- |
| **MRL**・**MRL機種** | `MRL` |
| **MR**・**MR機種**、機械室あり Nexcube（CM-MA, CM-LB, KM-LD …） | `MR` |
| Lists **全エレ機種** | 空 + `scope_note`（本文で MRL/MR が分かれば追記） |

Lists `Model=VFGLF` だけでは MRL/MR は決まらない — **Lists 機種ラベル** または **品目** で埋める。

---

## 1. エレベーター：機種略称 ↔ 制御方式（提供画像 catalog）

**draft `record_id`:** `elv-model-abbreviations-user-image`  
**ファイル:** [ELV_機種略称・制御方式一覧_提供画像.md](../drafts/ELV_機種略称・制御方式一覧_提供画像.md)

| 商品名 | 区分（概要） | 機械室 | 機種略称（例） | 制御方式欄の表示 |
| --- | --- | --- | --- | --- |
| AXIEZ | MRL | MRL | KE-PF, KE-RF, KE-RFS, KE-BF, KE-WF/HF | VFGLB, VFGLB-JB（結合セル要再確認） |
| Nexcube | 低速大容量 | CMR | KM-LD | VFGLB-WB |
| Nexcube | 省スペース低速 | CMR | **CM-LB** | **VFGLB-K** |
| Nexcube | 省スペース高速 | CMR | **CM-MA** | **VFGH** |
| Nexcube | 超高速 | MR | ME-CH | VFGH |
| Nexcube | 高速 | MR | ME-CM | VFGH |
| Nexcube | 低速 | （画像判読不可） | ME-BL | VFEL |
| MELCITY / MELWIDE | 小形 MRL | MRL | AC-PB, AC-CB | VFGR |
| 荷物用 MRL | 荷物 MRL | MRL | KF-ETC, KF-MTC | VFGLB |
| 中小形荷物 | MR | MR | FE-TA, FM-TA | VFEL |
| 駅舎用 | MRL | MRL | KE-SA, KE-SAT, KM-SA, KM-SAT | VFGL |

表の **CMR** 列は提供画像の原文。**テーマカードの `machine_room` は MRL / MR のみ** — CMR 行の機種（CM-MA, CM-LB, KM-LD）は **`MR`** と書く。

**Lists での注意:** 欄に **VFGLF** とある事例の多くは **AXIEZ-LINKs / NEXIEZ 系制御**（提供画像表の外。Lists・Vault が制御名として VFGLF を使う）。**VFGLB と VFGLF は制御方式が異なる**（例: 煙感知器点検口 SW — draft ID385）。カードでは `control_methods: [VFGLF]` と `product_lines: [AXIEZ-LINKs]` を併記し、機種略称が分かれば `model_abbreviations` も足す。

**AXIEZ-LINKs:** 機種略称一覧の行には無いが、draft 前缀 `ELV_AXIEZ-LINKS_*`・Lists の「LINKs」表記・`model_type: AXIEZ-LINKs` が棚規則。制御方式ラベルは Lists/Vault 上 **VFGLF** であることが多い。

---

## 2. Vault カテゴリ（draft `category` / `source_path`）— エレ

| category（件数目安） | 役割 | カード化の置き場 |
| --- | --- | --- |
| 不具合対応(ELV) / 不具合対応【ELV】 | 事例・トラブルシュート | `case-summaries/`。制御別エラー表は **参照のみ**（表本体は AWS レーン） |
| 技術メモ【ELV】１ | 基礎・一般 | 横断 `practice-guides/` または制御軸 |
| 技術メモ【ELV】２ | 一般・FAQ・**エレ機種一覧** | catalog 系。`elv-model-abbreviations-user-image` |
| 技術メモ【ELV】３ | モード・群管理・**機種別**（CM-LB, KM-LD …） | draft 前缀 **`ELV3_`** ≒ この Vault ツリー |
| 総点（VFGH）/ 総点（VFGLB・VFGLF） | 引渡し総点 | 制御方式別。カードは総点手順の要約に留める |
| NEXWAY(VFGH) / NEXIEZ(VFGLF) | QC メモ | **NEXWAY は NEXCUBE の海外呼称**（2026-10-20）。日本向けカードは `product_lines: Nexcube`。フォルダ名の VFGH は制御。CM-MA だけに狭めない |
| 工技業務（現場系）１/２、現場担当業務 | 工技業務（`knowledge_domain: engineering_business`） | エレ技術と混ぜない。必要なら `product: 昇降機` 等 |

**制御エラー参照（Vault 路径の慣例）**

| 制御方式 | draft 例 | OneNote 索引例 |
| --- | --- | --- |
| VFGH | [ELV_VFGH制御エラー.md](../drafts/ELV_VFGH制御エラー.md) | `…:123` |
| VFGLF | ELV_VFGLF制御エラー.md | （同系列） |
| VFGLB | ELV_VFGLB制御エラー.md | （同系列） |

個別エラーコードは **事例カードに文脈付き**で載せ、総合エラー表は写さない（[IMPORT-SCOPE.md](../drafts/IMPORT-SCOPE.md)）。

---

## 3. draft ファイル名前缀（630 件棚の見分け）

| 前缀 / パターン | 含意 |
| --- | --- |
| `ELV_` | エレ一般。続くトークンに **VFGLF / AXIEZ-LINKS / CM-MA / KM-LD** 等 |
| `ELV2_` | Vault **`技術メモ【ELV】２/`** 配下の索引・FAQ 親ページ等 |
| `ELV3_` | Vault **`技術メモ【ELV】３/`**（群管理・モード・CM-LB 専用页） |
| `VFGH_` / `VFGLB総点` | 制御方式または総点系列 |
| `ESC_` / `u形` / `ZJ2` / `エスカ機種一覧` | **エスカレーター**（`product: エスカレーター`） |
| `工技現場系` / `現場_` / `研修` | 工技業務・現場運用 |
| `NEXWAY` / `NEXIEZ` | QC。**NEXWAY → Nexcube**（海外呼称）。NEXIEZ は VFGLF 側の QC 呼称としてフォルダに残る |

---

## 4. エスカレーター：機種 catalog

**draft `record_id`:** `catalog-escalator-u-models`  
**ファイル:** [u形エスカレーター_機種一覧.md](../drafts/u形エスカレーター_機種一覧.md)  
**Vault category:** `エスカ機種一覧` / `エスカ（u形）` / `総点(u型エス)` 等

u 形: 機種略称 S1UJ1(S1000), S6UJ1(S600) 等 — 詳細は structured_data。エスカカードは **`product_line: escalator`** と **`model_abbreviations`** を必須とし、エレの VFGH/VFGLB 軸に載せない。

---

## 5. テーマカードへの適用ルール（Must）

1. **§1 使う場面** の先頭で **制御方式** と **機種略称** を明示（Lists Model 欄は脚注）。
2. `model_scope` に最低限: `lists_model_label`, `control_methods`, `model_abbreviations`, `product_lines`, `machine_room`, **`guide_systems`**, **`door_families`**, **`door_types`**（分かる場合）。従来の `observed_on` / `may_apply_to` / `excludes` は維持。
3. **INDEX** は [cards/INDEX.md](../cards/INDEX.md) で **guide_systems / door_families / door_types / 制御 / 機種略称** を混同しない（エスカ・工技は別節）。

### ドア軸の階層（現場の分け方）

```text
door_families     L型  |  K型          ← Lists/OneNote が明示した大分類
       ↓
door_types        LV5K / LV6K / LV0K …  ← 「ドアタイプ」として品目表・Lists に出る型名
                  KV4K-3, KV4, K4N-2 … ← 戸閉装置型名も door_types（略称は原表記と併記可）
                  CO/2S/SS, 気配りドア付 …
```

| 層 | 例（ソース上） | 載せ方 |
| --- | --- | --- |
| **L型 / K型** | list 242「L型ドア」、72「K型ドア」、OneNote「L型：2.5mm以内、K型：1.0mm以内」 | `door_families: ["L型"]` または `["K型"]` |
| **LV 系列** | `ドアタイプが LV5K-2S`（433）、`LV5K/LV6Kドア`（432/435）、`LV0K-7-2S`（439 Notes）、`LINKs（LV5Kドア）` | `door_types` に **LV5K-2S**、**LV5K-CO/2S** 等（分解は原文どおり） |
| **KV 系列** | Vault「KV4K-3（略称 KV4）」、乗場 K4N-2 | `door_types: ["KV4K-3"]` 等。**kV/KV 表記ゆれ**は原文の正式名称を優先 |
| **付加** | 気配り・HMS/MBS | `door_types` に `気配りドア付` + `may_apply_to` |
| **未記載** | Lists に L/K も LV も無い | `door_families: []`, `door_types: []` — **未確認**に「品目表で L/K とドア型名を確認」 |

OneNote の LV5K CLT 注意（**L型ドア**で駆動装置が桁上、など）と list 432 を開くときは **family + types の両方**を見る（draft [ELV_OLT_CLT位置調整_参照記録.md](../drafts/ELV_OLT_CLT位置調整_参照記録.md)）。

4. 横断（「全エレ機種」）は `control_methods: []` と `scope_note: 全エレ機種` で Lists 原文を保持。
5. 提供画像 catalog と矛盾する Lists 表記は **未確認事項** に書く（断定しない）。

---

## 6. 関連 registry

| 用途 | ファイル |
| --- | --- |
| Lists ↔ draft 照合 | [list-item-to-record.jsonl](./list-item-to-record.jsonl) |
| Lists タイトル ↔ OneNote | [lists-onenote-title-hits.jsonl](./lists-onenote-title-hits.jsonl) |
| 統合ロードマップ | [validation/RECONCILE-ROADMAP.md](../validation/RECONCILE-ROADMAP.md) |

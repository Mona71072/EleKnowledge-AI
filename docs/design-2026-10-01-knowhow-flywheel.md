---
status: draft
last-verified: 2026-10-01
related-code:
  - lambda/rag/rag-function/app.py
  - lambda/rag/rag-function/kb_profile.py
  - infrastructure/sam/phase2-template.yaml
  - frontend/src/app/chat/page.tsx
  - lambda/chat/chat-management/app.py
  - scripts/eval/run_retrieve_eval.py
---

# 設計: Know-how Knowledge Layer（Knowledge Flywheel）

> **状態:** 共同確認用ドラフト。**未確定。実装しない。**
>
> **調査:** [survey-2026-10-01-knowhow-flywheel.md](./survey-2026-10-01-knowhow-flywheel.md)
>
> **位置づけ:** 既存 EleKnowledge を前提に、現場経験知を「社員の追加業務にせず」蓄積するための最小構成案。新システムの建国ではない。

## 0. この PR で決めてほしいこと（先に読む）

Approve は次の Yes/No で足りる。詳細は本文。

1. Know-how を EleKnowledge の検索対象に加える方向でよいか（業務スコープ変更。機種追加と同種の共同確認）
2. 共有 KB `VQV81CNYU4` には入れず、**専用 S3 + 専用 KB** で分離してよいか（法令 RAG と同じ型。据付チャットボットへの影響ゼロ）
3. Canonical は Markdown、編集は人が確認した差分だけ、AI の直接上書きは禁止、でよいか
4. 最初の実装は Flywheel 全体ではなく、後述の **MVP** でよいか
5. Markdown スキーマ v1（§5）を初期案としてよいか（実データ投入後に削ってよい）

決まらないこと: Curator Agent の新設、アプリ内レビュー画面、OneNote 一括変換、キーマン Skill DB、Obsidian のシステム組み込み、共有 KB の改変。

---

## 1. 目的と原則

EleKnowledge はすでに正式資料を RAG で届けている。今後それとは別に、

**現場経験・トラブル対応・調整ノウハウ・判断ポイント・暗黙知を、通常業務の副産物として捕捉し、人が確認した分だけ再利用する層**

を足したい。

目的は OneNote を Obsidian に置き換えることではない。目的は次の一文である。

> 日常業務の中で発生した経験をシステムが捕捉し、AI が下書きし、人間は確認し、使われるほど Knowledge が成熟する。

最重要原則:

1. **Knowledge Management を社員の追加業務にしない。** 「ノウハウを書いてください」に依存しない
2. **Capture automatically, verify by humans.** AI が候補を作り、人は承認・修正・却下する
3. **イベントをそのまま KB に載せない。** 一般化した Canonical Markdown だけを公開する
4. **Official Knowledge は AI が改変しない。** Know-how は「正解へ到達する経験知」であり、守るべき正解そのものではない
5. **既存実装を流用し、過剰設計しない。** マイクロサービス・新 Agent・新 DB は必要が証明されるまで作らない

`PRODUCT_INTENT.md` の「答えを代行せず、根拠を揃え判断を支える」「最初からマルチエージェントにしない」は維持する。Know-how は新しい答えエンジンではなく、**届ける資料の種類を 1 つ増やす**話である。

---

## 2. レイヤー

| 層 | 意味 | 置き場所 |
|---|---|---|
| Official Knowledge | 規程・要領・基準・法令・メーカー仕様。守るべき正解 | 既存共有 KB `VQV81CNYU4`（変更しない） |
| Know-how Knowledge | 現場で再利用できる経験知。到達の仕方 | **新設する専用 KB**（本設計） |
| 未検証情報 | 下書き・候補・未確認事項 | Git の PR / draft。KB には載せない |

回答時は可能な限り 3 つをラベルで区別する。

```text
[正式資料]  ○○施工要領書では…
[現場ノウハウ]  過去の確認事例では…
[未確認]  ○○については十分な根拠なし
```

安全・品質・法令・設計仕様について、Know-how を正式仕様と誤認させてはならない。プロンプトだけでなく、**retrieve 結果に `source_type` を付け、画面にも出す**。プロンプトだけの区別は足りない。

---

## 3. ライフサイクル

```text
Knowledge Event（ChatLogs / アーカイブ。既存）
      ↓ 週次バッチがクラスタ化（新規スクリプト。Agent ではない）
Knowledge Candidate（Git の PR。draft Markdown）
      ↓ 人が確認・修正・却下
Canonical Markdown（マージ後）
      ↓ 検証 → サイドカー生成 → 専用 S3 → ingestion
Published Knowledge（専用 KB の published のみ）
      ↓ EleKnowledge が 2 本目の retrieve（既定 OFF から）
利用ログ（既存 ChatLogs。sourceType を足す）
      ↓
改善 PR（再び Candidate）
```

状態は Markdown 上では 3 つに絞る。

| `status` | 意味 | KB |
|---|---|---|
| `draft` | PR 上の候補 | 載せない |
| `published` | 確認済み | 載せる |
| `deprecated` | 廃止 | 索引から除く（S3 から削除して再 Sync） |

レビュー中は GitHub PR が状態を持つ。アプリ内ステートマシンは MVP では作らない。お知らせ機能の draft/scheduled/published は流用しない（ドメインが違う）。

`status` と `maturity` は分ける。

| `maturity` | 意味 |
|---|---|
| `observed` | 経験則。公開してよいが断定しない |
| `validated` | キーマンまたは所管が確認した |
| `established` | 繰り返し使われ、矛盾が出ていない |

`published` かつ `observed` を許容する（公開されているがまだ経験則）。

---

## 4. 複数ループのうち、最初にやるもの

| Loop | 内容 | MVP |
|---|---|---|
| A. 通常検索 | `not_found`・👎・類似質問の繰り返しから Gap を拾う | **やる**（Athena + 人手。自動起票は後） |
| B. 業務調査 | 調査そのものから下書き | 入口が無い。後回し |
| C. 現場トラブル | 診断セッションから troubleshooting 候補 | Phase 3 は admin 限定。後回し |
| D. キーマン確認 | AI 下書きを 30 秒〜数分で承認 | **やる**（PR または curator 代理記録） |
| E. 正式資料更新 | Official との矛盾検出 | 共有 KB の更新イベントが取れない。後回し |

[design-2026-07-29-improvement-proposals.md](./design-2026-07-29-improvement-proposals.md) の v0 は LLM 自動起票をしない。Loop A の「AI が Candidate を書く」は、この決定を見直す話でもある。MVP では **人が failures から題材を選び、AI がその題材の下書きだけを書く** に留め、自動量産しない。

---

## 5. Markdown スキーマ v1（推奨）

現行 RAG を踏まえた変更点:

- Bedrock は YAML frontmatter をメタデータとして読まない（**要公式確認**）。公開時に `.metadata.json` へ写し、本文から frontmatter を除く
- `aliases` / `search_terms` はメタに置いても HYBRID の本文検索には乗らない（**要公式確認**）。本文の「現場での言い方」節へ移す
- 機種は既存の `model_type`（`*` = 全機種共通）に合わせる。`models` という別名は使わない
- 動的指標（閲覧数・Helpful 率・score）は Markdown に書かない。ChatLogs / Athena 側
- 項目は会議室で増やさない。実データ投入後に削る

```markdown
---
knowledge_id: KH-000123
title: 戸開不能時の○○コネクタ確認
knowledge_type: troubleshooting
status: published
maturity: observed
model_type: [ATEA, ATDN]
processes: [adjustment]
components: [door]
risk_level: quality
official_refs: [C-xxxx.pdf]
related: [KH-000095]
supersedes: []
last_validated_at: 2026-10-01
review_interval_days: 180
---

# 戸開不能時の○○コネクタ確認

## 要点

## 現場での言い方

戸が開かない / ドア開かない / DO動かない

## 適用条件

## 結論・対応

## 判断ポイント

## 原因・理由

## 注意・適用外

正式資料を優先すべきケースを必ず書く。

## 根拠

### 正式資料

### 現場知見

個人情報・工事番号・現場固有名は書かない。

## 未確認事項

AI が推測で埋めない。
```

`knowledge_type` は `troubleshooting` / `howto` / `judgment` / `inspection` / `case` / `faq` から始める。本文構造は共通化し、必要な節だけ書く。

### メタデータの振り分け

| 残す | 名前を変える | 本文へ | 削除 | システム側 |
|---|---|---|---|---|
| `knowledge_id` `title` `knowledge_type` `status` `maturity` `official_refs` `related` `supersedes` `last_validated_at` | `models` → `model_type`。`risk_domains` → `risk_level`（1 値） | `aliases` `search_terms` | `schema_version` `product_family` `domain` `access_scope` `owner_domain` `steward_role` `created_at` | 閲覧数・再利用・score・承認者（PR）。公開時にサイドカーへ `source_type: knowhow` を自動付与 |

サイドカーへ自動で足すもの（人が Markdown に書かない）:

- `source_type: knowhow`
- `knowledge_id` / `status` / `maturity` / `model_type` / `risk_level`
- `source_commit`（公開した Git SHA。Git と KB のずれ検出用）

`review_interval_days` は `risk_level` が `safety` / `legal` のとき必須。一般 Know-how は Demand-driven、安全・法令・重大品質は定期レビュー必須、という別ルールをメタで表現する。

### Chunking

本番共有 KB の chunking はリポジトリに記録が無い。Know-how 専用 KB なら作り直せる。

初期案: 記事が 1〜2 画面なら **1 ファイル 1 チャンク（分割なし）** を既定候補にする。見出し単位分割は、評価で「節をまたぐと誤る」ことが出てから Custom Transformation で足す。固定 300 token は法令設計の条文分割向けであり、短い Know-how には過剰な可能性がある。

採用は推測で決めず、同じ 10〜20 本を「分割なし」と「固定サイズ」の 2 KB（または 2 データソース）で `run_retrieve_eval.py` 比較する。

---

## 6. 推奨アーキテクチャ（既存資産の再利用）

```text
[Event]     ChatLogs → S3 アーカイブ → Athena          既存
[Gap]       SQL 抽出 → 週次クラスタ（スクリプト）         新規・バッチ
[Candidate] 下書き Markdown の PR                       Git（新リポ推奨）
[Review]    人が Approve / 修正 / Close                 GitHub。記録は PR
[Publish]   検証 → sidecar → 専用 S3 → ingestion        新規スクリプト。最初は手動
[Retrieve]  共有 KB + Know-how KB を並べて検索           app.py 拡張。既定 OFF
[Answer]    source_type ラベル。安全系は正式資料優先      プロンプト + UI
[Usage]     sourceDocuments に sourceType               既存アーカイブに乗る
```

### 6.1 専用 KB（他アプリ影響ゼロ）

法令 RAG 設計（PR #155）と同じ分離:

- 専用 S3 プレフィックス（例: `knowhow/published/`）
- 専用 Managed Knowledge Base（EleKnowledge の IaC で作る）
- 既存 `category` / `model_type` 契約を共有 KB 側では変えない
- Phase 2 Lambda は新 KB ID を環境変数で受け取る。空なら現行どおり 1 本だけ retrieve

共有 KB への書き込み・Sync・メタ追加はしない。D4 を破らない。

### 6.2 2 本目の retrieve

`retrieve_for_normal_query` が、`KNOWHOW_KNOWLEDGE_BASE_ID` が空でなければ Know-how KB も retrieve し、結果に `source_type` を付けてマージする。Rerank / 検索語書き換えと同じく **既定 OFF**（[decisions-2026-09-24-rag-two-modes.md](./decisions-2026-09-24-rag-two-modes.md) D3）。

マージ規則（暫定。評価で見直す）:

- Know-how は件数上限を小さくする（例: 選別後 2 件）
- `risk_level` が `safety` / `legal` の質問、または既存の安全ゲートに触れる質問では、Know-how を根拠にしない（表示は「参考」に落とすか出さない）
- 画面とプロンプトの両方で `[正式資料]` / `[現場ノウハウ]` を出す
- 現行の `.md` 除外は「拡張子」ではなく `source_type` で判定する。さもないと Know-how が引用されない

### 6.3 Git と Obsidian

- **Canonical の版管理は Git。** 差分・承認・revert・S3 との SHA 照合ができる
- 置き場所は **アプリリポジトリとは分ける** ことを推奨する。レビューする人と公開フローが違う。本リポに `knowledge/` を置くとデプロイ PR と混ざる
- **Obsidian は編集ツールに留める。** wikilink・プラグイン依存は CI で禁止する。ベンダー非依存の Markdown が資産
- AI は Canonical を直接上書きしない。`Current → AI Proposal → Diff → Human Review → Merge`

キーマンが GitHub を使わない場合、curator（mona 側の知識係）が PR に代理記録するか、後で簡易確認画面を足す。MVP でアプリ内ワークフローは作らない。

### 6.4 Knowledge Curator Agent

今は新設しない。週次スクリプト（Athena → LLM でクラスタ → Markdown レポート）で足りる。件数が増え、ルーティングや矛盾検出が手に余ってから、既存 Lambda のバッチとして足す。Bedrock Agent を新しく置く必要は、この段階ではない。

`PRODUCT_INTENT.md` の「最初からマルチエージェントにしない」にも合う。

---

## 7. MVP（最初に出す価値）

実装コードはこの PR に含めない。合意後のデプロイ PR で、だいたい次の順になる。

1. スキーマ検証スクリプトとサイドカー変換（frontmatter を本文に残さない）
2. `/admin/failures` で多いテーマから、手作業で 10〜20 本を Markdown 化する（OneNote 一括ではない）
3. 専用 KB を dev に作り、手動公開スクリプトで入れる
4. `app.py` に 2 本目 retrieve（既定 OFF）、`sourceType`、`.md` 判定変更、プロンプト 3 区分
5. チャット画面で「現場ノウハウ」を別表示
6. 既存 golden set で回帰（正式資料の到達が落ちないこと）と、Know-how 用の小セットで ON/OFF 比較
7. 週次 Gap レポートは Athena SQL を人が回す（自動起票しない）

これで「検索しているだけで候補の題材が溜まり、確認した分だけ届く」の最小形になる。Flywheel の後半（自動 Candidate 量産、キーマン Skill、矛盾検出）は使われ方を見てから。

---

## 8. 優先度

判断軸: 安全性 → Knowledge 品質 → 実装コスト → 既存影響 → 利用者価値。面白さでは並べない。

### P0

- 本設計の共同確認（本 PR）
- スキーマ v1・検証・サイドカー変換
- 専用 KB（共有 KB 非接触）
- 2 本目 retrieve（既定 OFF）と出典ラベル
- `.md` 除外を `source_type` 判定へ変更
- 評価（回帰 + Know-how 小セット）

### P1

- 検索トレース / 構造化ログ / 資料クリック（既存 PR #111 等を先に載せる）
- 週次 Gap レポートの定型化
- GitHub Actions での公開自動化
- 安全系の `review_interval_days` 切れ検出
- metrics に `sourceType` 別の再利用
- OneNote からの段階 ingest（Normalize → Candidate。一括公開しない）

### P2

- アプリ内レビュー画面と Candidate テーブル
- キーマン Skill / Routing
- Curator Agent
- Loop C / E
- 資料単位 ACL（今は「全社員に出してよいものだけ公開」で逃げる）

---

## 9. コード影響（実在ファイルのみ。合意後のデプロイ PR 用）

存在しないパスは書いていない。

| 対象 | 内容 |
|---|---|
| `lambda/rag/rag-function/app.py` | `KNOWHOW_KNOWLEDGE_BASE_ID`（空なら OFF）。`query_knowledge_base` に KB ID 引数。`retrieve_for_normal_query` でマージと `source_type`。`build_page_candidates` / `extract_citations_from_selected` の `.md` 除外を種別判定へ。`build_claude_messages` と `system_prompt` に 3 区分と正式資料優先。`is_allowed_document_uri` に専用バケット |
| `lambda/rag/rag-function/kb_profile.py` | Know-how KB 用プロファイル |
| `infrastructure/sam/phase2-template.yaml` | `KnowhowKnowledgeBaseId`（既定空）。その ARN だけへ `bedrock:Retrieve` |
| `frontend/src/app/chat/page.tsx` | 型に `sourceType`。頁候補・参考資料で「現場ノウハウ」表示 |
| `frontend/src/lib/documents.ts` | Know-how URI のリンク |
| `scripts/eval/run_retrieve_eval.py` | ON/OFF 比較 |
| 新規（合意後） | `infrastructure/sam/knowhow-kb-template.yaml`、`scripts/knowhow/`（検証・sidecar・公開）、Know-how 用 golden、unit test |
| 正本 docs（実装 PR で） | `docs/api/rag.md` と `docs/data-model.md` は production。実装前に事前確認してから更新。impl-log / decisions も同じ PR |

### DB

MVP では **テーブル追加なし。** Event は ChatLogs、Candidate は Git。アプリ内キューが必要になったら DynamoDB を検討する。

---

## 10. セキュリティ / ガバナンス

| 項目 | MVP のやり方 |
|---|---|
| Permission | 全社員公開前提。出せないものは載せない。資料 ACL は作らない |
| Approval | GitHub PR。キーマンが使えないなら curator が代理記録し、記録者を PR に残す |
| Audit | PR のマージログ + サイドカー `source_commit` |
| Provenance | 本文の「根拠」節 + `official_refs`（既存 KB の `filename` で辿れる値） |
| Sensitive data | 公開 CI で氏名・工事番号などのパターン検査 |
| AI editing | 直接 push 禁止。数値・安全基準・適用機種の追加は人が見る |
| Rollback | Git revert + S3 Versioning + `sync --delete` 後の件数照合 |
| Retrieval poisoning | 件数上限・ラベル・安全系では使わない。既存の「資料内指示に従わない」を維持 |
| 他アプリ | 共有 KB 非接触で影響ゼロ |

---

## 11. テスト

| 層 | 内容 |
|---|---|
| Unit | スキーマ、sidecar（frontmatter が本文に残らない）、マージ、件数上限、OFF 時の現行同等、`.md` 判定 |
| Integration | dev KB への sync・削除反映・失敗文書の検出 |
| Retrieval | 既存 golden の回帰（`hit_in_candidates`）。Know-how セットの ON/OFF |
| RAG eval | 「安全・法令で Know-how を根拠にしない」否定セット |
| Permission | IAM が 2 KB ARN に限定されていること |
| 比較方法 | 同じ質問を OFF/ON で流し、資料到達率と「正式資料が押し出されていないか」を見る。成功定義は作文の上手さではない |

---

## 12. 調査プロンプトへの回答（15 問）

1. **土台として使えるか。** Event・失敗・評価・フィルタ・引用の器は使える。置く場所と種別が無い。
2. **一番大きな不足。** 自前の Know-how KB と、正式 / Know-how の出典区別。
3. **最小変更の最初。** 10〜20 本を専用 KB に入れ、既定 OFF の 2 本目 retrieve とラベルを付けて評価する。
4. **スキーマは足りるか。** 構造は足りる。sidecar 変換と `model_type` への名前合わせと別名の本文化が必須。
5. **メタ過多か。** やや多い。約 20 項目を 13 前後へ削った。
6. **Event の保存先。** 既存 ChatLogs → S3 → Athena。新ストア不要。検索トレースが先。
7. **Candidate の管理。** MVP は Git PR。量と UX が破綻してから DynamoDB。
8. **Obsidian。** 編集ツールまで。アーキテクチャに入れない。
9. **Git を Canonical の版管理に使うか。** 使う。アプリリポとは分ける。
10. **Publish。** マージ → 検証 → sidecar → 専用 S3 → ingestion → 照合。最初は手動スクリプト。
11. **Gap 検出できるか。** `not_found` と 👎 で粗い検出は今できる。トレースと言い換えで精度が上がる。
12. **Curator Agent。** 今は価値が薄い。週次バッチから。
13. **分離と統合検索。** 保存は KB ごと。検索は並べる。表示はラベル。安全・法令は正式資料優先。
14. **他アプリ影響。** 共有 KB を触らなければ回避できる。
15. **現実的な MVP。** §7。

---

## 13. 構想側への指摘（案を絶対視しない）

- **Loop B/C は入口が無い。** 最初から「業務をやるだけで全部捕捉」はできない。今捕捉できるのは EleKnowledge 検索だけである
- **キーマンの GitHub PR は現場と合わない可能性が高い。** 承認の記録方法は本 PR の未決事項
- **Candidate の自動量産は Review を壊す。** 優先度の点数表を先に作らず、「failures で繰り返しているテーマだけ下書きする」
- **Obsidian を中心に据えると、RAG・監査・公開がツールに縛られる。** Markdown が資産、Obsidian はビューア
- **共有 KB へ Know-how を足すのは最短に見えて、据付チャットボットと正式資料の境界を壊す。** 専用 KB の方が実装は増えるが、影響範囲は小さい
- **登録件数 KPI は採らない。** 既存どおり資料到達と 👎 / `not_found` を見る

---

## 14. 未決（PR で止める質問）

1. Know-how を検索対象に加える業務判断（決定者・確認者・対象外データの扱い）を、いつ誰が書くか
2. Canonical Git を別リポジトリにするか、当面本リポの `knowledge/` で始めるか
3. キーマン承認を PR 代理記録でよいか、確認画面が先か
4. improvement-proposals v0 の「LLM 自動起票しない」を、下書き生成だけ例外にするか

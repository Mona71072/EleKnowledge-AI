---
status: draft
last-verified: 2026-10-21
related-code: []
---

# 用語・基礎知識のノウハウ統合: 設計準備と次セッション引継ぎ

本書は設計に必要な論点・資料・実装接点の棚卸し。確定したAPI・スキーマ・リソース構成ではない。製品方針は[初期構想](../../concept-2026-10-21-product-domain-knowledge.md)、共通の技術契約は[ノウハウ設計](https://github.com/yukiworkspace/EleKnowledge-AI/blob/08ba5eaa7b86749f8aafdf752d2badc8240e2a6f/docs/design-2026-10-01-knowhow-flywheel.md)へ集約し、本書を第三の仕様正本にしない。

## 0. 最初に確認すること

次回はルートAGENTS.md、本節、[再開プロンプト](#8-再開プロンプト)から始める。指定worktreeのstatus/logとPR #195/#200の最新head・コメントを確認し、保存時点との差を調べる。ルートと他worktreeの未コミット変更を上書きしない。

2026-10-21に照合した参照点:

| 対象 | 参照点・状態 |
| --- | --- |
| #195 実装 | `08ba5eaa7b86749f8aafdf752d2badc8240e2a6f`、open。リモートのコード・文書を読取確認 |
| #200 方針 | `471b6133661f06f3e5014e43e358e43f6bdad81c`を基準に本棚卸しを追加。Draft |
| itai検証worktree | `.worktrees/senpai-itai-t01-20261021`、`d0f63a6f`、追跡ファイルの未コミット変更なし。本設計作業では変更していない |
| ルート | `c3ae301f`、既存の多数の未コミット変更あり。本設計作業では変更していない |

ユーザー指定は、ノウハウとの共通管理、「用語・基礎知識」の分類、Ele-Knowledge内のadminグループ向けインボックス。monaは共通正本・承認経路と少数単元の試行にYes。**実装を#195へ統合する追加質問は、確認時点で返答待ち**。[依頼コメント](https://github.com/yukiworkspace/EleKnowledge-AI/pull/200#issuecomment-6318600137)と最新返信を次回確認する。待っている間も設計の比較・具体化は進められる。

今回はGitHub上の指定版の静的照合のみ。AWSの現況、会社ネットでの操作、実資料の内容、承認・製品受入、デプロイを検証した記録ではない。

## 1. 既存実装と不足の切り分け

| 領域 | #195で確認できたもの | 統合に向けた不足・注意 |
| --- | --- | --- |
| 編集画面 | `/admin/knowledge`、ローカルMarkdownの読込・編集・差分用パケットと候補のファイル出力 | 作業はメモリ内。共有下書き保存、Git正本への反映、正式承認・公開へ未接続 |
| 根拠照合 | `/admin/knowledge/research`、技術／法令RAG回答と出典の表示、選択回答の編集候補への取込 | AI回答の追跡メモであり原本確認・技術承認ではない。不明用語のキューと永続的な根拠管理は追加検討 |
| 現場報告 | `POST/GET /rag/senpai/field-reports`。dev/admin限定、本人の相談との照合、条件付き保存・本人向け読取 | GETは本人の相談単位。担当者の横断一覧・振り分け・状態変更・採否理由・書出しAPIは未実装 |
| 既存の指摘・要望 | `/admin/failures`、`/chat/suggestions`、管理者の要望一覧、クライアント側の改善提案集計 | 技術候補の承認台帳ではない。共通インボックスの入口に接続するか比較する |
| ノウハウ検索 | 明示許可した版・hashの索引生成、private S3単一索引のGetObject、機種条件付き検索 | `navigation_only`のadmin探索用途。クラウド処理許可と技術承認は別。承認知識の公開経路へ自動転用しない |
| カード種別・配置 | ビルダーの許可対象は`knowledge/cards/case-summaries/`と`practice-guides/` | 新分類は表示変更だけでは索引化できない。パーサー・配置許可・JS/Python契約・評価・引用への伝播を確認 |
| 調査ジョブ | 受付／ワーカー分離、予算・冪等・本人の進捗・根拠検索 | 不明用語の永続台帳ではない。既存ジョブ表の短い保持や相談単位のキーをそのまま候補へ流用しない |
| 版・公開 | 設計には非公開Git正本・特定版承認・別操作の公開／停止がある | 画面のチェックやMarkdownのapproved表記は承認にならない。実装済みの範囲を次回も区別する |

## 2. 設計で決める事項と成果物

| 優先 | 検討事項 | 次回に残す具体的な決定・比較 |
| --- | --- | --- |
| 1 | 最初の完成範囲 | 収集→草案→adminレビュー→正本保存→公開→両AI参照のうち今回どこまで通すか。残りは誰が何を待つか |
| 1 | 共通インボックスの単位 | 現場報告・不明用語・訂正・要望を同じ一覧に載せる共通項目と、種別固有項目。既存データを移動せず参照で集約する案も比較 |
| 1 | 収集の起点と共有許可 | 明示資料読込／RAGでの理解不足／開発中の不足をどう検出するか。記録・共有・検索／生成の実行をどう分けるか。チャット全文の自動コピーを避ける |
| 1 | ID・分類・文脈 | 用語・別名・使用場面・最小文脈・出典・版・未解決点・対象条件。候補IDと知識ID、同じ語の機種別の意味、複数候補の一単元への統合 |
| 1 | 状態と役割 | 候補の未確認／確認待ち／反映済み／保留・不採用と、本文のdraft／approved／retired、公開状態を分離。admin閲覧と編集・技術承認・公開権限の対応 |
| 1 | APIと保存 | admin横断一覧のQuery用キー／GSI・ページング、詳細・編集・状態変更、楽観的競合検出、冪等、再試行・部分失敗、投稿者への状態表示 |
| 1 | 正本と監査 | 共通非公開Gitの具体的な会社承認先・サービス資格情報・許可パス。Web更新とObsidian持込の基準版照合。承認者・内容hash・根拠hash・時刻・理由の耐久記録 |
| 2 | 根拠検索と草案生成 | 技術RAG／ノウハウRAG／原資料の役割。原資料版までの追跡、ヒットなし・矛盾・未読添付・自己引用の扱い。既存承認単元の参照と独立根拠の区別 |
| 2 | 非同期処理と費用 | 手動起動から始めるか、検出後に自動実行するか。検索／モデル回数・入力サイズ・時間・日次枠・同時実行・キャンセル・再試行上限と失敗時の復旧 |
| 2 | 保持期間 | ChatLogsは60日、現場報告の未確認は暫定180日、調査ジョブは別の短期保持。候補の文脈と採用根拠がチャット消失後にも確認可能な最小保存・期限・閲覧範囲 |
| 2 | 配布と両AIの利用 | Git正本→承認版配布→有効な公開一覧→検索／直接読取。S3領域の分離、索引更新・キャッシュ・撤回、開発エージェントの読取と候補登録の認証経路 |
| 2 | 旧仕様と移行 | `record_id/record_version/record_type`と`knowledgeId/cardVersion/kind`等の対応。旧Vault正本案と共通Git正本方針を整理。既存397/398枚等の歴史的件数を現況と扱わない |
| 2 | 検証・試行・停止 | 合成テストと人の技術評価を分ける。試行単元、確認担当、許可範囲、成功条件、失敗時のフラグ停止・前版復帰を決定 |

最初から専用辞書システム、別の承認台帳、新しい自律エージェント群を前提にしない。保存方式も「共通一覧＝全データの同一テーブル化」と決めず、既存機能への影響・権限・保持要件で比較する。

## 3. 対象ドキュメント

まずfrontmatterと必要な節だけを読む。大量のカード・原資料の全文読込は不要。

| 文書 | 次回読む／整合する範囲 |
| --- | --- |
| `AGENTS.md` / `spec.md` | ルールと索引。方針文書#200と実装#195の分離 |
| [初期構想](../../concept-2026-10-21-product-domain-knowledge.md) | 合意済み方向・adminインボックス・未決事項。#200の返信と対応 |
| [知識循環の構想](https://github.com/yukiworkspace/EleKnowledge-AI/blob/08ba5eaa7b86749f8aafdf752d2badc8240e2a6f/docs/concept-2026-10-19-kougi-senpai-knowledge-cycle.md) | §5–6・§10の収集・役割・段階導入 |
| [ノウハウ設計](https://github.com/yukiworkspace/EleKnowledge-AI/blob/08ba5eaa7b86749f8aafdf752d2badc8240e2a6f/docs/design-2026-10-01-knowhow-flywheel.md) | §3分類、§4–5データ／承認、§9利用、§14.6収集箱、§15画面・API・権限・競合 |
| [Markdown基盤](https://github.com/yukiworkspace/EleKnowledge-AI/blob/08ba5eaa7b86749f8aafdf752d2badc8240e2a6f/docs/features/development/knowledge-markdown-foundation.md) | 旧Vault正本・recordモデルと現在方針の差、移行対象を明記。旧案を黙って同一視しない |
| [編集画面](https://github.com/yukiworkspace/EleKnowledge-AI/blob/08ba5eaa7b86749f8aafdf752d2badc8240e2a6f/docs/features/development/knowledge-review-workbench.md) / [照合画面](https://github.com/yukiworkspace/EleKnowledge-AI/blob/08ba5eaa7b86749f8aafdf752d2badc8240e2a6f/docs/features/development/knowledge-research-workspace.md) | メモリ内作業と共有保存の境界、送信内容、確認失効、原本表示 |
| [検索・索引](https://github.com/yukiworkspace/EleKnowledge-AI/blob/08ba5eaa7b86749f8aafdf752d2badc8240e2a6f/docs/features/development/knowledge-markdown-retrieval.md) | 許可フォルダー、取込一覧、navigation_only、専用S3、機種フィルタ、クラウド許可と承認の区別 |
| [現場報告](https://github.com/yukiworkspace/EleKnowledge-AI/blob/08ba5eaa7b86749f8aafdf752d2badc8240e2a6f/docs/features/development/senpai-field-reports.md) | §3 API／データ、§4 TTL、§5集計、§7–8共同確認・未実装 |
| [調査ジョブ契約](https://github.com/yukiworkspace/EleKnowledge-AI/blob/08ba5eaa7b86749f8aafdf752d2badc8240e2a6f/docs/features/development/senpai-research-contract.md) / [実装メモ](https://github.com/yukiworkspace/EleKnowledge-AI/blob/08ba5eaa7b86749f8aafdf752d2badc8240e2a6f/docs/features/development/senpai-research.md) | 再利用できる検索・ジョブ・予算契約。itaiローカル修正とmonaの差は別途照合 |
| `docs/design-2026-07-29-improvement-proposals.md` / `docs/proposals/knowledge-improvement-loop.md` | 既存指摘・要望と収集箱の重複・責任境界 |
| `docs/decisions-2026-10-19-knowledge-evidence-sources.md` | 元資料・機種・利用者の追加／除外判断の前例。新判断の決定記録先を選ぶ |
| `docs/api/rag.md` / `docs/features/production/phase2-rag-chat.md` | 既存APIとの互換性を読取確認。production文書の編集が必要なら理由・影響・対応コードを示して事前合意 |
| `docs/aws-resource-map.md` / `docs/ops-runbook.md` §8 / SAMテンプレート | 管理スタック・既存リソース・配備手順の照合。共有ルートの既存変更は触らない |

実装契約をどの文書へ集約するかを次回決め、同じ仕様本文を本書と複製しない。方針・業務判断は#200等の共同確認、コードに直結するAPI・実装契約更新は#195の対象とする案。

## 4. コード・テストの調査対象

| 領域 | 接点 |
| --- | --- |
| 管理画面 | `frontend/src/app/admin/knowledge/{page.tsx,research/page.tsx}`、`frontend/src/components/knowledge/{KnowledgeWorkbench,KnowledgeResearchWorkspace}.tsx` |
| クライアント契約 | `frontend/src/lib/knowledge-{workbench,research,senpai-field-report}.mjs`、`frontend/src/lib/improvement-proposals.ts`、`frontend/src/hooks/useAdminGate.ts` |
| 利用中の収集 | `KnowledgeSenpaiChat.tsx`、`SenpaiFieldReportForm.tsx`、開発エージェント側の候補登録アダプター（追加要否を設計） |
| 本人の報告保存 | `lambda/rag/senpai-field-report/{app,field_report_input,field_report_store,field_report_vocab}.py` |
| 既存指摘・履歴 | `lambda/chat/chat-management/app.py`、管理者failures／suggestionsのクライアントとAPI |
| 検索・索引 | `lambda/rag/rag-function/knowhow_retrieval.py`、`scripts/knowledge/build-senpai-index.mjs`、`build_scope_review_queue.py`、`build_registry.py` |
| 非同期・RAG | `senpai_research_{api,worker,store,search,rag,budget,config}.py`。回答用ジョブの契約へ副作用を追加するかは比較が必要 |
| IaC | `infrastructure/sam/phase2-template.yaml`。必要時のみphase1の既存Cognito・ChatLogs参照を調査 |
| 回帰対象 | `tests/unit/test_senpai_field_report*.py`、`test_scope_review_queue.py`、`test_knowhow*.py`、`test_senpai_research*.py`、`frontend/tests/knowledge-*.test.mjs` |

新分類では許可ディレクトリ、frontmatter、検索対象属性、JS/Python共通の出典・機種契約、表示、評価索引を一通り確認する。既存の語彙を削除・書換して新分類へ合わせる移行を無断で行わない。

## 5. リソース棚卸しと次回の実査項目

以下は#195のコード／SAM／設計から抽出した論理リソース。デプロイ済み・利用可能であることの確認ではない。バケット名・アカウント・内部URL・資格情報をこの文書へ記載しない。

| リソース | 現状と設計時の確認 |
| --- | --- |
| Cognito User Pool・adminグループ | 既存を利用する方針。JWT検証とAPI側認可、admin閲覧に含まれる候補範囲、業務承認役の割当 |
| Next.js / Amplify | 既存管理画面に収集箱を接続する候補。画面フラグとAPIフラグ、ページ／タブ構成、一般利用者への公開範囲 |
| API Gateway `RagApi` / `ChatApi` | 既存認証・ルートとの整合。投稿経路と担当者向け横断読取・更新APIの分離、入力検証 |
| `SenpaiFieldReportFunction` / `SenpaiFieldReportsTable` | 現場報告用。相談単位・本人向け読取・暫定TTLを維持するか。候補共通化時のキー／GSI／IAM差分 |
| `SenpaiResearchApiFunction` / `SenpaiResearchWorkerFunction` / `SenpaiResearchJobsTable` | 検索・生成ジョブの再利用候補。予算・短期保持・所有者分離・リース。候補台帳への流用とは分ける |
| ChatLogs / chat-management | 既存60日TTL。会話の所有者と最小文脈取得を確認。候補一覧への全会話公開はしない |
| 候補・下書き・承認／監査の保存 | 共有保存と横断Queryが不足。既存テーブル拡張／共通台帳／参照集約の差を比較し、必要な追加だけ選ぶ |
| 会社承認の非公開Git | 共通Markdownの編集正本。対象リポジトリ・パス・サービス認証は未確定。既存アプリリポジトリを当然の保存先にしない |
| private S3ノウハウ索引 | 固定bucket/keyのGetObject用途。現在のnavigation_only索引と、承認版の配布・検索を区別 |
| 承認版の保存・配布先 | S3候補。新規／既存領域、暗号化、版管理、IAM、公開一覧、キャッシュと撤回を設計。編集正本は増やさない |
| 技術KB・法令KB・元のS3データソース | 許可済み資料から根拠を探す読取経路。元資料版の解決と原本閲覧。既存資料の複製・削除・同期を前提にしない |
| ノウハウ用KB等 | 既存のS3索引による直接検索とBedrock KBは別方式。実在する接続先と必要な検索方式を確認し、新設を既定にしない |
| Lambda実行ロール・Git連携資格情報・監査ログ | 検索／モデル／GetObject／候補書込／正本反映／公開の権限を分離。必要ならSecrets Manager。本文・引用全文・トークンをログへ出さない |
| キュー／イベント・監視 | 非同期化が必要なら既存Invoke方式と待ち行列方式を比較。未処理件数・失敗・期限・費用を監視する手段を検討。サービス追加は未決 |

AWS実査が必要になった場合は、まずローカルの環境対応と対象を確認し、必要なリソースの設定・スキーマ・権限だけを読取照合する。大きいJSONや本文を一括出力せず対象項目だけ抽出する。

## 6. 次回の設計順と完了条件

1. #200の統合先への返答、#195の更新・担当重複を確認する。
2. 現場報告・不明用語・訂正を各1件の合成例で並べ、共通インボックスの状態・閲覧・保持の違いを決める。
3. 「候補→草案→レビュー→正本→承認版公開→両AI参照」の一往復を描き、今回の完成範囲を決める。
4. データモデル・状態遷移・役割表・API案・保存先の比較を作り、採用理由と未決事項を記録する。
5. #195の既存コードへの差分、追加リソース、移行、失敗時の復旧、テスト・製品受入条件を整理する。
6. 試行単元・技術確認担当・mona/itaiの分担・実装着手条件を明確にする。

設計完了の成果物は、初回範囲、状態遷移図、データ契約、API／権限表、リソース差分、段階導入と検証計画、判断待ちの担当・理由。詳細は技術契約の正本へ反映し、方針合意と実行許可を混同しない。

特に必要な否定テストは、非adminの直API、他人のチャット取得、秘匿文脈の漏出、改変された承認状態、版競合、重複投函・生成、古いAI結果、根拠の循環、改訂違い、未承認草案の回答混入、公開停止後の旧版利用、保存／公開途中失敗。

## 7. 今回の対象外と既存itai検証の保全

今回は設計準備のみ。アプリコード・AWS設定・元資料・カード本文を変更せず、新規モデル生成・RAG Retrieve・有料試験・KB同期は行わない。#195への実装統合、マージ、デプロイ、共有dev変更、受入前itai切替／push、削除は行わない。

既存itai検証は別の入口`senpai-itai-handoff.md`§0と私有`t24-revision-confirmation.json`で継続する。本書はそれを置き換えない。消化済み有料枠は再実行・流用しない。T17の回答種別4/4を技術的正解率と呼ばず、SR-019の最終ガードは保存実応答再生のみ、技術者受入は未実施として引き継ぐ。Q-3730改訂Bはユーザー確認済みの現行正、新版登録・同期は別タスク。

BKは試行候補であり、ユーザー説明と原本確認済みの事実を区別する。私有の本文・PDF・保存応答を追跡fixtureやこの資料へ移さない。

## 8. 再開プロンプト

```text
EleKnowledge-AIの「用語・基礎知識をノウハウへ統合する設計」を再開してください。
今回は設計を進め、実装・デプロイ・有料実測は行いません。

最初にリポジトリルートAGENTS.mdと
docs/features/development/product-domain-knowledge-integration-handoff.md §0を読んでください。
この文書はPR #200のブランチにあり、itai検証worktreeに存在するとは限りません。
ローカルの古い版を前提にせず、#200の最新headから必要な文書を読んでください。

git status/log、#195/#200の最新head・コメントを確認し、monaの実装統合への返答と重複作業を確認してください。
ルート・他worktreeの既存未コミット変更を上書きしないでください。
実装統合への返答待ちでも、選択肢比較と設計は進めてください。

方針は、ノウハウとの共通管理、「用語・基礎知識」の分類、共通の非公開Git Markdown正本、
Ele-Knowledge内のadmin向けインボックス、人の修正・技術承認、別操作での承認版公開、
RAGと開発エージェントからの共通参照です。
admin閲覧と編集・技術承認・公開の業務権限は分けて設計してください。

引継ぎ資料§1〜6を必要な範囲で読み、既存の現場報告保存・メモリ内編集画面・navigation_only索引を
完成済みの共有インボックス・正本保存・承認済み知識基盤と扱わないでください。
共通候補モデル、状態遷移、API・権限表、保存方式、リソース差分、最初の完成範囲、
mona/itaiの担当と未決事項、検証・受入条件を具体化してください。
共通仕様は既存ノウハウ設計へ集約し、旧Vault正本案やrecord/cardスキーマとの差を整理してください。

#200は方針の共同確認、実装は#195へ統合する承諾待ちです。
AWS変更・元資料登録・KB同期・共有dev変更・受入前itai切替/push・削除・無断マージは禁止です。
消化済み有料枠を再実行／流用せず、私有本文を追跡fixtureへ移さないでください。
大きいJSON・カード群・原資料全文は読まず、必要な対象と項目だけ確認してください。
```

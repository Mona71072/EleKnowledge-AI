---
status: development
last-verified: 2026-11-16
related-code:
  - lambda/knowledge/common-knowledge/app.py
  - lambda/knowledge/common-knowledge/service.py
  - lambda/knowledge/common-knowledge/storage.py
  - frontend/src/components/knowledge/common-knowledge-inbox.tsx
  - frontend/src/app/chat/page.tsx
  - frontend/src/components/knowledge/SenpaiFieldReportForm.tsx
  - frontend/src/components/knowledge/KnowledgeCommentResearch.tsx
  - lambda/rag/knowhow-rewrite/
  - frontend/src/lib/knowhow-rewrite-client.mjs
  - frontend/src/lib/knowhow-rewrite-request.mjs
  - frontend/src/components/knowledge/useKnowhowRewrite.ts
  - frontend/src/components/knowledge/KnowhowCardCheck.tsx
  - frontend/src/components/knowledge/KnowhowRewritePanel.tsx
  - infrastructure/sam/common-knowledge-itai-template.yaml
  - infrastructure/sam/phase2-template.yaml
---

# ノウハウ改善ループ 開発仕様

> **mona ブランチでの試作仕様。共同確認・本番反映の決定ではない。** 実装状況と未確認範囲は §10 に記録し、合成データによる段階的な実装・確認を前提とする。
>
> 最終検証: 2026-11-16 — CommonKnowledge、knowhow-rewrite、SAM、関連する #207 設計と業務設計メモの記載を読み合わせ。AWS 環境での有効化・配備・実資料での受入は確認していない。

## 1. 目的と完了像

チャットで利用者が明示して送った材料を、既存 CommonKnowledge の候補受付・版管理へ集める。管理者は受信箱で候補を読み、必要な場合に限って1クリックでAI案を作り、Yes / No または自然言語の指示を返す。AIは同じ根拠に基づいて案を作り直す。採用した案は作業版となり、既存の技術確認・承認・公開を人が行う。公開版が既存の索引へ反映され、以降のチャットで参照される。

候補の材料は、本人が確認して送った次の3種類に限る。

1. 通常チャットの `not_found` に対して、利用者が「候補として送る」を選んだ質問・要約。
2. 先輩チャットの「当てはまらなかった」等の現場報告。本人が画面で確認・編集して送信済みのもの。
3. 利用者が「残す」を選んだ回答。

チャット全文を候補へ自動保存・複製しない。送信前に利用者が文面を確認・編集でき、個人情報・顧客名を入力しない注意を表示する。利用者の送信は候補台帳への登録であり、AI案作成は管理者の1クリック、技術承認・公開はそれぞれ人の別操作とする。

## 2. 既存実装と接続方針

既存の CommonKnowledge に候補台帳を一本化する。第2の候補テーブルは原則作らない。現行ルート・状態・関数の根拠は以下のとおり（行番号は2026-11-16に読んだこのブランチのソース）。

| 接続点 | 現行契約・実装 | 参照 |
|---|---|---|
| 候補受付・一覧・詳細・状態変更 | `POST/GET /knowledge/contributions`、`GET/PATCH /knowledge/contributions/{id}`。`Service.contribute`、`list_candidates`、`detail`、`transition` | `lambda/knowledge/common-knowledge/app.py:28-48,91-122`; `lambda/knowledge/common-knowledge/service.py:170-279` |
| 候補状態 | `unconfirmed`、`in_review`、`awaiting_review`、`reflected`、`held`、`rejected`。状態遷移は `TRANSITIONS` に限定 | `lambda/knowledge/common-knowledge/service.py:12-22,262-279` |
| 作業版・確認依頼 | `PUT /knowledge/cards/{id}/draft`、`POST /knowledge/cards/{id}/review-requests`。`save_draft` と `review` は作業版・根拠束を版とhashで固定 | `lambda/knowledge/common-knowledge/app.py:40-44,125-130`; `lambda/knowledge/common-knowledge/service.py:281-301,327-397,405-431` |
| 技術判断・公開 | `POST /knowledge/cards/{id}/decisions`、`/publish`、`/withdraw`。`decide` と `publish` は独立した人の操作 | `lambda/knowledge/common-knowledge/app.py:42-45,127-132`; `lambda/knowledge/common-knowledge/service.py:439-491,616-641` |
| 受信箱UI | `CommonKnowledgeInbox` が一覧、候補詳細、編集引受け、作業版保存、技術確認、承認、公開・停止を表示 | `frontend/src/components/knowledge/common-knowledge-inbox.tsx:103-146,263-290` |
| 書き換え案 | `POST /rag/knowhow/rewrite-proposal`。既存カードの `knowledgeId` / `cardVersion`、対象節、根拠を受け、検証済みの差分案を返す。保存はしない | `docs/features/development/knowhow-rewrite-proposal-contract.md:21-50,52-71,128-136`; `lambda/rag/knowhow-rewrite/app.py:92-120` |

## 3. 候補の受付と決定的な整理

### 3.1 受付データ

既存 `Service.contribute` は `candidateType`（`field_report` / `unknown_term` / `correction` / `request`）、`originRef`、`summary`、`context`、`domain`、`audience`、サーバー発行の `permissionId`、`confirmedHash` を受け、候補を `unconfirmed` として登録する。同じ投稿者・種別・`originRef` の再送を冪等に扱い、内容が異なる再送は拒否する（`lambda/knowledge/common-knowledge/service.py:170-219`）。

3種類のチャット起点を判別できるよう、候補レコードに最小限の `intakeKind`（`not_found` / `field_report` / `saved_answer`）を加える。これは候補の由来を示す分類で、根拠の確かさ・共有範囲・公開可否を示す値ではない。`candidateType`、`originRef`、`confirmedHash` の既存検証・冪等性を保ち、必要なら `intakeKind` を同じ冪等性キーと確認hashへ含める。会話本文・会話IDから全文を復元できる識別子は候補へ転記しない。

既存 `candidateType` は維持し、`not_found` と `saved_answer` は `request`、`field_report` は `field_report` として受け付ける。3つの由来は `intakeKind` で区別し、既存分類の意味を拡張しない。

クライアントは本文の `userId`・権限・共有許可を決めない。認証済みのJWT `sub` を使い、サーバー側の `permissionId` と保護された認可表で投稿可否、分野、読者、期限、派生利用可否を検査する。Cognito の admin グループだけで CommonKnowledge の編集・承認・公開権限を与えない（`lambda/knowledge/common-knowledge/service.py:69-83,196-201`）。

### 3.2 整理と受信箱

- 同一 `knowledgeId`・同一 `cardVersion`・同一 `intakeKind` の候補を受信箱上でグループ表示し、件数を集計する。対象カードがまだ無い候補は、IDや本文が似ているだけで自動統合しない。
- 原候補、投稿者、版、状態、指示、案、判断は削除・上書きでまとめず個別に保持する。グループ化は決定的な一覧用投影であり、内容の類似判定やAIによる重複判断を行わない。
- 現行の受付は同じ `originRef` の二重登録を防ぐが、カード版・候補種別ごとのグループ件数を出さない。集計用の候補属性または一覧投影を最小限追加し、権限で読めない候補の件数・本文も返さない。
- 受信箱は既存の `GET /knowledge/contributions?scope=inbox&state=...` と候補詳細を拡張して使う。現行一覧は最大50件のページングであり、一覧自体は本文を返さない（`lambda/knowledge/common-knowledge/service.py:221-247`）。

## 4. 管理者のAI案・指示・判断

### 4.1 AI案を作る

> 最終検証: 2026-11-18 — S1 の指示付き数値拒否・画面注意書き・関連単体テストと、合成Playwrightでの連続再生成・履歴切替・同じ根拠/版/対象節・人の確認後の下書き反映。意味上の正しさ、Bedrock実出力、AWS実機は未確認

管理者が候補の「AI案を作る」を押したときだけ `POST /rag/knowhow/rewrite-proposal` を呼ぶ。受付時の自動生成は行わない。既存 API のカードID・版・対象節・`technical` / `law` の確認済み根拠・出力検証を再利用する。

従来の要求契約には自然言語指示も前回案もなかった。S1 で `instruction`（最大1,000字）と `previousProposal`（直前案の節ごとの内容と版識別子）を追加する。初回は `previousProposal` なしで呼び、作り直しでは直前案・新しい指示・同じ根拠・同じ対象カード版を渡す。根拠を更新した場合は同じ案の続きとして扱わず、新しい根拠束の案として記録する。

指示は「AIへの編集指示」として扱い、事実を支える根拠には数えない。プロンプトで、根拠にない内容を指示が求めた節は変更せず、不足理由を返すよう求める。数値裏付け検査は意味上の事実を機械判定できないため、指示付き要求で裏付けのない裸の数値を含む節は `rejected` にする（初回案は従来どおり警告）。それでも「安全装置の試験は不要」のような数値を含まない誤った主張は検出できない。指示付き案には「指示で求めた内容は根拠で確認できていません。差分と根拠を確認してから採用してください」と常時表示し、管理者の差分確認を最後の砦とする。情報不足・食い違い・検証拒否が出た場合は理由を管理者へ返す。管理者は既存コメント再照会（技術KB・法令KB）で根拠を追加確認してから、同じ候補で再実行できる。

候補本文だけで公式根拠の確認済み状態を作らない。候補の発言は出所を明示した現場申告として保ち、書き換えに使う根拠は管理者が確認したKB回答など既存 rewrite 契約に載る情報から構成する。根拠を確認できない事実は追加せず「根拠が足りない」とする。既存 rewrite の数値検査は文字列の裏付けを確認するもので、意味の正しさは保証しないため、管理者の差分確認を残す（`knowhow-rewrite-proposal-contract.md:138-145`）。

### 4.2 指示・案・判断の履歴

候補ごとに次を時系列で記録する。記録主体はリクエスト本文ではなくJWT由来の `sub`、時刻はサーバー時刻を使う。

- AI案の作成要求に使ったカードID・版・本文hash、根拠束の識別hash、案の版/hashと検証状態。
- 管理者の指示本文（空の初回案も記録）、作成者、時刻、直前案への参照。
- Yes / No / 根拠追加待ちの判断、任意理由、判断者、時刻。

新しい台帳は作らず、CommonKnowledge の候補台帳・操作履歴へ追記する。候補単位の履歴保存には、例えば `POST /knowledge/contributions/{id}/improvements` を追加し、`If-Match` と `Idempotency-Key` を必須にする。操作種別は `proposal` / `instruction` / `decision` とし、候補版、操作者、サーバー時刻、カード版/hash、根拠hash、直前履歴IDをサーバーで結び付ける。候補ごとに指示・案・判断の履歴を残すことは本仕様の要件とする。履歴本文の保存期間・削除方法は共同確認まで未確定のため、その決定前に機能を有効化しない。現行の `mutate` 操作記録は要求hash・主体・役割・理由を記録するが、完了後に要求本文を保持しない。ログへ本文を出さない。このルート・操作種別は提案であり、現行APIには存在しない。

### 4.3 Yes / No と作業版

- **Yes:** AI案を採用候補として選び、元候補と由来を結び付けて既存の `PUT /knowledge/cards/{id}/draft` で作業版を保存する。AI案はカードへ直接反映せず、公開中の版を上書きしない。作業版保存後の「この版の技術確認を依頼」→技術者の `approve` →人の `publish` は既存どおり別操作とする。
- **No:** 既存 `PATCH /knowledge/contributions/{id}` の `state: rejected` で候補を閉じる。理由は短文・任意とする。現行 `Service.transition` は `reason` を必須入力として検証するため、空の理由を許す最小変更が必要。Noの後に利用者へ通知するかは未決。
- **指示:** 候補を `in_review` のまま保ち、指示・直前案・同じ根拠で再生成する。新しい案は別履歴として受信箱に戻す。履歴を上書きしない。
- **根拠不足:** 候補を閉じず、理由を示して再照会待ちにする。候補本文や指示を根拠へ昇格させない。

CommonKnowledge の現行責務分割は `intake`（受付・候補）、`editorial`（作業版・確認依頼・判断）、`publication`、`reader`、`recovery` である（`lambda/knowledge/common-knowledge/app.py:18-24`）。候補履歴・AI案操作を追加する場合も必要な責務にのみ配線し、AI実行主体へ `approve` / `publish` / 読者変更 / 削除権限を付けない。

## 5. 版・指紋と公開後の検索

- 案は元になったカードの `knowledgeId`、`cardVersion`、本文SHA-256を保持する。候補の更新版と根拠束のhashも案に結び付ける。
- AI案の表示・Yes確定時に現行版とhashを再照合する。元カード版・本文hash・根拠hashのどれかが変わっていれば自動適用せず、管理者に最新状態での再生成を促す。If-Match と候補版の競合検査を使い、古い画面の操作を409等で止める。
- 新規カードの場合は、管理者が候補をカード編集対象として選んだ時点の作業版を基準にする。元となるカード/作業版を固定できないときはAI案を作らない。
- 技術承認は対象版・根拠束・hashに固定する。承認版は不変で保存し、公開はmanifest世代を使う別操作とする。停止済みの公開を古い要求で戻さない。
- 索引の入力は既存の公開版経路とする。公開されていない案・作業版・却下候補は次のチャットの索引へ入れない。公開後に索引の更新・件数/hash照合を行い、反映確認が済む前に「次のチャットで利用可能」と表示しない。

## 6. フラグ・利用環境

この試作は開発環境限定・管理者画面限定・既定オフとする。両方のフラグが有効でなければ、入口・ボタン・APIを利用できない。

| 用途 | 提案名 | 初期値・条件 |
|---|---|---|
| SAM | `KnowhowImprovementLoopEnabled`（条件 `KnowhowImprovementLoopDevEnabled`） | `false`。`Environment=dev` かつ明示 `true` のときだけループの経路・配線を作る |
| Next.js | `NEXT_PUBLIC_ENABLE_KNOWHOW_IMPROVEMENT_LOOP` | `false`。管理者画面の入口・操作を隠す。フロントの表示だけで認可しない |

既存の rewrite SAM パラメータは `KnowhowRewriteEnabled`（既定 `false`）、ブラウザー側は `NEXT_PUBLIC_ENABLE_KNOWHOW_REWRITE` である（`infrastructure/sam/phase2-template.yaml:95-101,492-494`; `frontend/src/components/knowledge/KnowhowRewritePanel.tsx:90-93`）。既存rewriteフラグとCommonKnowledgeの既定オフを尊重し、ループ用フラグを別に設ける。実環境でCommonKnowledgeが有効か、itai環境でこのテンプレートを使うかは確認できていない。フラグが合成受入で安全に動くことを確かめるまで有効化しない。

CommonKnowledge側の現行SAMフラグは `CommonKnowledgeEnabled`（既定 `false`、`infrastructure/sam/common-knowledge-itai-template.yaml:26-30,63-70`）。提案するループフラグはこれと rewrite フラグの両方を前提条件として扱う。環境の実配備・有効状態は別途確認する。

## 7. 実装段階と合成受入

> 最終検証: 2026-11-18 — S1 の受入条件と合成Playwrightの画面経路を確認。連続2回の再生成、直前案の引継ぎ、同じ根拠/版/対象節、履歴切替、古い確認/差分の破棄、管理者確認後の下書き反映を確認。実環境・実モデル・AWS実機は未確認

すべて架空の利用者・機種・カード・根拠を使う。合成データの成功は実資料、業務受入、AWS配備の確認を意味しない。

| 段階 | 実装単位 | 合成データでの受入条件 |
|---|---|---|
| **S1 指示で再生成** | rewrite要求に1,000字以下の `instruction` と前回案を追加。既存書き換えパネルに「指示して作り直す」を加える。受信箱に依存しない。 | 根拠・カード版が同じまま、初回案→指示→再生成を複数回実行して各案と指示を区別できる。指示付き要求の未裏付け数値は拒否し、指示で求めた未裏付け内容は変更しないようモデルへ指示する。意味の正しさは検証できず、指示付き案に常時注意書きを出して管理者の差分確認を最後の砦とする。1,001字、未知キー、壊れた前回案は拒否する。既存の差分検査・警告・conflict処理を維持し、APIが本文を保存しないことを確認する。 |
| **S2 チャットから明示受付** | 3種類の入口に利用者の送信選択・確認編集画面・個人情報/顧客名の注意を追加。確認済み本文だけを `contributions` へ登録し、由来 `intakeKind` を持たせる。 | 3入口が正しい `intakeKind` と `originRef` で登録される。送信前の編集が反映される。キャンセル・未確認は登録されない。会話全文・隣接ターン・顧客名を自動複製しない。同一送信再試行は二重登録されず、改変された同一originは競合として拒否される。 |
| **S3 受信箱の案・判断・履歴** | 既存 `CommonKnowledgeInbox` を拡張。グループ件数、1クリックAI案、Yes/No/指示、候補ごとの履歴を表示・保存する。必要最小限の候補フィールド・履歴API・状態検証を追加し、別台帳は作らない。 | `knowledgeId`・版・由来別の決定的集計が一致し、異なる版/種別は混ざらない。許可外読者は候補や件数を読めない。Yesは作業版までで停止し、技術承認・公開が別人の明示操作に残る。Noの理由は任意で状態が閉じる。指示・案・判断の操作者/時刻/参照が並び、更新競合・再送で履歴が欠落/重複しない。本文ログなしを確認する。 |
| **S4 公開から索引へ** | 既存の技術確認・承認・公開後に、公開版から索引へ反映し次のチャットで読む経路を接続・確認する。 | 未公開案・draft・rejectedは検索結果に出ない。承認だけでは索引に入らず、publish後の指定版/hashが索引と一致する。反映遅延・失敗・manifest変更時は利用可能と誤表示せず、再試行後に同じ公開版が一度だけ反映される。 |

### 7.1 自動下書きの停止条件

第1版で自動にするのは受付後の確定的な重複整理・件数集計だけ。AI案生成は管理者の1クリックで始める。受付時にAI案まで自動作成・保存する運用は #207 WP7 の未回答事項と同じ判断領域であり、別フラグ・既定オフとする。共同確認と状態・権限・公開版検索・候補結合の契約が揃うまで有効化しない（`docs/design-2026-11-16-gyomu-knowhow-evidence.md:134-135`; PR #207設計 `docs/design-2026-11-11-knowledge-governance.md:198-226,429-435`）。

## 8. 権限・ログ・データ保護

- 受付本文は本人が確認した最小限のテキストだけを候補として保存する。チャット全文・未選択の回答・顧客名・個人情報・参照引用全文を自動保存・ログ出力しない。
- JWT由来の操作者、保護されたサーバー認可表、分野・読者・期限・共有許可で各操作を検証する。管理者UIの表示条件だけでAPIを認可しない。
- AIは提案・未検証の作業版まで。候補の承認、正本反映、公開、読者変更、削除は人の権限に残す。AIに公開・承認・削除用API/IAMを与えない。
- 指示、候補文、AI案、質問、回答、顧客情報、引用全文、`sub` をCloudWatch Logsへ出さない。ログはイベント種別・段階・成否・エラー分類・所要時間・件数など本文を含まない指標に限定する。
- 版/hash、根拠、候補状態が不整合・期限切れ・読取不能なら案の保存や利用を止め、管理者へ再確認を促す。既存公開版を自動で書き換えない。

## 9. 共同確認が必要な点

以下はこの仕様では決めない。

1. 候補、指示、AI案、判断履歴の本文とメタデータの保存期間・削除方法。
2. Noで閉じた後、利用者へ通知するか。通知する場合の内容・方法・時期。
3. 受付の対象読者、対象部門、対象機種・資料範囲。業務スコープ変更は根拠・影響件数・対象外データの扱いを含め mona/itai で共同確認する。
4. 受付時のAI自動下書きの可否、別フラグ、対象条件と停止条件。
5. AI利用料の上限・月間/候補単位の予算停止方法。
6. itai環境で CommonKnowledge が有効か、どのSAMテンプレート・認可表・保存先を接続対象にするか。

## 10. 既存実装との差分と未実装

> 最終検証: 2026-11-18 — S1 の Lambda 入力検証・プロンプト分離・数値裏付け範囲、フロント単体テストと合成Playwrightの再生成・履歴・下書き反映を確認。Bedrock実出力・AWS実機は未確認

- 候補の既存 `candidateType` は `field_report` / `unknown_term` / `correction` / `request` であり、3種類のチャット起点を個別に示す項目はない。`intakeKind` の追加と送信元の対応付けが必要。
- 現行の重複防止は同一投稿者・種別・`originRef` に対する冪等性であり、同一カード版・由来種別のグループ集計ではない。
- S1 の API と画面を実装済み。rewrite 要求に1〜1,000字の `instruction` と、同じカード版・対象節hashに結び付いた `previousProposal` を追加し、同じ根拠で再実行する。パネルはページ内だけで「第1案」「指示→次案」の履歴を表示し、選んだ案を既存の差分確認・反映フローへ渡す。409（カード版・対象本文の競合）を利用者向けに表示し、`field` レーンでは再実行欄を出さない。rewrite APIは指示・案を永続化しない。指示付き案の未裏付け数値を拒否し、注意書きを表示する。自動テストは要求生成・入力上限・履歴・表示・409 を確認する。合成Playwrightで再生成・履歴・人の確認後の下書き反映を確認済み。実環境・実モデル・有効化後の受入は未実施。
- CommonKnowledge受信箱は編集・特定版技術確認・承認・公開を持つが、AI案の作成、Yes/NoによるAI案判断、候補に紐づく指示・案履歴は持たない。
- 現行 `transition` は理由を必須としており、Noの任意理由と異なる。
- S4の索引反映は既存公開版読取経路を使う前提であり、本仕様時点で接続・配備・実チャット反映を確認したものではない。

したがって、本書は仕様案であり、全体のループが既に実装済み・有効化済みという意味ではない。

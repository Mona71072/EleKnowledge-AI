---
status: draft
last-verified: 2026-09-09
related-code: frontend/src/app/, lambda/rag/rag-function/app.py, lambda/chat/chat-management/app.py, infrastructure/sam/phase1-template.yaml
---

# EleKnowledge 利用者マニュアル 管理者向け確認表（第1版）

作成日: 2026-09-09　作成: Claude Code（依頼者: itai）
対象成果物: `docs/user-manual/EleKnowledge_利用者マニュアル_v1.pdf`（原稿 `eleknowledge-user-manual.html`、画像 `images/`）

## 1. 参照版

| 項目 | 値 |
|---|---|
| リポジトリ | https://github.com/yukiworkspace/EleKnowledge-AI/ |
| 正本ブランチ | `develop` |
| 参照コミット | `ba6d3303225f8fabf894f2ef9e38364396b5a081`（2026-08-27 21:08 JST, PR #71 マージ） |
| 実環境（フロント） | Amplify app `d9ngenggxas1k` branch `develop` = 上記コミット ba6d330 をビルド（Job 27, 2026-08-27 21:10 JST 成功）。`https://develop.d9ngenggxas1k.amplifyapp.com/` |
| 実環境（バックエンド） | Lambda `rag-dev` / `chat-dev`（ap-northeast-1）。**最終更新 2026-09-09 16:11 JST**。環境変数 `SESSION_TITLE_LLM=true`, `CITATION_URI_MODE=s3`, `PRESIGNED_URL_EXPIRES_IN=300` |
| 認証 | Cognito User Pool `users-dev`（ap-northeast-1_DN17ekXik）。PreSignUp / PreAuthentication に DomainGuard 関数が設定済み |
| 添付画像（依頼時） | 14 枚（ログイン、PDF 表示、チャット初期、ホーム×2、メール確認、Outlook、アカウント作成、要望モーダル、絞り込み、回答・評価×3、絞り込み中の回答）。**画像ファイルとしては受領していない**（チャット上の表示のみ）。ファイル名は参照できなかった |
| 参照ドキュメント | `docs/features/production/phase1-foundation.md`（last-verified 2026-08-21）、`docs/api/rag.md`（2026-08-26）、`docs/api/chat.md`（2026-07-29）、`docs/security.md`（2026-08-21）、`docs/features/production/phase2-rag-chat.md`（**実装と乖離の警告あり。根拠に使用せず**） |

## 2. 説明範囲と根拠

| # | 利用者の操作 | 主な根拠（コード） | 画面根拠 | 実操作確認 |
|---|---|---|---|---|
| 1 | サインアップ | `frontend/src/app/signup/page.tsx`, `verify/page.tsx`, `components/ui/PasswordStrength.tsx`, `VerificationCodeInput.tsx`, `lambda/cognito-domain-guard/domain_guard.py`, `infrastructure/sam/phase1-template.yaml`（PasswordPolicy） | 添付: アカウント作成／メール確認／Outlook。自撮影: 03-*, 04-* | 実サイトで入力・バリデーション表示まで確認。**登録（Cognito SignUp）は未実施** |
| 2 | ログイン／ログアウト／パスワードリセット | `login/page.tsx`, `forgot-password/page.tsx`, `page.tsx`(handleSignOut), Cognito クライアント設定（Refresh 24h） | 添付: ログイン。自撮影: 01-*, 02-*, 05-* | 実サイトで入力まで確認。**実アカウントでのログイン・リセットは未実施**（エラー表示・ステップ2 はモック応答で表示） |
| 3 | ホーム画面 | `frontend/src/app/page.tsx`, `components/announcements/*` | 添付: ホーム×2。自撮影: 06-* | 実サイトの develop ビルドで、認証トークンと API 応答をブラウザ内で差し替えて表示（後述 §4） |
| 4 | 質問を送る（聞き返し／見つからない含む） | `chat/page.tsx`（handleSendMessage ほか）, `lambda/rag/rag-function/app.py`（needs_clarify, build_not_found_content, 注意書き付与） | 添付: チャット初期／回答。自撮影: 07, 11, 12, 13, 20, 21 | 同上（RAG API はモック応答） |
| 5 | 絞り込み | `chat/page.tsx`（categoryOptions, ALL_MODEL_TYPES）, `data/kbModelTypes.ts` | 添付: 絞り込みパネル×2。自撮影: 08, 09, 10 | 同上（UI 操作は実ビルドで確認） |
| 6 | 回答と参考資料 | `chat/page.tsx`（pageCandidates, sourceDocuments, さらに N 件表示）, `lib/documents.ts`, `app/doc/page.tsx`, `rag-function/app.py`（GET /rag/document, PRESIGNED_URL_EXPIRES_IN） | 添付: 回答／参考資料展開／PDF 表示。自撮影: 13-*, 14, 22 | 同上。PDF 実表示は添付画像でのみ確認 |
| 7 | 評価・要望 | `components/chat/ChatMessageFeedback.tsx`, `ProductWishModal.tsx`, `lib/chat-failures.ts` | 添付: 解けない／解けた／要望モーダル。自撮影: 15, 16, 17, 19 | 同上（PUT feedback / POST suggestions はモック） |
| 8 | 履歴 | `chat/page.tsx`（sessions, handleDeleteSession）, `lambda/chat/chat-management/app.py`（TTL 60 日, title） | 添付: 履歴一覧。自撮影: 18 | 同上（削除の confirm ダイアログは撮影不可・文言はコードから） |
| 9 | 問い合わせ | 依頼文の運用案内 | — | — |

## 3. 確認結果（分類別）

### 3.1 コードで確認した事項

- 登録可能ドメインは `@meltec.co.jp` と `@<sub>.mitsubishielectric.co.jp` のみ（PreSignUp/PreAuth。実環境の User Pool にも設定済みであることを AWS CLI で確認）。
- パスワード条件: 8 文字以上・大文字・小文字・数字・記号（UI と Cognito 双方）。UI の記号判定は `!@#$%^&*(),.?":{}|<>` に限定（Cognito はより広い）。
- 名前は 2 文字以上（UI バリデーション）。
- 確認コード再送信は 60 秒間隔（`resendTimer`）。確認後、同一タブなら自動ログイン→ホーム（1.5 秒後）、それ以外はログイン画面（2 秒後）。
- ログイン画面を開くと `signOut({global:true})` と localStorage/sessionStorage クリアが走る（＝ログイン画面を開いた時点でログアウト）。
- セッション有効期間: Refresh Token 24 時間、Access/ID 60 分（テンプレートと実クライアント設定の両方で確認）。
- ホームの質問入力→`/chat?q=` で入力欄に引き継ぎ（自動送信はしない）。
- チャット: Enter 送信・Shift+Enter 改行・入力 200px 上限・送信中は入力不可。回答本文はタイプライター表示。参考資料は上位 3 件＋「さらに N 件表示」。該当頁候補は最大 5 件、`#page=N` 付きで `/doc` 経由。
- 絞り込み: 資料 9 種（複数）、機種 6 種（単一）。w_doc（W 資料）は業務判断待ちで非表示。機種未指定時は回答先頭に注意書き。
- 聞き返し: 症状語あり＋（機種未指定 or 部位・状況とも無し）で発火。追記は直前質問と結合して検索（`compose_search_query`）。
- 見つからない: `not_found` 時「検索が弱いため断定回答はしていません」＋カテゴリ絞り込み中のみ「資料カテゴリの絞り込みを外す」ボタン。
- 引用 URL: `/doc?uri=s3://…` → `GET /rag/document` で署名付き URL を都度発行。有効期間 300 秒（実環境の環境変数で確認）。未ログインならログイン後に `/doc` へ戻る。
- 評価: 解けた／解けない、理由 4 種、補足 200 字、要望 1000 字。トースト文言はコードのとおり。
- 履歴: TTL 60 日（`60*24*60*60`）、`daysUntilDeletion` 表示、削除は `window.confirm('このセッションを削除しますか？')`。
- WAF: Amplify アプリに Web ACL 関連付け済み（`ASSOCIATION_SUCCESS`）、既定 Block、`IpAllowList`（Allow）＋ AWS マネージドルール 3 種。**許可 IP の内容は確認していない（Tier A のため未記載）**。

### 3.2 画像（添付）で確認した事項

- ログイン／アカウント作成／メール確認／ホーム／チャット初期／絞り込み／回答／評価パネル／要望モーダルの画面構成と文言がコードと一致。
- 確認メール: 差出人 `no-reply@verificationemail.com`、件名 `Your verification code`、本文 `Your confirmation code is ######`（Cognito 既定テンプレート。実環境も既定＝null を確認）。Outlook では「社外メール」フォルダーに振り分けられていた。
- 引用 PDF は S3 の署名付き URL でブラウザ表示（ヘッダー「社外秘（協力会社開示可）」の資料が表示されている）。
- 履歴見出し: 添付の 3 枚では「※機種未指定のため、一般資料…」「# 溶接作業の据付基準（整理）…」（develop の挙動）、別の 1 枚では「溶接脚長の基準外判定」など短い見出し（PR #84 の挙動）。

### 3.3 実際の操作で確認した事項（2026-09-09、Playwright + Chromium、社内ネットワーク）

- 公開ページ（/login, /signup, /verify, /forgot-password）: 実サイトで表示・入力・バリデーションを確認。
- 認証後ページ（/, /chat, /doc）: **実サイトの develop ビルド**に対し、ブラウザ内で認証トークン（Cookie）と API 応答（Cognito GetUser、/chat/*、/rag/*、/announcements）を差し替えて操作。UI の挙動（絞り込み、送信、参考資料展開、評価パネル、要望モーダル、履歴操作）は実コードで動作。**バックエンドへの書き込みは一切行っていない**。
- 自撮影画像の利用者名・メール・質問・回答・資料名は説明用サンプル（資料名は添付画像に出ていた実在の文書名を流用）。

### 3.4 未確認の事項

- 実アカウントでのサインアップ→確認コード→自動ログインの一連動作（Cognito 実呼び出し）。
- 実アカウントでのログイン、パスワードリセットのメール受信と完了。
- 実 RAG API の応答（回答内容・所要時間・聞き返し／見つからないの実発生条件）。マニュアルの「数秒〜十数秒」は目安であり実測していない。
- 添付画像 14 枚のファイル名（受領できず）。
- WAF 許可 IP に対象部門のネットワークが含まれるか。
- 「該当頁候補」から開いた PDF が該当ページで開くか（`#page=N` はブラウザ PDF ビューア依存）。
- 削除確認ダイアログの実表示（ネイティブ confirm）。

## 4. コード／画面／運用案内の食い違い（利用者操作に影響するもの）

| # | 区分 | 内容 | 影響 | マニュアルでの扱い | 管理者の判断事項 |
|---|---|---|---|---|---|
| D1 | 実装済み・develop 未マージ・**dev 環境反映済み** | 履歴見出しの生成（PR #84, 2026-09-09 作成）。`rag-dev`/`chat-dev` は同日 16:11 JST に更新され `SESSION_TITLE_LLM=true`。develop（ba6d330）のコードでは見出しが「※機種未指定のため…」や Markdown 見出しになる | 履歴の見出し表示が PR #84 の状態で説明されている | 9.1 で「最初の質問をもとに自動で付く」とだけ記載（LLM 生成／切り詰めのどちらでも成立する表現） | PR #84 をマージするか、dev 環境を develop に戻すか。戻す場合は 9.1 の記述と図 9-1 の見出し例を差し替え |
| D2 | 実装・反映済み | 引用 URL モードが `s3`（都度発行）。`docs/api/rag.md` は既定 `presigned` と記載（切替手順どおり）。develop フロントは両方に対応 | なし（説明は都度発行前提で記載） | 7.3 に「約 5 分で無効」と記載 | ドキュメントの「現在の設定値」追記要否 |
| D3 | 名称 | 運用案内は「Ele-Knowledge」、画面・リポジトリは「EleKnowledge」 | 検索・問い合わせ時の表記ゆれ | 表紙・本文で「EleKnowledge（サポート名: Ele-Knowledge）」と併記 | 正式名称の統一 |
| D4 | 仕様書と実装 | `phase1-foundation.md` の「トークン保存: localStorage」は誤り。実装は `Amplify.configure(..., {ssr:true})` により Cookie 保存 | 利用者操作には影響なし（内部） | 記載なし | production ドキュメントの修正（事前確認要） |
| D5 | 仕様書と実装 | `phase1-foundation.md`「失敗回数制限: 5 回でアカウントロック（15 分）」は Cognito 既定の一時ロック挙動を指すと解釈。UI は `NotAuthorizedException` を「メールアドレスまたはパスワードが正しくありません。」として表示するため、ロック中も同じ文言になる | ロック中に原因が分かりにくい | 3.2 で「何度も失敗すると一時的にログインできない。数分〜15 分待つ」と記載 | 文言追加の要否（実装変更） |
| D6 | 画面文言 | ホームの「参考資料の見方」小窓は「資料タイプ/モデル」と表記、チャット画面は「資料／機種」 | 軽微（用語ゆれ） | マニュアルは「資料／機種」で統一 | 文言統一の要否 |
| D7 | 動作（コード由来・未実測） | ホーム／チャットの質問例「異音が出るときに最初に確認する項目は？」は、機種未指定で送ると聞き返し（clarify）になる条件を満たす（症状語「異音」あり、部位・状況語なし） | 質問例を押した利用者が最初に聞き返しを受ける | 5.3 で聞き返しの説明を記載。質問例自体には言及せず | 質問例の見直し、または実機で確認 |
| D8 | 動作（モック環境で再現・実環境未確認） | 初回送信後に `fetchSessionMessages` が完了するタイミングとタイプライター表示のタイマーが競合し、本文が途中で止まった状態になることがある（`chat/page.tsx` の `streamingMessages` 更新順序）。API 応答が即時のモックで再現。実環境では応答に数百 ms かかるため発生頻度は不明 | 発生時、回答本文が途中までしか表示されない（履歴から開き直すと全文表示） | 5.5 に「履歴からそのチャットを開いて確認」を記載 | 実環境での再現確認とフロント修正要否 |
| D9 | 運用案内 | 「登録方法はサインアップしたら利用可能」に対し、実装はメールドメイン制限あり（他ドメインは「登録に失敗しました」） | 対象外ドメインの利用者は登録不可 | 1.2、2.1、2.4 に対象ドメインを明記 | 対象者に該当しないドメインがあるか |
| D10 | 環境 | 配布対象 URL が `develop.…amplifyapp.com`（開発環境）。本番 URL ではない | 将来 URL が変わる可能性 | 表紙・1.2 に記載 | 配布時点の正式 URL の確認 |
| D11 | 個人情報 | 添付画像には依頼者の氏名・メールアドレス・実在資料の内容が含まれる。マニュアルの画像はサンプル名（現場 太郎 / sample.user@meltec.co.jp）に置き換えた自撮影画像を使用。資料名（GM-01-05-D.pdf 等）と抜粋文はサンプルとして残している | 配布範囲によっては資料名・抜粋の扱いを確認要 | 冒頭に「画像内の内容は例」と明記 | 社外秘資料名・抜粋のマニュアル掲載可否 |
| D12 | 未提供機能 | ホームの「トラブルシューティング」カードは一般利用者には「開発中」で開けない | 押しても何も起きない | 4 章・10.1 に「利用不可」と記載 | 公開時期の案内 |

## 5. 配布前の残課題

| # | 課題 | 区分 | 担当（案） |
|---|---|---|---|
| R1 | D1 の方針決定（PR #84 マージ or 環境戻し）。戻す場合はマニュアル 9.1 と図 9-1 の修正 | 配布可否を左右 | itai / mona |
| R2 | 実アカウントで 2 章→3 章→5 章→7.3 の一連操作を実施し、所要時間・聞き返しの実挙動・PDF のページ指定を確認（3.4 の未確認事項） | 手順の正しさ | itai（実環境で操作可能な担当） |
| R3 | 自撮影画像を、依頼者の実画面（サンプル名でログインした状態）に差し替えるかの判断。差し替える場合は `capture.js` の注釈位置に合わせて番号を付け直す | 画像の真正性 | itai |
| R4 | D11: 資料名・抜粋の掲載可否確認 | 情報管理 | itai / 品質管理 |
| R5 | D9: 対象者のメールドメインが `@meltec.co.jp` / `@*.mitsubishielectric.co.jp` に収まるか確認 | 登録可否 | itai |
| R6 | D10: 配布時の正式 URL 確認 | 案内の正しさ | itai |
| R7 | D4 / D5 / D6 の production ドキュメント・文言修正（別 PR、事前確認要） | 記録の整合 | 任意 |
| R8 | D8 の実環境再現確認 | 品質 | mona / itai |

**配布可否の判定:** 現時点では「条件付き」。R1（履歴見出しの方針）と R2（実アカウントでの通し確認）が完了するまで、配布可能と断定しない。上記が済めば、原稿の修正は 9.1 周辺と数値（所要時間）の微修正にとどまる見込み。

## 6. 成果物一覧

| ファイル | 内容 |
|---|---|
| `docs/user-manual/EleKnowledge_利用者マニュアル_v1.pdf` | 利用者向けマニュアル（配布形式） |
| `docs/user-manual/eleknowledge-user-manual.html` | 同 原稿（HTML）。修正後 `build-pdf.js` で再生成 |
| `docs/user-manual/images/*.png` | 画面画像（注釈付き、自撮影） |
| `docs/user-manual/admin-verification-sheet.md` | 本確認表（正本） |
| `docs/user-manual/EleKnowledge_管理者向け確認表_v1.pdf` | 本確認表の PDF |
| `docs/user-manual/build-pdf.js` | PDF 生成スクリプト |
| `docs/user-manual/capture.js` | 画面撮影スクリプト（実サイト＋ブラウザ内モック。再撮影用） |

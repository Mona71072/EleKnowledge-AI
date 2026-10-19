---
status: development
last-verified: 2026-10-20
related-code:
  - frontend/src/app/admin/knowledge/research/page.tsx
  - frontend/src/components/knowledge/KnowledgeResearchWorkspace.tsx
  - frontend/src/lib/knowledge-research.mjs
  - frontend/tests/knowledge-research.test.mjs
---

# 工技先輩の開発画面：ノウハウ・技術KB・法令KBの照合

## 目的と完成条件

開発中の独立した画面で、選択したノウハウMarkdownを読み、技術KBと法令KBを調べ、根拠を比較して編集案を作る。最終目標は、三つの情報源を条件・出典付きで活用できる、実際に使えるアプリである。画面表示やモック試験だけで最終目標を完了としない。

段階的に、(1)両KBへの実API接続と出典別の比較、(2)選んだ結果のMarkdown編集案への取込み、(3)許可された開発環境で実検索と出典閲覧、(4)適用条件・食い違いを扱う統合支援と評価を進める。通常・法令の回答を単に並べた状態を「統合AI回答」と呼ばない。実環境の検索・閲覧・適用確認は未検証として残す。

## 今回実装する接続

- `/admin/knowledge/research`に「工技先輩（開発中）」を追加。既存のノウハウ機能フラグを使い、通常画面と分ける。既存admin利用者の試行用であり、新しい利用者へのadmin付与はしない。
- 技術KBと法令KBは既存`POST /rag/query`へ、同じ明示入力の質問を`mode: normal`と`mode: law`で並列送信する。CognitoのID tokenをAuthorizationに使い、userIdを本文へ追加しない。モード間でsessionIdを共有しない。
- 初期版は毎回独立した問い合わせとし、履歴継続は既存チャットの各モードへのリンクで行う。APIが作る履歴は通常・法令それぞれ別であり、既存の60日保持対象となることを送信前に表示する。
- ローカルMarkdown・OneNote案・メタデータ・ファイル名を自動送信しない。送信対象は質問欄だけ。資料をもとに質問する場合は利用者が質問欄へ必要な内容を入力して確認する。
- 各回答は独立した出典欄に表示する。一方が未設定・403・タイムアウト・検索失敗でも、成功側を利用できる。未収載とAPI利用不可を区別する。法令が失敗しても技術KBで代用しない。
- 質問は空白以外1〜2000文字。設定不足・未認証・不正な応答は日本語で案内。通信と認証待機には上限を設け、中止・新規検索・画面終了後の古い応答で現在の結果を上書きしない。中止してもサーバー処理・履歴保存そのものの取消は保証しない。

## 出典と編集

技術資料は既存の認証付き`/doc`経由で開く。S3の署名付きURLを持ち帰りファイルやリンクへ残さず、S3 URIへ戻して中継する。法令は応答にある法令名・条文・施行日・e-Gov出典を表示し、HTTPSのe-Gov法令URLだけを有効にする。日付や条文番号、リンクのアンカーを推測しない。API応答の生HTML・埋込・画像を実行しない。

「編集案へ取り込む」で、選択した回答と出典を調査メモとしてローカルMarkdown本文へ追記する。これはAI回答の採用候補であり、技術承認・法的判断・KB本文の人手確認ではない。照合済みチェックを自動で付けない。本文編集と同じ版失効を通し、OneNote案との再照合を必要にする。元ファイル・OneNoteへ自動書込みしない。

取り込み先は検索開始時の文書セッション・ID・原版・本文の作業版へ紐付ける。文書の再取込・別文書への切替・本文の手編集後は旧結果を表示できても取込み不可とし、再検索を案内する。ファイル未選択での調査は閲覧用であり、後から選んだファイルへ無警告で適用しない。同一検索の技術・法令両メモを順に追加する操作は許容し、その既知の追記だけでは相手側の結果を失効しない。取り込み先の条件を変える本文手編集は必ず失効させる。

調査メモには検索モード・質問・クライアント受信日時、APIが返す回答日時（有効な場合）、sessionId/messageIdも追跡情報として残す。これらはAI回答の追跡用であり、資料の改訂版や技術承認の識別子ではない。API履歴は60日で失われ得るため、採用時の本文と出典も併せて保持する。

## 実装の分担と契約

`knowledge-research.mjs`は`queryKnowledgeSource({baseUrl, getToken, fetchImpl?, mode, query, signal?, timeoutMs?})`、`researchSourceHref(source, mode)`、`buildResearchNote(answer)`を公開する。API応答は`content`、`responseType`、`sessionId`、`aiMessageId/messageId`、`sourceDocuments`、`pageCandidates`、`clarifyQuestions`を検証して正規化し、`.d.mts`で型を共有する。

`KnowledgeResearchWorkspace`は検索と結果表示を担当し、`KnowledgeWorkbench`の編集状態を正本とする。任意の`research`モードで編集画面に検索欄を表示し、採用操作だけを既存`editBody`へ渡す。API認証や検索結果から公開・レビュー状態を生成しない。

## 検証と未完了項目

TDDで認証・送信項目・モード分離・不正入力・不正応答・出典URL・HTTPエラー・中止/タイムアウト・調査メモを検証する。ローカルHTTPテストダブルとブラウザー操作は接続契約の検証であり、AWSのKB内容や法的適用の正確性の証明にしない。実際の接続先・認証・両KBの有効化・実資料への到達確認が必要。

本番デプロイ、対象資料・対象者の拡大、下書き全文のAI送信、OneNote自動追記は今回の実装には含めない。これらを最終目標の代替条件にせず、必要なものは別途明示して実装・受入を進める。

関連: [ノウハウ編集画面](knowledge-review-workbench.md)、[法令API](../../api/legal-chat.md)、[カードとPDF KB](card-kb-two-tier-retrieval.md)。

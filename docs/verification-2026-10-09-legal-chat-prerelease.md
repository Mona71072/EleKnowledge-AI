---
status: reference
last-verified: 2026-10-09
related-code: frontend/src/app/chat/page.tsx, lambda/rag/rag-function/app.py, lambda/chat/chat-management/app.py, infrastructure/sam/phase2-template.yaml
---

# 法令チャット プレリリース準備確認（2026-10-09）

**目的:** 最新PRの合意・マージの証拠と、文書作成時点で確認していない実環境の項目を記録する。

追加依頼に基づくdevelop公開反映の結果は§6へ追記する。§5の撮影時点ではdevelopは法令カード未表示だった。

**検証範囲:** GitHub MCP、developコード、ユーザーの操作完了申告、ログイン済みブラウザによるdevelop / itai配信画面の読取り・撮影、Amplifyの公開設定・job、RAG Lambdaの法令有効化設定。コード照合元は`b8070f56`、追加公開の採用版は`795aa0a2`。費用とAWSリソース全体の再検証は対象外。運用手順は[プレリリース手順](legal-chat-prerelease.md)、決定条件は[対象一覧](features/development/legal-rag-target-laws.md)を参照する。

## 1. PRで確認できたこと

| 日時（JST） | 発言者・記録 | 読み取れる範囲 |
| --- | --- | --- |
| 2026-10-06 20:14 | [Monaの#155回答](https://github.com/yukiworkspace/EleKnowledge-AI/pull/155#issuecomment-6015041836) | CSV一致・分野別理由を初期候補根拠としてYes。dev条件、対象外案内、月額100 USD仮上限、2026-12-31評価で共同確認を進めること、加工事実・主体表示にYes。正式部門等は未確認 |
| 2026-10-06 20:14 | [Monaの#156回答](https://github.com/yukiworkspace/EleKnowledge-AI/pull/156#issuecomment-6015041381) | 必須4点の技術修正はYes。衝突解消、#155のゲート、#168後のCI成功をマージ条件として記載 |
| 2026-10-09 18:36 | [itaiのdev試行範囲の補足](https://github.com/yukiworkspace/EleKnowledge-AI/pull/155#issuecomment-6078333229) | 既存develop / AWS devで反映・計測する目的を明示。本番・正式部門・範囲拡大・追加同期・削除の承認とは区別 |
| 2026-10-09 19:45 | [itaiの#155マージ記録](https://github.com/yukiworkspace/EleKnowledge-AI/pull/155#issuecomment-6079334718) | 10/6のYesと未確認事項を保持したまま、既存試行devで計測を進める前提でマージする旨 |
| 2026-10-09 19:47（コメント表記） | [itaiの#156マージ記録](https://github.com/yukiworkspace/EleKnowledge-AI/pull/156#issuecomment-6079341838) | #155マージ、最新head CI成功、競合なしを確認したとの記録。SAMはitai |

GitHubメタデータでは#155は2026-10-09 19:46:03 JSTにマージ済み（`760fccb45beafa33232488376cf9e3b66114f85d`）、#156は19:46:29 JSTにマージ済み（`25139cebece79df288396f3885123c5d78000eec`）。上の#156コメントの「19:47」は投稿者の表記であり、メタデータの秒単位時刻とは区別する。

今回確認した最後のコメントはitaiの実施記録であり、新たなMonaの全面承認が投稿されたという意味ではない。既存dev試行の記録として読み、本番・正式業務採用・範囲拡大・追加同期・削除の許可へ拡張しない。

## 2. コードとの照合

| 項目 | 確認結果 |
| --- | --- |
| 入口 | `page.tsx`は公開フラグで法令カードを表示。`/chat?mode=law`へ遷移 |
| 検索・履歴 | `mode=law`、法令専用KB、`ragMode`別のセッション取得とモード不一致409 |
| 入力 | JSON object、queryの型・空白・2000文字、sessionId最大128文字、filtersの型を検証 |
| ゲート | `ENVIRONMENT=dev`・`LAW_RAG_ENABLED=true`・KB IDあり。条件不成立時403 |
| 出典 | `lawCitation`、e-Gov HTTPS URL、施行日、加工主体の文言。APIの`sourceUri`もe-Gov URL |
| 提供しない絞り込み | `lawId` / `legalTopics`の検索指定は未実装。lawではfiltersを空に正規化 |
| 過去時点 | `asOfDate`なし。現行版スナップショット。将来設計と区別 |
| 既知の限界 | 全文補完はdev実験。過去の5送信で9.57〜25.95秒という記録は今回の計測ではない。未取得の関連条文の救済は未実装 |

## 3. 実環境の確認結果記入欄

ユーザー申告、ブラウザでの実確認、AWS設定の読取りを区別する。実アカウント操作はitai配信版で完了済み。対象利用者はdev環境の全ユーザー、実費は今後確認するとの指示を反映した。人数や実費の確定を既存dev試行の追加条件にはしない。

| 項目 | 状態 | 確認日時・担当 | 証拠・対象期間・備考 |
| --- | --- | --- | --- |
| develop採用版とAmplify配信job・成功 | 反映済み | 2026-10-09 / Codex | `795aa0a2`、job 64のBUILD / DEPLOY / VERIFYすべて`SUCCEED`。実ログイン済みブラウザで法令カードと法令画面への遷移を確認 |
| RAG / Chat Lambdaの反映版 | 未確認 | — | — |
| AWS側の法令有効化設定とフロント公開設定 | 設定読取り済み | 2026-10-09 / Codex | `rag-dev`はdev・有効化true・KB IDあり。develop公開フラグtrue、ビルド用依存のインストール設定を追加。APIでの新規質問送信は今回未実施 |
| 本番OFFを維持した設定・本番無変更 | 未確認 | — | — |
| 既存KB / DataSourceのprefixと同期状態（再同期なし） | 未確認 | — | — |
| 利用対象 | 確定 | 2026-10-09 / ユーザー指示 | dev環境の全ユーザー。人数の集計は利用対象の決定と分ける |
| 対象期間の法令実利用者数 | 今後計測 | — | 試行中の計測項目。公開の追加条件にしない |
| 実費／推定費、入力・出力token数、運用工数 | 今後確認 | 2026-10-09 / ユーザー指示 | 実費は今後確認。合意済みの月額仮上限・見直し責任者・評価期限は維持 |
| 実アカウントでの操作確認 | 完了済み（ユーザー申告） | 2026-10-09 / ユーザー申告 | 確認環境はitaiブランチの配信版。個別P01〜P11の全項目合格やdevelop反映済みとは読み替えない |
| 法令画面画像と配信版の一致 | 実撮影済み | 2026-10-09 / Codex | ホーム・初期画面はdevelop、既存回答・出典・履歴・e-Gov原文はitaiを撮影。撮影元は管理者用文書で保持。itaiは開発確認用で利用者への展開先ではないため、利用者本文には記載しない |
| 第2版PDFの配布前確認 | 画像更新・再生成済み | 2026-10-09 / Codex（文書作成担当） | developの入口2画像へ更新。組版・リンク・画像参照を確認。新規回答の加工表示と問い合わせ先の最終確認は残る |

正式対象部門の決定は別途共同確認する。実測記録へ氏名・メール・JWT・法令引用全文を貼り付けず、匿名化した件数・request ID・管理者限定証拠の所在を記録する。

## 4. 文書・配布候補の検証

> 最終検証: 2026-10-09 — 相対リンク・HTML画像参照・PDF本文・追加章の組版、develop / itaiの実画面を確認。AWS法令有効化設定と配信結果は§6、実費は今後確認。

- 変更した文書の相対リンクと利用者HTMLの画像ファイル存在を確認。既存のChat APIから改善提案設計への相対リンク1件も修正した。
- 利用者・管理者の第2版PDFをEdge headlessで再生成（改訂履歴追加後は利用者38ページ、管理者9ページ）。法令章の6画面と管理者冒頭を目視し、日本語・表・改ページを確認した。全ページの既存内容を今回再検証したという意味ではない。
- 管理者PDFのリンクをGitHub文書URLへ変換し、作成端末のローカルパスを配布物へ含めない。Markdown正本の相対リンクは維持する。
- 利用者の追加指示に合わせ、表紙の対象者を第1版の「東日本支社 工事統括部　現場代理人・品質管理担当者」に戻した。利用者本文・代替テキストからitaiブランチ名と提供対象の区別を削除し、撮影元は管理者用文書で保持する。
- HTML・利用者PDFの目次14項目（1〜11章、付録A／B、改訂履歴）をリンク化。HTMLのIDとPDF内部の名前付きリンクを照合し、全14件の遷移先に該当見出しがあることを確認した。PDFの本文にitai・dev全ユーザーの説明が残らず、表紙の対象者が指定どおりであること、配布PDFにローカルファイルURLがないことを確認。目次と法令章冒頭の組版も目視した。
- 追加指示に基づき確認用途のラベルと表紙の「バージョン・作成日」を削除し、末尾に「バージョン・改訂内容・改定日」の改訂履歴表を追加。第1版（2026-09-09）、第1版の訂正（2026-09-11）、第2版（2026-10-09）を記録した。生成スクリプトのヘッダーから版・日付の表示も削除。PDF本文で不要文言の残存がないこと、表紙・目次・最終ページの表の組版を確認した。
- PDF生成スクリプトは第2版のファイル名・ヘッダーへ更新し、JavaScript構文を確認。Playwright実行はしていない。既存第1版PDFは過去の配布物として保持する。
- itaiの6画面に加え、develop反映後のホーム・法令初期画面を撮影して原稿に反映。問い合わせ先と新規回答の加工表示の最終確認は管理者用文書で保持する。実アカウント操作の完了申告と、個別のセキュリティ・ログ試験の証跡は区別する。

## 5. 実配信画面の撮影記録

> 最終検証: 2026-10-09 — 22時台JST、既存Edgeのログイン済み実画面をWindows UI Automation / ウィンドウ撮影で確認。認証・API応答の差し替えなし。

この撮影時点ではdevelopに法令カードがなく、法令URLも通常チャット表示だった。ユーザーの補足「みたのはitaiブランチ」に基づき、itai配信版を撮影対象とした。itaiはdevelop反映前の開発確認用で利用者へ展開していないため、撮影元は本記録と管理者用文書で保持し、利用者本文にはブランチ名を記載しない。既存の法令履歴を閲覧し、新しい質問の送信・評価投稿・履歴削除は行っていない。

| 画像 | 内容・確認範囲 |
| --- | --- |
| [23-law-home-itai.png](user-manual/images/23-law-home-itai.png) | ホームの通常／法令カードとプレリリース表示 |
| [24-law-empty-itai.png](user-manual/images/24-law-empty-itai.png) | 法令初期画面、質問例、収録範囲の注意、入力欄 |
| [25-law-answer-itai.png](user-manual/images/25-law-answer-itai.png) | 既存履歴の建築基準法第三十四条の回答。内容の法的正確性を今回保証するものではない |
| [26-law-citations-itai.png](user-manual/images/26-law-citations-itai.png) | 参考資料の条番号・施行日・関連度 |
| [27-law-history-itai.png](user-manual/images/27-law-history-itai.png) | 法令モードの履歴と残日数 |
| [28-law-egov-itai.png](user-manual/images/28-law-egov-itai.png) | 実際の参考資料リンクからe-Gov原文の第三十四条に到達 |

氏名・メール・ブラウザのタブ・無関係な履歴が入らない範囲を撮影した。回答や出典の内容は差し替えていない。過去の回答を用いたため、developコードにある加工主体の注記がこの撮影例に表示されていない点は、develop反映後の新規回答で確認する。

## 6. develop公開反映の修正

> 最終検証: 2026-10-09 — AWS CLI / boto3でAmplifyとRAG Lambdaの必要設定を読み戻し、ユーザーの公開依頼に基づきdevelop限定で設定変更。

- 採用版: develop `795aa0a2a7489e87ce1b76659cbce6bcced76813`（#170、法令カード公開フラグ追加済み）。今回はGitの新規マージを行っていない。
- 原因: Amplify job 63はNode 22でビルドを開始したが、`Cannot find module '@tailwindcss/postcss'`で失敗。法令公開コードを含む新しい配信へ切り替わっていなかった。
- 読取り: `rag-dev`は`ENVIRONMENT=dev`、`LAW_RAG_ENABLED=true`、法令KB ID指定あり。現在のAPI有効化条件は成立。Lambdaの更新は行っていない。
- 修正: developブランチ環境変数に`NEXT_PUBLIC_LAW_RAG_ENABLED=true`、`NPM_CONFIG_INCLUDE=dev`を設定。既存変数を保持し、他ブランチとアプリ共通の環境変数が変わっていないことを読み戻し確認した。
- 再配信: job 63の採用版を固定してjob 64を開始。ビルドと実画面の結果を後述へ記録する。
- 結果: job 64は2026-10-09 23:05:16 JST開始、23:06:59 JST終了。BUILD / DEPLOY / VERIFYはすべて`SUCCEED`。実ログイン済みdevelopで「法令チャット」「プレリリース」のカードを確認し、「法令を調べる」から法令初期画面へ遷移した。質問例・対象外案内・法令向け入力欄を確認。今回は新規質問・評価投稿・履歴削除は行っていない。
- 画像: [developホーム](user-manual/images/29-law-home-develop.png)、[develop法令初期画面](user-manual/images/30-law-empty-develop.png)。マニュアルの図11-1 / 11-2をこの2画像へ更新した。その他の回答画像の撮影元は本記録で保持し、利用者本文にはブランチ名を記載しない。
- ローカル検証: フロント既存テスト46件成功。今回のクラウド設定変更による新規コード差分はなく、配信側でNext.jsビルド・型検査が成功したことも確認した。
- 参照: [npm include / omit](https://docs.npmjs.com/cli/v11/using-npm/config#include)、[Amplifyブランチ環境変数](https://docs.aws.amazon.com/amplify/latest/APIReference/API_Branch.html)。`NODE_ENV=production`下でもビルドに必要なdev依存をインストールするための設定として使用した。

## 7. dev全文補完の反映と直接Lambda統合検証

> 最終検証: 2026-10-14 — boto3で既存法令ソース・暗号化設定・CloudFormation差分を確認し、dev限定でSAM反映後に合成ユーザーの直接Lambda呼出しと件数ログを照合。

- ユーザーの「devで動かす」の指示に基づく試行。反映元は未マージの#177 `f80aee277fa41bc2ec59581b4ba69b9d6a3e3bb1`。当時のdevelop `20871803`を統合済みのソースであり、#177がdevelopへマージ済みという意味ではない。
- 事前確認では法令有効化とKB指定は成立していたが、全文補完用バケット設定は空だった。既存Managed KBコネクターから同一アカウントの資料バケットと`kb/egov/` prefixを照合した。既存バケットはAWS管理キー`alias/aws/s3`によるSSE-KMS。新しいKMSキー・バケット・KBの作成やデータ再同期は行っていない。
- `EleKnowledge-dev-phase2`の既存パラメーターを保持し、法令バケット名だけ設定した。変更セットはChatApi / ChatManagementFunction / RagApi / RagFunction / RagLambdaRoleのModify 5件、ReplacementはすべてFalse、Add / Removeなし。実行直前にも既存パラメーターが準備時から不変であることを確認した。適用後は`UPDATE_COMPLETE`。
- 合成ユーザーの法令質問1件を直接Lambdaへ送信し、HTTP相当200・FunctionErrorなし、所要10.18秒、responseType=pagesを確認した。出典10件のうち全文補完6件・部分4件、部分理由は`document_limit`、参照本文合計4,084文字。件数ログも一致した。1試行の結果であり、品質評価・p95測定ではない。
- 試験が作成した会話2行だけを所有者条件付きで削除した。通常ユーザーの会話は操作していない。DynamoDB Stream由来の合成試験アーカイブは削除していない。
- この確認は直接Lambda統合試験であり、Cognito / API Gateway / ブラウザを通るE2Eは未実施。既存の実画面・実アカウント確認を、この新しい反映版のE2E合格に読み替えない。本番環境は今回の反映対象外。
- 証跡は#177の検証報告と、実行端末の未追跡ローカル記録`law-runtime-verification-local.json` / `law-changeset-detail-local.json`に保持。共有文書にはアカウントID・実リソース識別子・質問/回答/引用全文・認証情報を含めない。
- 試行を停止する場合は、既存パラメーターを保持して`LawDataBucketName`を空にする変更セットの差分を確認して適用する。フロントの非表示だけをAPI停止とは扱わない。

この節だけを追加検証したため、文書全体のfrontmatter `last-verified`は進めていない。

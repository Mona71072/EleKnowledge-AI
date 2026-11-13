---
status: development
last-verified: 2026-10-22
related-code:
  - lambda/knowledge/common-knowledge/
  - infrastructure/sam/phase2-template.yaml
  - frontend/src/lib/common-knowledge.mjs
---

# 共通知識: itai専用AWS検証への引継ぎ

> 進捗（2026-10-22）: 本書の実行順1〜7を実施。分離スタック `EleKnowledge-itai-common-knowledge` を新規作成し（フラグoff・Git未設定）、配備版と合成受入の結果、未受入・費用・rollbackを[AWS基盤の実装契約と実施記録](common-knowledge-itai-aws-contract.md)へ記録した。手順8（push・Amplify接続切替）と、会社Git・実主体・実データの受入は未実施。以下の本文は開始時点の引継ぎとして残す。

> 最終検証: 2026-10-22 — ユーザーの次回AWS作成・デプロイへの追加指定、現在のローカル実装、Git祖先関係、GitHub MCPのリモートitai、既存T2/T23の境界を照合。今回AWSの現況確認・作成・デプロイは行っていない。

## 0. 最新の依頼と許可範囲

ユーザーは2026-10-22、次セッションで「AWSでの検証用itaiリソース作成に着手し、デプロイを進める」こと、および「itaiブランチへのマージを順次行う」ことを指定した。以前のローカルI1限定・AWS変更禁止は、**次セッションのitai専用検証リソース作成・デプロイについて更新された**。同じ範囲の許可を毎回取り直して設計だけで止まらず、対象確認・実装・検証・changeset確認後に進める。

| 対象 | 最新の扱い |
| --- | --- |
| ローカルitaiへの統合 | 許可あり。既存変更と祖先関係を確認し、今回の統合・I1・引継ぎを順にfast-forwardする。今後も検証した差分を判断可能な単位で順次統合 |
| 次セッションのAWS | 認証主体と対象を確認したitai専用検証リソースのIaC・アダプター実装、作成、デプロイ、合成データによる検証へ進める。既存リソースとの衝突・権限・変更内容を先に確認 |
| 共有dev / 本番 / develop / main / 他人のPR | 今回の許可に含めない。#195/#200の採用・担当合意やマージ可を代わりに宣言しない |
| itaiへのpush・Amplifyの接続切替 | ローカルマージとは別。受入前のpush・切替禁止を包括解除したとは扱わない。専用バックエンドと接続先・フラグ・自動配信の影響を揃えてから、必要な未承認操作だけ具体的に確認する |
| 新しい有料検索・モデル生成、実資料登録・KB同期、実データ公開 | 別の対象・有限枠・許可が必要。旧有料枠・消化済みスクリプトは再実行しない。インフラ作成の許可をモデル試験や全カード投入へ広げない |
| 削除・置換・権限拡大 | 無断で実施しない。共有リソース変更や破壊的差分が必要なら、その差分だけを分離して確認 |

## 1. 開始位置と既存成果

- 実装worktree: `.worktrees/domain-knowledge-i1-20261022`
- 実装元ブランチ: `feature/itai用語基礎知識I1統合`
- `ac46bc5f`: リモートitai `e70c1cd3`と#195 `08ba5eaa`、既存itai検証の必要なT17/T20等をローカル統合。
- `a9f1af9c`: 共通知識I1。候補3入口→共有一覧→編集→Git保存→特定版の別担当承認→正本反映→別操作公開→両AI読取→停止・復旧。
- 本書・再開プロンプトを含む引継ぎコミットは、上記の後にローカルitaiへ統合する。開始時に`git log`で最新SHAを取得し、保存時点へ戻さない。
- ローカルitai用worktree: `.worktrees/common-knowledge-itai-20261022`。作成・統合後の状態は後述の統合記録を確認する。
- リモートitaiは今回確認時点で`e70c1cd3097fad459a3b73f7135ee37e9dca1280`。ローカルマージ後もpushしていない。ブランチ名・ローカルHEAD・リモートHEAD・配備済みコードを同一視しない。

読む順:

1. 共有ルートの`AGENTS.md`。
2. 本書と[再開プロンプト](common-knowledge-itai-aws-resume-prompt.md)。
3. [I1実装契約](common-knowledge-i1-contract.md)、[統合記録・検証・担当・ローカル試行](common-knowledge-i1-integration.md)。
4. 設計worktree `.worktrees/domain-knowledge-design-20261021`の`docs/design-2026-10-01-knowhow-flywheel.md` §17。詳細設計と引継ぎ4文書は未コミットのまま保全されている。詳細設計の保存hashは`2d803b8c33375087341b0eb42471db1d99ef3f689e896f05a2e09704f60cd877`。#200のheadだけでは取得できない。
5. 既存検証worktree `.worktrees/senpai-itai-t01-20261021`のT2と、必要に応じてT4/T5・T23。記録は過去の状態であり、現況の代用にしない。私有原本・保存応答・大きいJSONを一括読込しない。

既存検証の基準は`d0f63a6f`。itai専用API・履歴・ジョブ・Managed KBの作成・試験が過去に進んでいるため、全て未作成だと仮定しない。共通知識I1向けの候補台帳・Git承認・公開manifestとは役割が異なる。既存のitai専用環境へ追加するか、追加の分離スタックにするかを、実在・所有・依存・更新影響から決める。

既存ローカルルートの27件、設計worktreeの4件の追跡変更は保全対象。今回のコード作業先にしない。`.worktrees/pr195-itai`も`itai`そのものではない。

## 2. AWS化で残っている実装

I1は合成経路が完成した段階であり、現状のファイルをそのままLambdaへ配置しても機能しない。

| 接点 | 現状 | 次の実装・検証 |
| --- | --- | --- |
| `Store` / `Service` | SQLite。Service内にも直接SQL・DB transactionがある | 単なるStore差替えで済ませず、候補・操作受付・イベント・冪等・ロック・一覧のドメイン操作へ境界を分け、DynamoDBの条件付き更新／transaction／Queryへ移植。強整合の再検証、GSI投影、TTL期限のAPI遮断を維持 |
| `LocalGit` | ローカルGit、operation付きcommit、特定版・同一単元treeを照合 | 会社承認の非公開Git用アダプター・path allowlist・認証・commit照合・競合／再開を実装。Lambdaの`/tmp`やローカルGitを永続正本にしない |
| `LocalDistribution` | 台帳と別のSQLiteへ不変artifact＋generation CAS | private S3等の不変artifactと条件付きmanifest更新へ移植。artifactのみ成功・公開後投影失敗・停止との競走・古い再試行を実AWSでも検証 |
| `app.py` | `SERVICE=None`、実アダプター未設定で503 | 設定検証・機能ゲート・実アダプターfactory・責任別Lambda／API配線を実装。未設定時は実行拒否。SQLiteや合成サーバーをAWSで起動しない |
| 認証／業務許可 | API Gateway claimsを前提、合成人物の許可表はローカル注入 | Cognito User Pool/JWT、admin閲覧と編集・承認・公開・読者を分離。テスト用の実主体へ限定して所管が許可する。ブラウザのskip-auth・`synthetic-*`トークンをクラウドで受け付けない |
| フロント | ローカル合成フラグ、実データの投稿／保存には受入待ちのガード、API URLはoriginのみ | HTTPSのstage/base path、実共有許可・根拠・保持・業務ロール設定、既存画面との共存を整合する。合成の根拠hash・180日・人物を実設定へコピーしない |
| 参照 | 共通公開読取と入力前・返答前の再照合を合成で検証 | RAG／開発エージェントの実接続を既定オフで実装し、未承認・停止・期限切れ・manifest不能・権限外の遮断を確認。生成の有料試験は別枠 |

Git承認先・認証・実ロール・保持・試行単元が未決でも、AWS棚卸し、分離した基盤・API、DynamoDB/S3アダプター、無効フラグと未設定時拒否の検証は進められる。Git必須経路の一往復まで完了したとは扱わず、実接続に必要な未決項目だけを具体化する。

## 3. 次セッションの実行順

1. **現状照合**: Git状態、ローカル／リモートitai、#195/#200のhead・コメントを確認する。AWSの認証主体・対象account/regionをローカルで確認し、既存itai stack・Lambda・API・DynamoDB・S3・Secrets参照・WAF関連・Amplify itai接続を必要な項目だけ読取する。秘密値や全環境変数を出力・追跡しない。
2. **差分を具体化**: 既存itaiと共有devの依存を区別し、今回の名前空間・stack・追加/更新リソース・IAM・推定固定費・停止フラグ・rollbackを実装契約へ先に記録する。古いT2生成物やsamconfigをそのまま再利用せず、現在値と明示差分を照合する。
3. **実装**: 上表の未実装を判断可能な増分で進める。新規共通知識リソースはitai専用へ分離し、Cognito/WAF等の共有物は参照し、共有devへの書込IAMを混ぜない。新しいKBや全カード投入を必須にしない。Secrets Managerは必要な実Git資格情報等に限定し、未決の秘密を生成して認証済みとしない。
4. **ローカル検証**: DynamoDB／S3／Gitアダプターの合成障害、関連API回帰、Lint・型検査・関連テスト、SAM変換／lintを行う。全カード検査や旧有料試験を一括再実行しない。S3の条件付き書込・DynamoDB transaction・API認可等の重要判断は現在の公式仕様か実測へ根拠を残す。
5. **作成・デプロイ**: 対象限定のSAM build/package、changeset作成→全ページの差分確認→実行へ進める。新規stackは全Add、既存itai更新は意図した変更だけで、共有物への変更・想定外のReplace/Delete・過大なIAMがないことを確認する。今回許可されたitai専用の非破壊的範囲なら、同じ許可を取り直さず続行する。範囲外の差分は実行しない。
6. **配備版検証**: stack完了、配備ソースhash、暗号化・公開ブロック・TLS・JWT/IP/WAF、最小権限を確認する。合成データだけで候補保存・再試行・版競合・公開／停止・他人分拒否を通し、未設定Git経路は拒否することを確認する。実主体やGit接続が未決なら、通過部分と未受入部分を分ける。
7. **itaiへ順次統合**: 合格した差分をコミットし、使用先・未コミット変更・祖先関係を確認してローカルitaiへ順次マージする。force-resetしない。基準SHA、採用commit、changeset、配備済みhash、設定移植、確認結果、rollbackを記録する。
8. **配信は別段階**: 専用API・HTTPS base path・認証・フラグが揃うまで既存Amplify itaiの接続先を切り替えずpushしない。必要になったら具体的な差分と自動配信への影響を提示し、その外部操作の許可を確認する。共有dev／develop／mainへ波及させない。

CloudFormationやSAMは、実行しただけでアプリ受入済みとはしない。基盤デプロイ、Gitを含む知識の一往復、実ブラウザ、実データの技術受入、有料RAG品質検証を別々に記録する。

## 4. 担当と残す判断

- **itai側で進める**: 対象確認、既存itaiとの統合、AWSアダプター、分離IaC・IAM・設定、デプロイ・合成受入、ローカルitaiへの順次統合、再開可能な証跡。
- **monaへの確認待ち**: #195への採用、UI/SAMとの分担・レビュー担当。未返答を引受けとしないが、ユーザーが許可したitai専用の実装・検証を一律停止しない。
- **共同／所管の判断待ち**: 会社Gitと認証、実業務ロール・兼務、原資料・読者・保持、実試行単元と技術確認者。合成基盤のデプロイ許可で代決しない。

完了報告には「実装・統合先SHA、実際に作成／更新したitai資源、changeset、配備hash、検証、未受入、費用が発生するもの、rollback、未実行のpush／切替／有料試験」を残す。アカウントID・内部URL・IP一覧・秘密参照の実値は未追跡のローカル記録に置く。

## 5. 今回のローカル統合記録

ユーザーの明示依頼に基づき、未使用・祖先関係を確認したローカルitai用worktree `.worktrees/common-knowledge-itai-20261022` を作成した。旧local itai `3c9e89a3`→確認済みremote基準`e70c1cd3`→統合`ac46bc5f`→I1実装`a9f1af9c`の順で、各fast-forwardの成功を確認した。続けて今回の引継ぎコミットをfast-forwardする。既存変更を捨てる操作や履歴の書換えは行っていない。

実際の到達SHA・作業ツリー・remoteとの差分は、完了時の`git log/status/rev-list`で確認する。今回の追加作業は引継ぎ文書とローカル統合であり、I1の既存検証161件／フロント185件を再実行したとは記載しない。文書リンク・コードフェンス・diff checkと、祖先・競合なしを検証する。

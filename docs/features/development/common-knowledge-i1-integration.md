---
status: development
last-verified: 2026-10-22
related-code:
  - lambda/knowledge/common-knowledge/
  - scripts/knowledge/run-common-knowledge-local.py
  - frontend/src/components/knowledge/common-knowledge-inbox.tsx
  - tests/integration/test_common_knowledge_i1.py
---

# 共通知識I1: itai向けローカル統合・担当・試行

> 最終検証: 2026-10-22 — 指定された未コミット設計、GitHub MCPのPR head・コメント、ローカルの共通祖先、合成コード・永続保存・画面操作を照合。会社Git/AWS・実アカウント・実資料・実モデルの受入記録ではない。

## 作業先と保全

- 専用worktree: `.worktrees/domain-knowledge-i1-20261022`
- ローカルブランチ: `feature/itai用語基礎知識I1統合`
- 起点: 最新リモートitai `e70c1cd3097fad459a3b73f7135ee37e9dca1280`。GitHub MCPでbranchのcommitを確認し、同じローカルオブジェクトを使用した。CLI認証が使えないためfetchは行っていない。
- ローカル統合コミット: `ac46bc5f`（親: `e70c1cd3` / `08ba5eaa`）。共有ブランチ・PRのマージではない。
- 古いローカル`itai`（`3c9e89a3`、remoteより359コミット遅れ）は切り替えず、最新itai基準の専用ブランチで試行する。受入前の配信先切替を避け、`itai`・`mona`・`develop`・リモートrefは更新していない。
- ルートと既存の設計／検証worktreeには編集していない。設計4文書の未コミット差分は隣接するローカル証跡ディレクトリへpatchで保全し、詳細設計のSHA256 `2d803b8c33375087341b0eb42471db1d99ef3f689e896f05a2e09704f60cd877`が開始時と同じことを確認した。

方針の正本は指定された設計worktreeのノウハウ設計§17・引継ぎ§8/9。実装用の選択と受入条件だけを[共通知識I1契約](common-knowledge-i1-contract.md)へまとめた。#200の方針本文や未コミット設計全体を実装へコピーしていない。

## 統合元と競合の扱い

| 統合元 | 対象・採用した内容 | 競合／残した範囲 |
| --- | --- | --- |
| #195 / mona `08ba5eaa` | 現場報告API・画面、先輩チャットの開閉・引用表示、調査ジョブ、SAM、共通契約・サンプル・依存lock | 最新itaiとの共通祖先は`9e499768`、分岐は45/36コミット。既存変更をローカル統合し、カード群を再分類・再承認しない |
| itai検証 `d0f63a6f` | `senpai_research_*`の有限予算・論点別十分性・grounding・原文引用、出典アダプター、開発表示、合成サンプルと対応テスト | monaとの共通祖先`1b75a183`から必要なコード・契約を三者比較。既存worktree一式を上書きコピーしない |
| T17 `ccd3dcc3` / T20 `152c2281` | ノウハウ候補の交互集約、未支持の法令論点の生成拒否、引用の文末補完、内部指示ガード | monaの待ち時間制限・リンク除去・引用なし回答の拒否も維持。時間不足は意味検証済みと呼ばず資料一覧へ退避 |
| itai側の既存アダプター | `knowhow_retrieval.py`の候補上限引数・release/hash/版を検証するManaged読取契約、`app.py`の明示backend選択 | monaの正規化スコア・無関係質問の閾値・キャッシュを保った。既定local。Managed KBを作成・有効化していない |
| 新規I1 | 共通候補台帳、Git作業版・特定版承認、別操作公開、共通読取・停止、管理画面接続、ローカル合成サーバー | 既定オフ。既存のnavigation_only索引と本人向け現場報告を変更しない。新機能のSAMルート・IAM・リソース配線は未実施 |

RAG本体の競合はLF/CRLFを揃えた三者比較で解消した。`knowhow_retrieval.py`はmonaのスコア方式を残して候補上限を追加した。調査ジョブはT17の計画90秒・予約45秒・ワーカー180秒・ロック330秒へ揃え、monaのSDK待ち時間制限を維持し、自動再試行は1試行に固定した。これらはローカルSAM差分で、AWSへ適用していない。

JS/Python間では、統合ワーカーから合成サンプルを再生成した。架空のT9を含む生成例は引用置換となるため、画面・履歴側でも未使用のK参照をusedとして表示しない。#195の表示仕様とT17/T20の根拠判定を両方反映した結果であり、私有応答の再生・新規有料試験ではない。

既存の実測スクリプト・予算枠・実環境用Managed KBテンプレート・原本／保存応答は統合試験に使用していない。T21の技術出典選別保留、T22の技術内容・原本版の受入も解決済みとはしていない。

## itai側で担った実装と確認待ち

| 担当 | 今回具体化した範囲 | 次に必要な確認 |
| --- | --- | --- |
| itai側 | 共通契約、API認可、共有許可、Git保存・版競合・技術承認・公開／停止、画面接続、永続復旧、合成検証、#195/T17/T20のローカル統合 | 実装差分の採用先・担当の合意。実データの技術承認とは別 |
| mona側の既存成果 | #195の画面・SAM・調査ジョブの既存実装を保全して参照・統合 | 新しい仕事を引き受けたとはしていない。共通インボックスのUI/SAM差分をレビューする担当を確認したい |
| mona/itai共同 | 方針とローカルI1を分け、実データ接続前の未決事項を整理 | #195へ採用するか、会社承認Git・認証、保持、分野と読者、実業務ロール、兼務、試行単元と技術確認者の決定 |

2026-10-22のGitHub MCP確認時点で、[#195](https://github.com/yukiworkspace/EleKnowledge-AI/pull/195) headは`08ba5eaa`、[#200](https://github.com/yukiworkspace/EleKnowledge-AI/pull/200)はDraftの`4a9a6558`。終了前にもheadとコメントを再確認し、#200の方向性Yesの後、実装統合・担当重複への追加返答はない。Yesをmonaの引受け、製品受入、配備・マージ可へ読み替えていない。GitHubへ投稿していない。

相手への確認文案（未送信）:

> @Mona-mebs itai側で、最新itai＋#195の画面・SAMとT17/T20を専用ブランチへローカル統合し、共通知識I1の投函・Git保存・別担当の技術承認・別操作公開・共通読取・停止を合成で確認しました。Yes/No: このI1のコード・テスト・実装契約を#195へ採用する方針でよいですか？ itai側で共通台帳・認可・Git／公開・合成検証を担当し、mona側には既存UI/SAMとの接続レビューをお願いする分担でよいですか？ 同じ箇所を修正中なら対象ファイル／commitを教えてください。採用・レビューの合意と、配備・マージ可は別です。

## ローカル試行

専用worktree内で操作する。実資料・実アカウントは使わない。Pythonサーバーは標準ライブラリのみで動き、AWS・会社Git・検索・モデルを呼ばない。

ターミナル1（リポジトリルート）:

```powershell
Set-Location .worktrees/domain-knowledge-i1-20261022
python -X utf8 scripts/knowledge/run-common-knowledge-local.py --enable-synthetic
```

保存先の既定はOS一時領域の`eleknowledge-common-i1`。台帳、配布ストア、専用ローカルGitを保持するので、サーバーを止めて起動し直しても残る。別の合成試行には`--data-dir <repo外の専用ディレクトリ>`を指定する。起動フラグなしでは実行拒否。repo配下を本文保存先へ指定できない。

ターミナル2（同じworktreeのfrontend）:

```powershell
Set-Location .worktrees/domain-knowledge-i1-20261022/frontend
npm.cmd ci --ignore-scripts
$env:NEXT_PUBLIC_SKIP_AUTH='true'
$env:NEXT_PUBLIC_DEV_ADMIN='true'
$env:NEXT_PUBLIC_ENABLE_COMMON_KNOWLEDGE='true'
$env:NEXT_PUBLIC_COMMON_KNOWLEDGE_SYNTHETIC='true'
$env:NEXT_PUBLIC_COMMON_KNOWLEDGE_API_URL='http://127.0.0.1:8765'
npm.cmd run dev -- --hostname localhost --port 3000
```

`http://localhost:3000/admin/knowledge`を開く。合成人物を「投稿本人→編集担当→技術確認者→公開担当」と切り替え、現場報告・不明用語を投函して保存・承認・公開する。読者と開発エージェントは同じ公開ID・版・hashを読む。訂正は既存単元の承認版を指定して次版を作り、既存公開世代を確認して公開する。停止後は次の読取がNotPublishedになる。

共有一覧は状態を選んで取得する。操作理由は必須。保存はGit commitが返ったときだけ完了、技術承認後も公開前は未配布。APIが権限を判定するので、閲覧だけのadminによる変更は403になる。

応答喪失時は同じ操作者で「自分の未完了操作を取得」→「同じ操作IDから再開」。保存した要求をサーバーで再認可し、Git commitや公開CASを照合する。古い公開が停止後の世代を復活させることはない。キーを変えて同じ対象を無理に上書きしない。

## 検証と限界

関連テストは合成だけで実行する。`tests/unit`全件や全カード検査は、今回不要な資料・既存検証まで読み込むため一括再実行しない。

- 新規I1: API・SQLite再起動・ローカルGit・別配布ストアの統合／否定テスト。3入口、旧公開版保持、本人／業務権限、確認hash、版競合、冪等、保存・投影障害、公開と停止の競走、期限・根拠許可失効、Git別編集、cursor改変、操作ID復旧を確認。
- 画面: 実際のTSXハンドラー→HTTP→Python API→永続保存を合成3入口で実行。React state境界はテストハーネスで置換し、実ブラウザの見た目・Cognito実アカウント操作とは区別する。
- 既存回帰: 先輩調査ジョブ、根拠判定・原文引用、JS/Python応答サンプル、現場報告、まとめの関連テスト。通常RAG／全資料の製品受入ではない。
- 検証結果: 共通知識I1統合16件、既存の調査・出典関連145件（関連セット計161件）成功。別途、現場報告・まとめ・ジョブAPI／保存・検索スコア等も対象を分けて回帰した。重複する件数は合算しない。
- フロントの関連185件成功。ここには合成3入口を通す実TSXハンドラー＋HTTPのE2Eが1件含まれる。`npm ci --ignore-scripts --no-audit --no-fund`でlockどおりの専用依存を導入して再確認し、既存worktreeの依存は変更していない。package.json／lockに新規差分なし。
- 型検査成功、Lintはエラー0・既存画面の警告4件。cfn-lint 1.52.1は終了0。SAM validate --lintもテンプレートをvalidと判定し終了0だったが、端末のグローバルmetadataへのアクセス警告が出た。端末設定を上書きしていない。`git diff --check`も確認した。

実未検証: 会社Git・サービス認証・DynamoDB/S3実アダプター、保持・バックアップ、実アカウントのロール割当、原資料の技術内容、実モデル・検索、新機能のAWS/IAM配線、実ブラウザ、配信先切替。新機能のLambdaは実アダプター未設定で503となり、合成認証をAWSで有効化する設定はない。

次の外部操作は、差分受入後の#195採用／担当合意、実保存先・保持・業務権限・試行単元の決定、その後に別許可を受けた実環境接続。今回push、PR操作、共有dev変更、デプロイ、KB登録・同期、有料実測、既存データ削除は行っていない。

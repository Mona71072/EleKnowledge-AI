---
status: draft
last-verified: 2026-10-30
related-code:
  - infrastructure/sam/phase2-template.yaml
  - amplify.yml
  - lambda/rag/rag-function/senpai_research_*.py
---

# PR #195 統合準備記録

## HEADと統合結果

2026-10-30にupstreamを読み直した。開始時のPR #195 HEADは`4a250c108aa4b1200340105397c4e87f7dee8197`、developは`58ccea2f21baa246627a110825a5832e55396bc7`、共通祖先は`cc47087235f807a3d4083945f770a6d31524e495`。`git rev-list --left-right --count origin/develop...origin/mona`は`26 99`だった。

PR HEADを保持し、別worktreeの`codex/pr195-develop-integration`上でdevelopをno-ff統合した。自動競合はなく、develop側の31ファイル変更（1,581行追加、118行削除）が統合された。ローカル統合コミットは`4bc2343`。これは検証用であり、レビュー受入・AWS適用・マージを意味しない。

| 優先確認 | 統合後の内容 | 判断 |
|---|---|---|
| AIルール | AGENTS.mdはv1.3.13。配布資料デザインへの参照を追加 | 適用する。PRの処理・認可規則と衝突なし |
| frontend依存 | Next.js / eslint-config-next 16.4.1、Zod 4.6.7を含むlockfile | PR側の古い依存差分を残さずdevelop版を保持。`npm ci`と全依存監査を確認 |
| Phase 2 SAM | developのEnvタグ削除とPRのKnowhow/先輩API・条件付き関数が統合 | PRで必要なパラメータ・経路・IAM定義は統合後も残る。新機能フラグの既定はfalse。cfn-lintは対象Phase 2で成功 |
| Amplify | PR元は`NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH=true` | 共有devで未受入機能が見えるためfalseへ変更し、回帰テストを追加。これは設定ファイルの修正で、配信変更は実施していない |
| API・認証 | Phase 2 APIのCognito Authorizerが既定。調査APIはJWT `sub`をowner IDに使い、状態取得時にも所有者を照合 | ローカル契約テストで確認。実Cognito・ブラウザE2Eは未検証 |
| #203セキュリティ修正 | merged developのpackage/lockfileを統合結果に保持 | Zod 4.6.7とNext.js 16.4.1を確認。npmの全依存監査0件 |

統合時のルート差分は実際のPR変更範囲と混同しない。PRの変更ファイル2,425件を共通祖先から分類した内訳は次のとおり。

| 分類 | 件数 |
|---|---:|
| source snapshot | 1,130 |
| draft | 635 |
| Knowledge Card / card index | 402 |
| program・frontend・Lambda・script・SAM | 119 |
| test・test fixture | 75 |
| docs | 15 |
| その他の設定・manifest | 49 |
| 合計 | 2,425 |

ランタイム検索は明示的なKnowledge Card indexを読む。source snapshotとdraftをランタイム用indexへ一括投入する変更ではない。コード・SAM・フロント・テストは同一契約に結び付き、一括変更の検証を要する。docsは独立整理できる。snapshot/draftの移動や分割は、出典参照・カードhash・index manifestを再検証し、知識データの担当承認を得てから行う。機密性と個人情報についてはファイル数だけでは判断できないため、公開前に分類者による本文レビューを別途完了する。

## レビュー・既存指摘

PR上の2件のレビュー指摘スレッドはともにResolvedだが、2026-10-30時点でも元の`CHANGES_REQUESTED`レビューは残る。以下は最新PR実装とローカル統合後の検証範囲であり、レビュアーによる再承認ではない。

| 指摘・境界 | 最新HEADでの確認 | 残る確認 |
|---|---|---|
| Windows CRLFによるhashずれ | `.gitattributes`が`knowledge/cards/** eol=lf`。統合後のカードbuild checkで398/398 valid | Windows実機checkoutは未実施 |
| 期限切れ・削除済みデータ再公開 | hidden winner rowの再取得テストと調査結果TTL論理判定を追加。`get_job`は期限切れを隠す | AWSのTTL物理削除タイミング実測は未実施 |
| 条件付き書込み・60秒lease | stale leaseのみ条件付き回収、in-flight duplicateは409、所有者付き解放。SAM API timeoutは15秒 | 実DynamoDBでの並行実行負荷・多重起動試験は未実施 |
| 所有者・相談ID分離 | jobはJWT `sub`のユーザーキーに保存し、status取得はownerを再照合 | 実Cognito・他利用者の実セッションを使うE2Eは未実施 |

## T17/T20/T21/T22 の公開証拠

元のT17 commit `ccd3dcc3` とT20 commit `152c2281`、T22 `b3b17f7c`は公開GitHubまたは取得済みGit objectとしては確認できない。未push差分を推定・再構成しない。

| 項目 | #195採用状態 | 取得できた証拠・不足 |
|---|---|---|
| T17 | 未採用。法令資料なしの回答保留は部分的に重複実装 | `origin/itai`の派生統合commit [`ac46bc5`](https://github.com/yukiworkspace/EleKnowledge-AI/commit/ac46bc5f06369e726f7ecd20d548132f3267ca16)にgrounding/claim関連実装。元commitは取得不可。派生branch実装と#195は同一ではない |
| T20 | 未採用 | 同派生commitに内部指示と原文引用を扱う実装がある。`#195`へ採用する検証・承認なし |
| T21 | 未採用・保留 | #195は技術資料を全体score順で10件に制限。以前の観察で有力候補が全体順位12位になった記録があるが、同一評価セットで代替配分を比較した現在のデータなし |
| T22 | 採用・検証とも未完 | PRコメントの観察記録はあるが、原本と保存応答は取得できず、技術内容・版の受入を再現できない |

## 知識承認・共有devの安全境界

#200の方針は、開発中のGit正本、運用開始時のS3正本、キーマンの内容承認、管理者によるapproved保存・公開を分ける。この#195実装にapproved保存・公開APIは見つからない。workbenchのexportは`publishable: false`かつdraftにする。RAG LambdaはS3の指定indexを読むが、承認者・管理者向けのS3書込み経路は含まない。approvedというcard statusだけで権威・公開を意味させてはならない。したがって「非管理者がapprovedへ最終追加できる」経路は確認されていない一方、キーマン承認と管理者公開を実現する機能も未実装である。

共有devのAmplify設定はKnowledge Workbenchをoffとする。SAMの`KnowhowEnabled`、`SenpaiSynthesisEnabled`、`SenpaiFieldReportsEnabled`、`SenpaiResearchEnabled`もdefault falseで、各関数・ルートはdev条件と明示フラグを要求する。S3への正本切替、権限変更、KB同期は本段階で行わない。

## 受入・マージ判定

| 受入単位 | 自動確認 | 業務・運用受入 | 判定 |
|---|---|---|---|
| PR統合・依存 | Python/frontend CI、lint、audit、typecheck、build、カードindex check | 統合後PRを最新HEADで再レビュー | 自動CI合格は確認後も必要条件にすぎない |
| 先輩チャットUI/API | feature flag・JWT・所有者テスト | dev環境でadminと非adminを使うE2E | 未実施 |
| 調査ジョブ | TTL、条件付きwrite、lease、再送・owner単体/合成DynamoDB試験 | 費用上限、同時実行、復旧を実環境で確認 | 未実施 |
| RAG回答 | 30件合成評価器の構造・計算テスト | 承認済み資料を2名以上で採点し、重大失敗と根拠を確認 | 実業務正答率は未測定 |
| Knowhow統合 | card hash・scope・明示index検証 | #200に沿う承認者/管理者ワークフロー | 未実装・未受入 |
| AWS/IaC | cfn-lint Phase 2 | AWS change setのRemove/Replace/IAM/parametersを読み取り確認 | SAM CLI/AWS実査なし。適用禁止状態を維持 |

次のマージ判断には、最新HEADのCI、変更要求レビューの解消、新しいHEADを対象にした再レビュー、30件評価セットの人手採点方法確定、管理機能の認可方針、共有devの実配信確認が必要である。今回PRのマージ・AWS適用・KB同期はしていない。

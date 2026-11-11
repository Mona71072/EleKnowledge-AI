---
status: draft
last-verified: 2026-10-22
related-code: []
---

# 用語・基礎知識: S3正本実装への整合と統合の引継ぎ

> 最終検証: 2026-11-11 — #200の11/5決定コメント、構想・設計・specの反映内容、既存itai実装契約への参照関係を照合。AWS・ブラウザ試験は再実施していない。

方針は[初期構想](../../concept-2026-10-21-product-domain-knowledge.md)、ノウハウ共通方針の改訂は[設計§17](../../design-2026-10-01-knowhow-flywheel.md#17-2026-10-22以降の改訂-s3正本と業務権限)へ集約する。実装仕様・受入の正本はitaiブランチの[実装契約](https://github.com/yukiworkspace/EleKnowledge-AI/blob/b9076cbd/docs/features/development/common-knowledge-itai-aws-contract.md)。このPRへコード・テスト・配備記録本文を複製しない。

## 現在の参照点と反映先

> 最終検証: 2026-11-11 — #200のPR状態・決定コメントと文書内の参照関係を照合。itai実装の現head・AWS状態は未実査。

| 対象 | 確認結果 |
| --- | --- |
| #195 | 先輩チャット・調査ジョブ・画面・SAMの実装PR。共通知識（二段階承認等）はmonaの2026-11-05決定により含めない。レビュー・headは作業再開時に再取得 |
| itai専用実装 | S3正本・認可表・専用AWS/Amplifyの実装契約と実施記録がある。参照コミットb9076cbdは履歴上の照合点で、現head・未コミット差分・AWS状態は作業再開時に確認 |
| #200 | 方針・決定記録のみの共同確認PR。monaの2026-11-05業務判断を構想書へ記録し、AWS変更・KB同期・実データ登録は含めない |
| 古いローカル設計 | domain-knowledge-design-20261021 worktreeの未コミット文書は保全。Git正本・admin所属の旧案は採用せず、共有環境のadmin識別案は「暫定」として扱う |

monaは当初、実装の統合先を#195とする方針にYesと回答したが、2026-11-05に共通知識（二段階承認等）は#195へ含めず別PRにする決定へ更新した。根拠判定・引用修正はitai、画面・SAMはmona中心という[分担回答](https://github.com/yukiworkspace/EleKnowledge-AI/pull/195#issuecomment-6328400429)は対象機能ごとの技術分担として参照する。共通知識の業務試行・実装は別に扱い、#195へ再統合しない。

2026-11-05の決定は[構想書の決定記録](../../concept-2026-10-21-product-domain-knowledge.md#2026-11-05-開発試行の業務判断)を参照する。確定事項はBK系1単元からの試行、開発中のmona・itaiによる内容確認・承認と限定読者、保持の暫定値、itai担当のGit→S3移行、既存承認記録を引き継がないこと。管理者識別・停止権限は未確認の暫定案。試行単元の具体的なID・範囲・根拠資料・選定理由は実データ登録前に特定し、特定できなければ登録を止める。

## 現行契約と接点

| 項目 | 現行itai実装と次の確認 |
| --- | --- |
| 保存 | itai検証はS3正本。業務用は開発中Git正本、運用開始時に移行照合後S3へ切替。内容承認とapproved保存を分離する改修が必要 |
| 認可 | itai検証は非adminでもapproved保存可。最新方針ではキーマンの内容承認と、管理者だけのapproved保存・公開を分離する。JWT本人と業務権限・分野・読者・期限の検証は維持 |
| API・UI | lambda/knowledge/common-knowledge/、frontend/src/components/knowledge/common-knowledge-inbox.tsx、/knowledge/meで権限表示。既存の先輩チャットadmin制限は別 |
| IaC | itaiのinfrastructure/sam/common-knowledge-itai-template.yaml。2表、作業用／正本S3、責任別API/Lambda/IAM、Cognito・WAF参照 |
| 開発エージェント | 作業用だけ直接書込。CLIの登録・確認依頼等と、API専用の承認・公開・停止を区別。知識利用は公開manifest検証経由 |
| 検索 | publishedにKB向けmetadataを用意。KB作成・同期、本番RAG／開発エージェント実接続・品質受入は未完了 |

## 検証結果と残作業

itaiの実施記録は合成13シナリオ、2アカウントの投函→編集→差し戻し→再依頼→承認→公開→読取→停止と台帳・S3照合を報告している。今回その実施を再実行したものではない。mona向け公開・停止の[確認手順](https://github.com/yukiworkspace/EleKnowledge-AI/blob/b9076cbd/docs/features/development/common-knowledge-itai-mona-check.md)への返答も別途確認する。

未受入: CLI作業版登録の実配備一往復、KB作成・同期、IP外拒否の実査、実データ・保持方針、キーマン向け専用編集画面、実業務の権限・読者・対象単元。未知用語の自動収集・根拠検索・草案生成を共通保存経路の完成と同一視しない。

## 次回の順序

> 最終検証: 2026-11-11 — #200の未決事項とmonaが指定した担当・開始条件を照合。

1. AGENTS.md、#200の最新コメント、構想書の決定記録を確認し、具体的なBK単元・根拠・登録許可を確定する。既存worktreeや未コミット差分を上書きしない。
2. 実装へ進む前に、itai契約と現head・未コミット差分を比較し、暫定のadmin識別・停止権限、公開版無期限・草案60日の保持をmonaが確認する。未確認なら共有環境・実データへ適用しない。
3. 新規受入をする場合は版競合、権限なし、内容承認だけではapprovedが作られないこと、管理者の最終追加・公開、内容変更後の再承認、非adminの最終追加・公開拒否（API直呼び・再試行を含む）、未承認／停止／期限切れ読取拒否、部分失敗復旧、個人チャット分離を確認する。Git→S3の全カード移行は1単元試行後・運用開始直前にitaiが担当し、運用開始日は別途決める。
4. 共通知識の方針PR、実装PR、AWS実行許可を分ける。#195へ共通知識を加えない。文書・方針の確認やマージをAWS変更・KB同期・実データ登録の許可と解釈しない。

## 2026-10-23のクラウド確認と次の統合条件

> 最終検証: 2026-10-23 — GitHubの参照点・コメント・コミット取得結果を照合。AWS・ブラウザ未実施。

- origin/itaiはb9076cbd、#195はd0dd0397。T17のccd3dcc3とT20の152c2281はGitHubに存在せず取得不可（APIがNo commit foundを返却）。ローカル修正を再現した推測コードで置き換えず、push済み参照かpatchを取得後、d504d9d・daa1c8c上で統合する。
- 方針の根拠判定はitai優先、monaの役割・説明の統合・意図別形式・understanding受渡しは保持する。コード未取得のため統合済みとはしない。
- 共通知識の移行は[切替手順案](../../concept-2026-10-21-product-domain-knowledge.md#gitからs3への切替手順案)で確認する。Gitの全カードを自動でapprovedへ入れる経路は作らない。
- itai専用のAPI・Amplify接続値を共有devへ移植せず、#195の採用範囲・機能フラグ・環境別設定を先に確定する。二段階承認の実装は#195、共同方針は#200に分ける（当時の方針。2026-11-05のmona決定で、共通知識の実装は#195に含めず別PRへ変更）。

---
status: draft
last-verified: 2026-10-22
related-code: []
---

# 用語・基礎知識: S3正本実装への整合と統合の引継ぎ

> 最終検証: 2026-10-22 — #195/#200のhead・全会話、origin/itai b9076cbdの実装契約・S3アダプター・認可・SAMを静的照合。AWS・ブラウザ試験は今回再実施していない。

方針は[初期構想](../../concept-2026-10-21-product-domain-knowledge.md)、ノウハウ共通方針の改訂は[設計§17](../../design-2026-10-01-knowhow-flywheel.md#17-2026-10-22の改訂-s3正本と業務権限)へ集約する。実装仕様・受入の正本はitaiブランチの[実装契約](https://github.com/yukiworkspace/EleKnowledge-AI/blob/b9076cbd/docs/features/development/common-knowledge-itai-aws-contract.md)。このPRへコード・テスト・配備記録本文を複製しない。

## 現在の参照点と反映先

| 対象 | 確認結果 |
| --- | --- |
| #195 | head d0dd0397。monaの先輩チャット・調査ジョブ・画面・SAM。itai専用の共通知識変更は未取込 |
| origin/itai | b9076cbd。共通知識のS3正本・業務権限と専用AWS・Amplify itaiの実施記録あり |
| #200 | 文書専用Draft。最新回答に合わせ、開発中Git正本／運用開始時S3切替と二段階承認を記載。移行案を追加 |
| 古いローカル設計 | domain-knowledge-design-20261021 worktreeの未コミット4文書は保全。古いGit/admin案や「統合先未返答」を次回指示として使わない |

monaは[統合先を#195とする方針にYes](https://github.com/yukiworkspace/EleKnowledge-AI/pull/200#issuecomment-6328353993)。根拠判定・引用修正はitai、画面・SAMはmona中心という[分担回答](https://github.com/yukiworkspace/EleKnowledge-AI/pull/195#issuecomment-6328400429)がある。共通知識の採用差分・今回の完成範囲・担当は別途突き合わせる。#195全体のマージや共有dev反映を代行して決めない。

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

1. AGENTS.md、#195/#200の最新コメント、itaiの最新headと未コミット差分を確認する。既存worktreeを上書きしない。
2. itai契約のS3正本化・実施記録・SAMとmona headを比較し、#195へ渡すコード・テスト・実装仕様だけを具体化する。非admin内容承認ではS3 approvedへ書けず、管理者の最終追加だけが書ける二段階方式を実装前に契約へ記載する。既存の承認処理と失敗復旧からの迂回も防ぐ。調査ジョブの根拠判定をitai優先、monaの回答指示・画面変更を保つ統合方針への返答を確認する。
3. 新規受入では版競合、権限なし、キーマン内容承認ではapproved未作成、管理者の最終追加・公開、内容変更後の再承認、非adminの最終追加・公開拒否（API直呼び・再試行を含む）、未承認／停止／期限切れ読取拒否、部分失敗復旧、個人チャット分離を確認する。
4. 共有方針の共同確認・実データ／権限割当・保持・公開範囲と、マージ／AWS実行許可を分ける。今回の文書修正でAWSやKBを変更しない。

## 2026-10-23のクラウド確認と次の統合条件

> 最終検証: 2026-10-23 — GitHubの参照点・コメント・コミット取得結果を照合。AWS・ブラウザ未実施。

- origin/itaiはb9076cbd、#195はd0dd0397。T17のccd3dcc3とT20の152c2281はGitHubに存在せず取得不可（APIがNo commit foundを返却）。ローカル修正を再現した推測コードで置き換えず、push済み参照かpatchを取得後、d504d9d・daa1c8c上で統合する。
- 方針の根拠判定はitai優先、monaの役割・説明の統合・意図別形式・understanding受渡しは保持する。コード未取得のため統合済みとはしない。
- 共通知識の移行は[切替手順案](../../concept-2026-10-21-product-domain-knowledge.md#gitからs3への切替手順案)で確認する。Gitの全カードを自動でapprovedへ入れる経路は作らない。
- itai専用のAPI・Amplify接続値を共有devへ移植せず、#195の採用範囲・機能フラグ・環境別設定を先に確定する。二段階承認の実装は#195、共同方針は#200に分ける。

---
status: development
last-verified: 2026-10-22
related-code:
  - lambda/knowledge/common-knowledge/
  - infrastructure/sam/phase2-template.yaml
---

# 再開プロンプト: 共通知識のitai専用AWS検証・デプロイ

> 最終検証: 2026-10-22 — 最新ユーザー依頼、I1の実装境界、未コミット設計、itai統合と配信の区別を引継ぎへ対応付けた。

次の本文を新セッションへ渡す。

```text
EleKnowledge-AIの共通知識（ノウハウ＋用語・基礎知識）を、itai専用AWS環境で検証・デプロイする作業を進めてください。

まず共有ルートAGENTS.mdを読み、.worktrees/domain-knowledge-i1-20261022 の以下を読んでください。
- docs/features/development/common-knowledge-itai-aws-handoff.md（今回の許可・AWS化の不足・実行順・itai統合）
- docs/features/development/common-knowledge-i1-contract.md
- docs/features/development/common-knowledge-i1-integration.md
ローカルitai用worktreeは .worktrees/common-knowledge-itai-20261022 です。開始時にgit status/log/worktree listとローカル・リモートitaiを再確認してください。

詳細設計§17は .worktrees/domain-knowledge-design-20261021/docs/design-2026-10-01-knowhow-flywheel.md の未コミット差分だけにあります。
同worktreeの引継ぎ§0/8/9も必要に応じて参照し、設計4文書の未コミット変更を保全してください。設計worktreeはsparse・detachedで、実装先に流用しないでください。
前回の統合はac46bc5f、I1実装はa9f1af9cです。今回の引継ぎコミットまでローカルitaiへ順次fast-forwardするため、最新SHAは実際のlogから取得してください。
古い3c9e89a3や保存時点のheadへ戻さず、force-reset・cleanを行わないでください。ルートと他worktreeの作業を上書きしないでください。

ユーザーは2026-10-22に、次セッションの「AWSでの検証用itaiリソース作成に着手し、デプロイを進める」ことと「itaiブランチへの順次マージ」を明示しました。
以前のローカルI1限定・AWS変更禁止は、このitai専用検証リソース作成・デプロイの範囲で更新されています。
同じ範囲の許可を繰り返し求めて設計だけで止まらず、対象確認・実装・ローカル検証・具体的changeset確認後に、許可された非破壊的なitai専用作成／更新とデプロイまで進めてください。
共有dev・本番・develop/main・他人のPRの変更、破壊的置換・削除、新規の有料検索／モデル試験・元資料登録／KB同期／実データ公開は含みません。
ローカルitaiへのマージと、push・Amplify接続切替は別です。受入前のpush／切替禁止は包括解除されていません。

最初にAWS認証主体・対象account/region、既存itai stack/API/Lambda/表/S3/Secrets参照/WAF関連、Amplify itaiの接続先と自動配信を必要項目だけ読取確認してください。
既存検証 .worktrees/senpai-itai-t01-20261021（基準d0f63a6f）のT2/T4/T5等の記録を参照し、既存itai資源を重複作成しないでください。
古いsnapshotや生成SAMの設定を黙って再利用せず、現在値と明示差分を照合してください。全環境変数・秘密値・大きいJSON・私有本文を出力／追跡しないでください。
#195/#200の最新head・コメントも確認し、monaの未返答を採用・担当引受け・マージ可へ読み替えないでください。外部へのコメント投稿は行わないでください。

I1は合成経路の完成で、AWSアダプターは未実装です。
Service内に直接SQLがあるため、SQLiteのStoreを名前だけ差し替えてDynamoDB対応済みにしないでください。
候補・操作受付・冪等・版競合・イベント・一覧をドメイン操作へ分け、DynamoDB transaction/条件付き更新/Queryと強整合再検証へ移植してください。
LocalDistributionは台帳と別の永続ストアです。不変artifact・manifest CAS・公開後投影失敗・停止との競走・古い公開の再試行をS3等の実アダプターでも維持してください。
LocalGitやLambdaの/tmpを永続Git正本にせず、会社承認Gitの認証・path・commit照合・復旧を実装してください。未設定ならGit必須操作を拒否してください。
app.pyのSERVICE=None、実アダプターfactory、機能フラグ、責任別API/Lambda/IAM、HTTPS stage/base path、実共有許可・根拠・保持・業務ロールの未実装も解消対象です。
ローカル用skip-auth・synthetic-*トークン・合成の根拠hash／人物／保持値をクラウドの実権限や実データへコピーしないでください。

会社Git・実ロール・保持・実単元が未決でも、分離した基盤・API・DynamoDB/S3・無効フラグ・未設定拒否の作成と検証は進められます。
未決を固定値で埋めず、実接続が必要になる箇所だけ判断待ちにし、基盤デプロイと知識の一往復・実データ受入を区別してください。
機種・資料・利用者等の業務対象を自動追加／除外しないでください。新KBや全カード投入を今回の必須条件にしないでください。

実装前に該当するdraft契約・受入条件を更新し、関連Unit/Integration/合成E2E・Lint・型検査・SAM変換/lintを実行してください。
次に対象を限定したbuild/package/changeset作成、全ページの差分確認、想定外の共有物変更・Replace/Delete・過大権限が無いことの確認、実行、配備済みhashと合成データでの受入まで進めてください。
作成・維持の参考費用、用途タグ、停止フラグ、rollbackを記録してください。モデル／KB検索は呼ばず、旧有料枠や消化済みスクリプトを再実行・流用しないでください。
合格した増分は日本語でコミットし、ローカルitaiへ順次統合してください。実装と共同確認用の方針文書をPRで混ぜないルールは維持してください。
pushやAmplify切替が必要になったら、専用バックエンドの検証と具体的な接続差分・自動配信への影響を揃えて、その未承認操作だけ確認してください。

最後に、統合したSHA、実際に作成／更新したitai資源、changeset・配備hash、合成検証結果、未受入、費用が発生するもの、rollback、未実行のpush／切替／有料試験を報告してください。
AWSデプロイ成功だけで会社Git連携・実ブラウザ・実データの技術受入・RAG品質検証まで完了したと報告しないでください。
```

---
status: development
last-verified: 2026-10-22
related-code:
  - lambda/knowledge/common-knowledge/
  - infrastructure/sam/common-knowledge-itai-template.yaml
  - frontend/src/components/knowledge/common-knowledge-inbox.tsx
---

# 共通知識: S3正本化とAmplify itai配信への引継ぎ

> 最終検証: 2026-10-22 — ユーザーとの会話で決定した事項の記録。AWS・コードへの反映は次セッション。

前提: [AWS基盤の実装契約と実施記録](common-knowledge-itai-aws-contract.md)。現在のローカルitaiは `f94ade97`（origin/itai `e70c1cd3`、未push）。スタック `EleKnowledge-itai-common-knowledge` はフラグoff・Git未設定・認可表空で稼働中。

## 決定事項（2026-10-22、ユーザー）

1. **正本はGitをやめS3にする。** 既存の配布バケットを正本バケットとして使い、作業用バケットを新設する（置換なし）。
   - 作業用バケット `drafts/`: バージョニング有効。編集の場。開発エージェントはここだけ書ける。
   - 正本バケット `approved/`: 承認時に特定版（作業用のVersionId＋sha256）を自動で不変コピー。KB対象外。
   - 正本バケット `published/`: 公開時に配置し、停止時に外す。**Bedrock KBのデータソースはここだけ**（本文＋KB用metadata）。`manifests/` はCASと読取ガード用。
   - KBの作成・同期は今回行わない（形式だけKB向けに揃える）。
2. **承認と公開は別操作のまま。** 将来はキーマンが編集・承認する想定で、その時はVSCode等を使えないため専用編集画面が必要（後続）。停止も単独操作。
3. **開発エージェントの境界。** 書込は作業用バケットだけ。台帳・正本は読取のみ（バケットポリシーで正本への書込をLambdaの承認・公開ロール以外拒否）。作業版の登録・確認依頼・承認・公開・停止はAPIか同じServiceを呼ぶCLI経由。作業版登録時はIAM主体名を編集者として記録する。知識を「使う」側は公開manifest経由の読取（drafts/approvedの直接参照で代用しない）。
4. **方針文書。** §17の改訂（正本をGitからS3へ）は実装と分け、共同確認用文書（別ブランチ、未push）とmona宛て確認文案（未送信）を作る。itai専用環境の実装・検証は返答を待たずに進める。
5. **配信。** origin/itaiへのpushを許可。Amplify itaiブランチの環境変数で、共通知識APIに加えRAG/チャット等もitai専用API（`EleKnowledge-itai-phase2`）へ切り替える。itai専用スタックに無いAPI（アプリAPI・トラブルシューティング等）は共有devのまま。push前に、itai専用APIで画面（#195の先輩チャット含む）が動くことを確認する。
6. **試験アカウント。** 本アカウント（開発用）＝投稿・編集・公開。登録済みの2つ目（メールに `itai` を含む、現在adminではない）＝承認・閲覧。monaのアカウントは使わない。分野・読者は検証専用の `itai-validation`、検証用の共有許可・根拠台帳を各1件、期限14日。画面には合成の内容だけを入力する。

7. **adminグループ条件を外す**（2026-10-22決定）。共通知識の操作は認可表の業務権限だけで判定し、Cognitoのadminを要求しない。2つ目のアカウントはadminへ追加しない（共有Cognitoは変更しない）。admin配下の画面への入り方も、業務権限のある利用者が入れるよう調整する。I1契約の「adminだけでは編集・承認・公開不可」は維持し、「admin所属が必要」の部分を改める。
8. **有料呼出しOK**（2026-10-22決定）。RAG/チャットをitai専用APIへ切り替えた後、ブラウザ確認の範囲での質問によるBedrock呼出しを許可。新しい有料の一括実測・旧スクリプトの再実行は含まない。

## 実施状況（2026-10-22）

> 最終検証: 2026-10-22 — 実施記録は [実装契約](common-knowledge-itai-aws-contract.md)の「S3正本化の反映と受入」節。

実行順1〜7は完了（7は2アカウントの実ブラウザで一往復と台帳・S3照合まで）。8（§17改訂の共同確認文書とmona宛て文案、別ブランチ・未push）は未着手。アカウントは特定済み（subは未追跡の作業記録のみ）。

## 開始時に確認する判断待ち

- **アカウントの特定**: 2アカウントのログイン名（メール）。subは読取で取得する。秘密値・メールを追跡ファイルへ書かない。

## 実行順

1. 判断待ちの回答を受け、実装契約（`common-knowledge-itai-aws-contract.md`）を更新。
2. 実装: Git依存（作業版・承認・公開時の本文読取・tree照合）をS3作業用／正本アダプターへ置換。承認時の `approved/` 自動反映、公開時の `published/`＋metadata、停止時の除去。CLI（作業版登録・状態操作）。adminグループ条件の扱い。画面の実データガードを検証範囲に限って解除し、本番相当の設定（API URL・権限）を画面へ出す。
3. ローカル試験（I1・アダプター・SAM契約・フロント）。既存の未設定Git経路の試験は置換に合わせて更新。
4. itai共通知識スタックの更新changeset（作業用バケット追加・IAM・バケットポリシー・環境変数。既存表・バケットのReplace/Deleteなし）を全ページ確認して実行。配備hash照合と合成受入。
5. 認可表へ検証用の権限を投入し、フラグをON（changeset確認）。
6. Amplify itai: itai専用APIの値でブランチ環境変数を追加し、push前に画面互換を確認。origin/itaiへpushして自動配信を確認。
7. 実ブラウザで2アカウントによる投函→編集→承認→公開→読取→停止を確認。結果・未受入・費用・rollbackを記録。
8. 別ブランチで§17改訂の共同確認文書とmona宛て文案（未送信）を作成。

各段階で、想定外の差分（共有物の変更、Replace/Delete、過大な権限）や失敗が出たらそこで止めて報告する。

## 端末の注意

pytestは `--basetemp=<作業用一時領域>` と `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.longpaths GIT_CONFIG_VALUE_0=true`。Windowsのaws.exeは `/c/...` パス不可（相対パスを使う）、`/aws/...` 引数は `MSYS_NO_PATHCONV=1`。Pythonの `write_text` はCRLFになり配備hashがずれる（`newline='\n'` で書く）。SAMはルートの `venv/Scripts/sam.exe`、region・profileを明示する。

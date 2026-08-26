---
status: reference
last-verified: 2026-08-26
related-code: lambda/rag/, frontend/src/app/
---

# タスク履歴（5W1H）

作業単位の意思決定と変更内容を、後から見直せるよう 5W1H で記録する運用ログ。
新しいエントリを**上に**追記する（逆時系列）。仕様そのものは各 `docs/**` を正とし、本ファイルは「いつ・なぜ・どう変えたか」の索引とする。

---

## 2026-08-21 認証改善3件: パスワードリセットSDK化 / サインアップ後自動ログイン / トークン24h化

| 項目 | 内容 |
|---|---|
| **Who** | YUKI ITAI / Claude Code |
| **When** | 2026-08-21 |
| **Where** | `frontend/src/app/forgot-password|signup|verify/page.tsx` / `infrastructure/sam/phase1-template.yaml` / `lambda/auth/forgot-password|confirm-password-reset/`（削除） |

**What**
1. **PR #44**（Issue #4）: パスワードリセットを API Gateway 経由から `aws-amplify/auth` の `resetPassword` / `confirmResetPassword` に切替。`ForgotPasswordFunction` / `ConfirmPasswordResetFunction` と両エンドポイント・Lambda ディレクトリを削除。
2. **PR #45**: `signUp` に `autoSignIn: true` を追加し、メール確認完了後（`COMPLETE_AUTO_SIGN_IN`）は `autoSignIn()` でそのままホームへ遷移。別タブ・リロード時はログイン画面へフォールバック。
3. **PR #46**: Cognito User Pool Client の `RefreshTokenValidity` を 30日 → **24時間** に短縮。

**Why**
1. カスタム認証 Lambda はパスワードを平文で受ける経路（2026-07-29 コードレビュー C-1 系統）のため、SDK 化で攻撃面ごと削除。
2. サインアップ完了後に再ログインさせられる UX の不満解消。
3. `phase1-foundation.md` セキュリティ要件「セッション有効期限: 24時間」に対し実装が 30日 と乖離していたのを是正。

**How**
`feature/3-password-reset-refactor` / `feature/signup-auto-signin` / `feature/token-ttl-24h` を develop から分岐し PR #44/#45/#46 を作成。`tsc --noEmit` / `sam validate --lint` パス。ドキュメントは `aws-resource-map.md`・`aws-migration-inventory.md`・`phase1-foundation.md`・`security.md` を各PRで追従。

**リリース状況**
- PR #44 / #45 / #46 は **2026-08-23 に develop へマージ済み**。
- パスワードリセットは **2026-08-23** に itai ブランチを Amplify でデプロイした環境で実環境 E2E を実施し、Amplify SDK 経由のログイン／パスワードリセットが正常に完了することを確認済み。
- **2026-08-26 14:17 JST** に `EleKnowledge-dev-phase1` へ phase1 SAM デプロイを実施し、`UPDATE_COMPLETE` を確認。PR #44 の旧パスワードリセット Lambda 2本・対応 API ルート／呼び出し権限の削除を実環境で確認済み。
- 同じ phase1 SAM デプロイで PR #46 の `RefreshTokenValidity=24` / `Units.RefreshToken=hours` を実環境で確認済み。
- PR #45 のサインアップ後自動ログインは develop へコード反映済み。PR上では develop 環境での個別 E2E 完了記録は確認できていないため、本履歴では「実環境確認済み」とは扱わない。
- 以前の「PR #37/#40 とまとめて phase1 SAM デプロイ」は不要となった。#44/#46 の phase1 反映は上記 2026-08-26 デプロイで完了している。

---

## 2026-07-27 (2) 到達不能カテゴリ追加・検索モード廃止・PR/デプロイ

| 項目 | 内容 |
|---|---|
| **Who** | YUKI ITAI / Claude Code |
| **When** | 2026-07-27 |
| **Where** | `frontend/src/app/chat/page.tsx` / `lambda/rag/rag-function/app.py`（CATEGORY_MAP） |

**What**
1. 資料カテゴリに `site_agent`=現場代理人業務マニュアル / `quality_mgmt`=品質管理業務マニュアル / `w_doc`=W資料 を追加（CATEGORY_MAP＋categoryOptions）。到達不能だった43件が絞り込み可能に。`TEST`(1件) はゴミデータのためUI非追加（データ側で除去予定）。
2. 検索モード（通常/仕様確認）UIを廃止。`SegmentedControl`・`mode` state・`spec` 分岐を削除し、サーバーへは `mode=normal` 固定送信。資料カテゴリの複数選択で代替。

**Why**
モード選択は資料カテゴリの二重軸で混乱要因だったため撤去。到達不能カテゴリは KB 実測で判明した被覆漏れの是正。

**How**
フロント編集 → `tsc --noEmit` パス → `py_compile` パス → コミット `4166f4a`。branch `feature/rag-filter-labels-fix` を push、**PR #26**（base `develop`）作成。

**リリース状況**
- フロント：Amplify が `develop` ブランチ連動。**PR #26 を develop にマージした時点で自動ビルド・反映**される。
- バックエンド（`rag-dev` Lambda, stack `EleKnowledge-dev-phase2`, acct `730972069979`, ap-northeast-1）：`lambda update-function-code` で**コード反映済**（2026-07-27, profile `datautl-bple-mebs`）。CodeSha256 `rBX4mlLxUG45msPO8DrKM6LvNs6xjASqD3XKUC93iOU=` → `zKryouXl9y2T6FWxzKnqQ+LkE9zdLLaI702cAgB/FJk=`、LastUpdateStatus=Successful。**CFnドリフト注意**：SAM管理関数へのコード直接更新のため次回 full `sam deploy` で整合を取ること。
- **注意（要確認）**：ドキュメントは KB を `DF9XUCSPDM` と記載するが、稼働中の `rag-dev` は `KNOWLEDGE_BASE_ID=VQV81CNYU4` を参照（同一データソース S3 バケットを共有）。full `sam deploy` する場合は `KnowledgeBaseId=VQV81CNYU4` を渡さないと KB を付け替えてしまう（runbook の例 `DF9XUCSPDM` は古い）。

---

## 2026-07-27 RAG 絞り込みの是正 と ホーム画面ステータス表記の修正

| 項目 | 内容 |
|---|---|
| **Who（誰が）** | YUKI ITAI / Claude Code |
| **When（いつ）** | 2026-07-27 |
| **Where（どこを）** | `frontend/src/app/chat/page.tsx`（categoryOptions） / `lambda/rag/rag-function/app.py`（build_kb_filter） / `frontend/src/app/page.tsx`（ホーム画面バッジ） / `docs/api/rag.md`（仕様） |

**What（何を）**
1. 資料カテゴリの UI ラベルを KB 実カテゴリ名に是正：`drawing`=据付場用図 / `spec`=C資料 / `tech_info`=TI / `incident`=災害事例集 / `qsheet`=Qシート（`std`=据付基準・`note`=据付ノートは元から一致）。**value（安定キー）は不変**のため API 契約は維持。
2. `build_kb_filter` の機種フィルタを **「選択機種 OR `*` OR `general`」（orAll）** に変更。機種選択時に全機種共通文書（`*`/`general`、KB 実測で約 819 件）が一律除外される不具合を修正。
3. ホーム画面バッジの文言とアイコンを是正：トラブルシューティング「PoC 利用可能（✓）」→「**開発中**（時計）」、品質書類チェック「近日公開（✗）」→「**検討中**（ℹ）」。
4. `docs/api/rag.md` に ② の挙動・HYBRID 検索（`RAG_SEARCH_TYPE`）・`filters.category` 対応表を追記し `last-verified` を更新。

**Why（なぜ）**
KB 実データ（`DF9XUCSPDM` / ap-northeast-1、文書 3,745 件の全メタデータ実測）調査で、(a) UI ラベル 7 項目中 5 項目が KB 実カテゴリ名と乖離、(b) 機種選択時に全機種共通 819 件が除外、(c) ホーム画面のステータス表記が実態と不一致、と判明したため。
調査報告書（Artifact）: https://claude.ai/code/artifact/7684f2d4-4084-498d-aae5-7be4d684619e

**How（どうやって）**
`datautl-bple-mebs` プロファイルで KB のデータソース S3（`ragknowledgebasestack…-datasourcebucket…ybbhm1efhyzb/docs/`）から `*.metadata.json` を全件取得・集計 → フロント/バックエンド/仕様と突合 → 影響最小の差分で是正（読み取り調査 → コード修正 → 仕様追記）。

**未対応・次アクション**
- 到達不能カテゴリ（現場代理人業務マニュアル 30 / 品質管理業務マニュアル 7 / W資料 5＝計 43 件）の UI 追加、`TEST` データの除去（再設計 07-③）
- 機種粒度の再設計、`stringContains` 誤爆（`AXIEZ`→`MAXIEZ` 混入）対策（07-④）
- 検索モードの資料カテゴリ統合（07-⑤）
- `docs/features/production/phase2-rag-chat.md` の旧 `SearchFilters` 記述（乖離警告付き）の全面改訂（別途要確認）
- **AWS 反映は未実施**：② は Lambda 再デプロイで有効化される（本コミット時点ではコード変更のみ）

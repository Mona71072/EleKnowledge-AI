---
status: reference
last-verified: 2026-07-27
related-code: lambda/rag/, frontend/src/app/
---

# タスク履歴（5W1H）

作業単位の意思決定と変更内容を、後から見直せるよう 5W1H で記録する運用ログ。
新しいエントリを**上に**追記する（逆時系列）。仕様そのものは各 `docs/**` を正とし、本ファイルは「いつ・なぜ・どう変えたか」の索引とする。

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

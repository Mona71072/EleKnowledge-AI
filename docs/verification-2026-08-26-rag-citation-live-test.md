---
status: reference
last-verified: 2026-08-26
related-code: lambda/rag/rag-function/app.py, frontend/src/app/chat/page.tsx, frontend/src/lib/documents.ts, infrastructure/sam/phase2-template.yaml
---

# 実機確認記録: RAG フィルタ改修と引用リンク認証（2026-08-26）

> **状態:** 実機確認の記録（dev 環境 / itai サンドボックスブランチ）
> **対象:** PR #56（KB 既定値是正）/ #57（カテゴリ常時フィルタ＋チップ）/ #58（機種フィルタ listContains 化）/ #50（引用リンクのログイン必須化）
> **確認者:** itai（yukiworkspace）。確認環境は `EleKnowledge-dev-phase2`（rag-dev Lambda）＋ Amplify itai ブランチ

## 1. デプロイ記録

| 回 | 内容 | 結果 |
|---|---|---|
| 1回目（17:49） | #56/#57/#58 を itai にマージ（280d589）して `sam deploy`。**#50 の `/rag/document` バックエンドもこのとき初回反映**（itai に以前からマージ済みだった分） | UPDATE_COMPLETE。`KnowledgeBaseId` はパラメータ変更なし = VQV81CNYU4 維持 |
| 2回目（19:13） | 実機確認を受けた追随対応（後述 §4）を itai にマージ（fc9b31b）して `sam deploy` | UPDATE_COMPLETE。実更新は RagFunction のみ（TTL 300 秒反映） |

注意: スタック Outputs に SSM `/eleknowledge/dev/knowledge-base-id` が出るが、実測（同日）では ParameterNotFound。[decisions-2026-08-26-kb-selection.md](./decisions-2026-08-26-kb-selection.md) の持ち越し論点。

## 2. 確認結果（フィルタ改修: #57/#58）

| # | 確認項目 | 結果 | 備考 |
|---|---|---|---|
| ① | 全検索で GenU / quick-start 由来の引用が出ない | ✅ 合格 | 「GenUについて教えて」で GenU ドキュメントの引用・回答なし（試行1回） |
| ② | 機種=AXIEZ で AXIEZ-LINKs 単独資料が混ざらない | ✅ 合格 | 「建築誤差が基準外の時の対応方法は？」で AXIEZ-LINKs 対象の C-1-C32.1-J- が返らない（試行1回）。listContains 化の狙いどおり |
| ③ | 機種選択時に共通文書（`["*"]` / `["general"]`）が出る | ✅ 合格 | 機種=AXIEZ「溶接の据付基準は？」で全機種対象 SUE-2-04.pdf がヒット（試行1回）。`_is_common_model_type` 修正による回復 494 件分の実証 |
| ④-a | site_agent / quality_mgmt チップの表示 | ✅ 合格（遅延あり） | 初回確認時は未表示 = **Amplify ビルド反映前の旧バンドル**だった（旧リスト固有の W資料チップが見えていたことで特定）。ビルド反映後に表示を確認 |
| ④-b | 全検索（チップなし）で GM 資料（現場代理人）がヒットするか | ⚠️ ヒットせず = **仕様どおり** | 2026-07-29 導入の本命優先 retrieve（mona 設計、[decisions-2026-07-29-rag-nuance.md](./decisions-2026-07-29-rag-nuance.md) §3-4）により、カテゴリ未指定時は C/TI/据付基準を先行検索し、弱いときのみ全資料へ拡大するため。site_agent チップ選択時は直接絞り込みになる。全検索でも出したい場合は優先カテゴリ追加/常時マージのチューニングが必要（未判断） |
| ⑤ | w_doc チップ選択で 0 件（既知） | ✅ 再現 | W資料 5 件全件が取扱機種スコープ対象外のため。→ ユーザー決定で**業務判断が出るまでチップ非表示**に変更（§4） |

## 3. 確認結果（引用リンク認証: #50）

| # | シナリオ | 結果 |
|---|---|---|
| ⑥-1 | ログイン済みで引用クリック | ✅ 中継ページ `/doc` 経由で文書が開く |
| ⑥-2 | ログアウト後、コピー済みの**閲覧 URL**（発行済みプリサイン URL）を開く | ⚠️ 開けてしまう（有効期限内）。プリサイン URL はベアラー URL で失効前の取り消しが不可という構造的限界。→ TTL 300 秒化で露出窓を最小化（§4） |
| ⑥-3 | ログアウト後、コピー済みの**引用リンク**を開く | ✅ 中継ページ → ログイン要求。認証ブロックが機能 |
| その他 | 数時間後に過去チャットの引用リンクをクリック | ❌ S3 の AccessDenied（Request has expired）。#50 以前のメッセージには TTL 1h のプリサイン URL がそのまま保存されていたため。→ フロントで旧 URL を `s3://` に逆変換して中継導線に乗せる改修を実施（§4） |

## 4. 実機確認を受けた追随対応（同日実施）

| 対応 | 反映先 | コミット |
|---|---|---|
| w_doc チップを業務判断まで非表示（CATEGORY_MAP / 許可リストは維持） | PR #57（#58 へも取込） | 9461002 / 15078cb |
| プリサイン URL TTL 3600 → 300 秒 | PR #50 | ebe8748 |
| 旧プリサイン URL → `s3://` 逆変換（過去履歴の引用復活＋保存済み URL の流出封鎖） | PR #50 | 27fd9d7 |
| 判断経緯の決定記録（TTL 変遷・ベアラー URL リスク・逆変換） | PR #50: [decisions-2026-08-26-presigned-url-ttl.md](./decisions-2026-08-26-presigned-url-ttl.md) | 65bc8fe |
| `GET /rag/document` API 仕様と期限切れ URL の想定挙動の明文化 | PR #50: [api/rag.md](./api/rag.md) ほか | ef1f811 |

いずれも itai にマージ済み・2回目デプロイで dev 反映済み（フロント分は Amplify 自動ビルド）。

## 5. 持ち越し（このサイクルでは対応しない）

- **W資料スコープの業務判断**: W資料機種（GPM 等）の HANDLED 追加 or カテゴリのスコープ例外化。判断が出たら w_doc チップを復活させる
- **全検索での少数カテゴリ（GM 資料等）の露出**: 本命優先 retrieve のチューニング（優先カテゴリ追加 / 常時マージ）。mona と要合意
- **SSM `/eleknowledge/dev/knowledge-base-id` の実態不一致**: Outputs にあるが実パラメータ不存在。テンプレ整理の論点
- **TTL 300 秒の様子見**: 大型 PDF のレンジ読み込みが 5 分を跨ぐと未読ページ取得が失敗しうる。頻発すれば再調整（例: 900 秒）

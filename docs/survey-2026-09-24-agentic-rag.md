---
status: draft
last-verified: 2026-09-24
related-code: lambda/rag/rag-function/app.py
---

# 調査: 単発 RAG と反復・エージェント型 RAG、深いモードの作り方

> **調査日:** 2026-09-24
>
> **方法:** Claude（論文・製品・AWS 公式）と Codex / gpt-5.6-luna（日本企業の事例、本リポジトリのコード分析、反論役）の複数エージェントで並行調査し、数値と一次情報を照合した。
>
> **位置づけ:** 設計 [design-2026-09-24-rag-two-modes.md](./design-2026-09-24-rag-two-modes.md) の根拠。数値は出典どおりで、本システムでの効果は未測定。

## 1. 現行の構成（2026-09-24 時点の develop）

- 聞き返し（ルール判定）→ KB Retrieve 1 回（ハイブリッド、30 件）→ score 0.3 以上・1 資料 2 件・上位 10 件（各 1,200 文字、画像 3 枚まで）→ 採用モデルを 1 回（運用上の採用は Sonnet 5 で、thinking を明示的に無効化。SAM テンプレートの既定値は Haiku 4.5 のまま）。弱い検索（最高 score 0.22 未満など）は作文せず not_found。
- 再検索は、略語展開で検索語が変わり、1 回目の選別結果が 0 件のときだけ。LLM が検索し直す仕組みはない。
- 会話履歴は生成には渡るが、検索に使うのは聞き返しの直後だけ。
- KB は別部門所有の共有 KB（標準テキスト解析）。表は行・列の構造を失った平文になり、図の中の情報は取り込まれない。図面の説明欄が空という旧調査もある（件数は要再確認。[kb-change-requests.md](./kb-change-requests.md) KB-08・KB-12）。
- Sonnet 5 の生成は平均 11.7 秒、最大 16.8 秒（[eval-2026-09-09-model-bakeoff.md](./eval-2026-09-09-model-bakeoff.md)）。

## 2. 反復検索は精度を上げるか（論文）

| 研究 | 結果 | 出典 |
|---|---|---|
| IRCoT（検索と思考を交互に） | マルチホップで検索 +21pt、回答 +15pt | https://arxiv.org/abs/2212.10509 |
| Adaptive-RAG（難しさで方式を切り替え） | 単発 45.27%・1.00 秒、多段 49.70%・3.33 秒、切り替え 48.97%・1.46 秒。単一ホップ（SQuAD）では多段が悪化（27.8 → 24.4） | https://arxiv.org/html/2403.14403v2 |
| Search-o1 | マルチホップで大幅改善（2Wiki 35.6 → 58.0）。単一ホップは 47.8 対 47.6 で差なし | https://arxiv.org/html/2501.05366 |
| FlashRAG の統一比較 | IRCoT は NQ で通常 RAG を下回り（33.3 対 35.1）、HotpotQA では上回る | https://github.com/RUC-NLPIR/FlashRAG |
| ReAct | 失敗の 23% は「役に立たない検索結果に推論が引きずられた」 | https://arxiv.org/html/2210.03629v3 |
| 検索のしすぎ | 検索ステップの 27.7% が不要 | https://arxiv.org/abs/2505.17281 |

**要点:** 反復の効果は「比較・複数資料・多段」の質問に集中する。1 資料で答えが出る質問では効果が無いか悪化し、時間は 3〜9 倍。

## 3. 思考（thinking）だけで正確になるか

- 推論を長くすると、Claude は無関係な情報に引きずられやすくなる（Anthropic, Inverse Scaling in Test-Time Compute）。https://alignment.anthropic.com/2025/inverse-scaling
- 根拠文書の要約タスクで、推論モデルは非推論モデルより幻覚率が高い例がある（DeepSeek-R1 14.3% 対 V3 3.9%、Vectara）。https://www.vectara.com/blog/deepseek-r1-hallucinates-more-than-deepseek-v3
- 思考をツール結果の分析と追加の検索に使うと改善する（Anthropic think tool: τ-bench airline 0.370 → 0.584）。https://www.anthropic.com/engineering/claude-think-tool

**要点:** 1 回の検索結果を深く考えさせるだけでは、機種の混在を増やすおそれがある。思考は「追加の検索」と「照合」に使う。

## 4. 主要製品の作り方

| 製品 | 通常 | 深いモード |
|---|---|---|
| ChatGPT | Instant / Thinking（自動振り分けあり） | Deep research（5〜30 分、計画を編集可） |
| Claude.ai | 1 回の応答内で検索を 1〜数回 | Research（数分、複数エージェント。通常チャットの約 15 倍のトークン） |
| Perplexity | 通常検索 | Pro Search（計画→段階検索）、Deep Research（2〜4 分） |
| M365 Copilot | 速度重視のチャット | Researcher（1 ユーザー月 25 回まで） |
| Google Vertex AI Search | 質問の書き換え（既定で有効）＋根拠照合 | 多段推論（オプション、最大 5 段） |
| Glean | Adaptive / Fast / Thinking | Deep Research（5〜30 分） |

出典: https://www.anthropic.com/engineering/multi-agent-research-system ／ https://openai.com/index/introducing-deep-research/ ／ https://learn.microsoft.com/en-us/microsoft-365/copilot/researcher-agent ／ https://docs.cloud.google.com/generative-ai-app-builder/docs/answer ／ https://docs.glean.com/user-guide/assistant/deep-research

**要点:** どの製品も、既定は「書き換え → 並列検索 → リランク → 生成（＋根拠照合）」の決まった流れ。何周も回すのは別モードで、時間の目安・途中経過・回数上限・引用つきの形をそろえている。

## 5. 労力あたりの効果が大きい施策

1. **評価セット**（改善を判断できる前提）
2. **リランク**: 上位 20 件の取りこぼし 2.9% → 1.9%（Anthropic Contextual Retrieval）
3. **チャンクへの文脈付与・メタデータ補完**: 取りこぼし 35〜49% 減（同上）。https://www.anthropic.com/news/contextual-retrieval
4. **会話履歴を使った書き換え・質問の振り分け**（Vertex / Azure は既定で有効）
5. **条件付きの再検索**（検索が弱いときだけ）
6. 自由に回るエージェント・複数エージェント（費用 4〜15 倍、効果は調査型に限定）

長い文脈は 32k〜64k トークンを超えると多くのモデルで劣化する（Databricks）。https://arxiv.org/abs/2411.03538

## 6. 日本企業の事例（技術文書）

| 事例 | 効いた施策 | 出典 |
|---|---|---|
| 鴻池運輸 | 記載粒度の統一、検索語の補正、ヒットした文書の全項目を別 DB から取得。100 件中 95 件合格 | https://aws.amazon.com/jp/blogs/news/konoike-transport-genai-chat/ |
| セゾンテクノロジー | キーワード抽出＋キーワード検索＋階層チャンク。Knowledge Bases 比で精度 +22% | https://aws.amazon.com/jp/blogs/news/gen-ai-usecase-saison-technology/ |
| NTT 西日本 | マニュアルをページ分割・Markdown 化、表は HTML 経由で Markdown 化、メタデータフィルタ | https://aws.amazon.com/jp/blogs/news/aws-genai-usecases-nttwest-elgana-rag/ |
| 日本製鋼所 | 短い抜粋ではなく、上位文書の全文を渡す | https://aws.amazon.com/jp/blogs/news/genai-case-study-jsw/ |
| メック | 検索語の自動生成、不十分なら複数回検索（効果の数値は未公表） | https://aws.amazon.com/jp/blogs/news/case-study-mec/ |

**要点:** 国内事例で効いているのは、取り込みの作り込み（表・ページ・メタデータ）と、ヒットした文書の「親単位」を取り直して渡す方式。エージェント化の効果は数値が公開されていない。

## 7. AWS の選択肢（東京リージョン、2026-09-24 時点）

| 項目 | 事実 | 出典 |
|---|---|---|
| 29 秒制限 | REST API のタイムアウトは引き上げ申請可（スロットル上限とのトレードオフ）。レスポンスストリーミングは最大 15 分。ただし Python Lambda は Lambda Web Adapter かカスタムランタイムが必要 | https://aws.amazon.com/about-aws/whats-new/2024/06/amazon-api-gateway-integration-timeout-limit-29-seconds/ ／ https://docs.aws.amazon.com/apigateway/latest/developerguide/response-transfer-mode.html ／ https://docs.aws.amazon.com/lambda/latest/dg/configuration-response-streaming.html |
| リランク | Amazon Rerank 1.0、Cohere Rerank 3.5 とも ap-northeast-1 で利用可 | https://docs.aws.amazon.com/bedrock/latest/userguide/rerank-supported.html |
| 解析 | 標準パーサーはテキストのみ。表・図には FM パーサー / Data Automation を推奨（全 PDF に追加費用） | https://docs.aws.amazon.com/bedrock/latest/userguide/kb-advanced-parsing.html |
| Managed Knowledge Base | 2026-06-17 GA、東京対応。AgenticRetrieveStream（質問分解・十分性判定・反復）と組み込みの解析・リランカー。**既存 KB の変換ではなく新規作成・再投入**。直接 API のフィルタ（`managedSearchConfiguration`）の演算子一覧に `listContains` が載っていない（AgentCore のコネクタ文書には載っている）、ページ番号・引用の形式が違う、IAM が増える。料金は Retrieve $1 / 1,000 回、Agentic $4 / 1,000 回＋内部の Retrieve、保管 $5 / GB・月 | https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-bedrock-managed-knowledge-base/ ／ https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-test-config.html ／ https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-agentic-retrieve.html |
| Bedrock Agents（Classic） | 2026-07-30 から新規顧客の受付停止（既存顧客は継続利用可）。後継は AgentCore | https://docs.aws.amazon.com/bedrock/latest/userguide/agents-supported.html |
| Sonnet 5 の思考設定 | 既定は adaptive。手動の budget_tokens は不可。深さは effort（low〜max）で調整。InvokeModel では effort を thinking の外に置く。思考トークンは出力として課金 | https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html ／ https://platform.claude.com/docs/en/build-with-claude/effort |
| Haiku 4.5 | モデルカードに「EOL は 2026-10-01 より前にはならない」（廃止日の確定ではない） | https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-4-5.html |

## 8. 費用の目安

Anthropic の公表価格（Sonnet 5: 入力 $2 / 出力 $10、キャッシュ読み取り $0.20 / 100 万トークン）での概算。Bedrock 上の正式単価は未確認で、4.7 世代以降のトークナイザーは約 30% 多く数える。

| 方式 | 1 問あたり |
|---|---|
| 現行（通常モード） | 約 $0.01〜0.03（モデル比較の実測は生成部分のみで $0.0136） |
| 書き換え＋リランクを追加 | ＋$0.002〜0.004 |
| 上限つき反復（3 検索） | 約 $0.07〜0.10 |
| じっくりモード（計画・統合・照合） | 約 $0.2〜0.6 |

リランクは Cohere Rerank 3.5 が $2 / 1,000 クエリ、Amazon Rerank 1.0 が $1 / 1,000 クエリ（1 クエリ最大 100 チャンク。AWS 公式料金ページ）。上の概算はすべて公表単価からの計算で、実測で置き換える。

## 9. 反論役の指摘（設計に反映済み）

- 評価セットの完成を待ってから試すのは遅い。20〜50 問で始め、評価と実験を並行で進める。
- ストリーミングは体感を良くするが、正確さは上げない。
- Managed KB への移行は、反復検索の効果と混ざらないよう、本番と切り離した試験として後で行う。
- 検索結果を全部引用に付けても、主張の根拠になるとは限らない。主張と根拠の対応を保持して照合する。

## 10. 未確認事項

- Bedrock 上の Sonnet 5 の正式単価、タイムアウト引き上げの上限値
- 本システムでの KB Retrieve・Rerank の実測時間
- 日本語の昇降機資料での、リランク・埋め込みモデル・Managed KB の効果
- 現行 KB の埋め込みモデルとチャンク設定（所有部門に確認。[kb-change-requests.md](./kb-change-requests.md)）

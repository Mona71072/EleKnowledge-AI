---
status: draft
last-verified: 2026-10-20
related-code:
  - lambda/rag/rag-function/app.py
  - lambda/rag/rag-function/knowhow_retrieval.py
  - lambda/rag/senpai-synthesis/app.py
  - infrastructure/sam/phase2-template.yaml
  - frontend/src/components/knowledge/KnowledgeSenpaiChat.tsx
  - frontend/src/lib/knowledge-senpai-chat.mjs
  - scripts/eval/run_retrieve_eval.py
---

# 調査: 工技先輩を「読む→探す→切り替える→まとめる」エージェント型にできるか、途中経過を出せるか

> **調査日:** 2026-10-20（URL の参照日はすべて同日）
>
> **位置づけ:** 先輩チャットを ChatGPT / Claude のように「案内（ノウハウ）を先に読み、技術資料・法令を順に探し、足りなければ言い換えや別の道具に切り替え、最後に出典付きで 1 つの答えにする」形にする案の調査。前回の [survey-2026-09-24-agentic-rag.md](./survey-2026-09-24-agentic-rag.md)（論文 IRCoT・Adaptive-RAG・Search-o1・FlashRAG、ReAct の失敗、検索のしすぎ 27.7%、思考の注意点、製品比較、AWS 選択肢、費用）は繰り返さず、そこにない点だけを足す。
>
> **事実の区別:** 公式文書・論文・計測は「事実」、ベンダーの紹介ページや二次記事は「紹介（二次）」と明記する。確認できなかったものは **未確認**。本システムでの効果は未測定で、数値は出典どおり。
>
> **関連:** [design-2026-09-24-rag-two-modes.md](./design-2026-09-24-rag-two-modes.md) ／ [decisions-2026-09-24-rag-two-modes.md](./decisions-2026-09-24-rag-two-modes.md)（D1〜D8）／ [design-2026-10-01-knowhow-flywheel.md](./design-2026-10-01-knowhow-flywheel.md) §9.1 ／ [features/development/senpai-synthesis-prototype.md](./features/development/senpai-synthesis-prototype.md)

## 0. 要約

- **進捗表示（「ノウハウを確認中 → 技術資料を検索中…」）と、エージェント化（AI が次の道具を自分で選ぶ）は別の話。** 進捗表示は今の固定の流れにも付けられる。先に進捗表示だけを入れ、エージェント化は評価で決めるのが安全。
- **主要製品が利用者に見せるのは「道具の呼び出しの要約」（計画・検索語・資料名・状態）で、モデルの生の思考ではない。** Glean は計画のタスク一覧に状態と進捗バーを出す（公式文書）。Claude の API も検索語をストリームに流す（公式文書）。生の思考を出す製品は確認できなかった。
- **効果の根拠は「複数資料にまたがる・曖昧な質問」に偏る。** 1 資料で答えが出る質問では差が出ないか悪化し、時間と費用は数倍になる（前回調査）。新しい証拠でも、効果を左右するのはループよりも検索の質（BrowseComp-Plus）で、モデルは取得済みの根拠を使い切れず、根拠がないときに断れない（WebDetective）。**KB の質が低いままではループで補えない。**
- **推奨は「案内を先に読み、独立な検索は並列に走らせ、足りないときだけ上限つきで追加検索する」有界ツールループ。** 順番に 1 つずつ探す形は遅く、29 秒に収まらない。ノウハウカードの要約（機種・制御方式・出典の資料番号）を先に読むことで、検索の絞り込みに使える。
- **進捗の運び方は、第 1 候補が「DynamoDB の進捗記録を数秒ごとに取りに行く方式」（じっくりモードと同じ土台）、第 2 候補が「API Gateway REST のレスポンスストリーミング」。** 後者は 2025-11-19 に一般提供され東京でも使えるが、Python Lambda は標準ランタイムでストリーミングできず Lambda Web Adapter かカスタムランタイムが必要で、REST API 経由の動作は **未確認（要 PoC）**。
- **D6（固定ワークフロー）との関係:** 有界ツールループは「マルチエージェント」ではなく単一 AI だが、「固定の手順」ではない。**新しい共同決定（案: D9）が必要。** 先に評価（23 問＋ golden v2）で、固定の流れ・並列の流れ・有界ループを比べる。
- **セキュリティ上の最大の論点は、検索結果とノウハウ本文に含まれる命令（間接プロンプトインジェクション）。** ツールを読み取り専用に限り、`userId` と機種範囲をサーバーが注入し、外部送信の手段（Web・URL 取得）を持たせない設計にすれば、「機密・未信頼入力・外部送信」の 3 点が揃うことを避けられる。

## 1. 製品は何をどう見せているか

### 1.1 見せ方の比較

| 製品 | 利用者に見えるもの | 区分 | 出典 |
|---|---|---|---|
| Claude API の Web 検索ツール | 検索語（`server_tool_use` の入力）、結果（URL・タイトル）、引用。ストリーミングでは、検索実行中に間が空き、検索語が流れ、結果が続く。`max_uses` で回数を制限でき、超過は結果内のエラーコード | 事実（公式） | https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool |
| Claude の思考 | API が返すのは「要約された思考」のブロック。生の思考ではない | 事実（公式） | https://platform.claude.com/docs/en/build-with-claude/extended-thinking |
| Anthropic の Research（多エージェント） | 設計記事は内部構造（主エージェント＋サブエージェント、引用専用の工程）を述べるが、画面の見せ方は述べない。運用では会話の中身を見ずに判断パターンだけを追跡する | 事実（公式ブログ） | https://www.anthropic.com/engineering/multi-agent-research-system |
| Glean（Thinking モード） | 計画のタスク一覧（保留・実行中・完了）、全体の進捗バー（例 3/5）、現在の状態、途中の推論の痕跡、ツール呼び出し。単純な質問では計画を作らず直接答える。計画は Thinking モードのみ | 事実（公式文書） | https://docs.glean.com/user-guide/assistant/glean-chat/plan |
| Gemini Deep Research | 計画を提示して編集でき、進行中は「思考」を表示する、と Google の紹介ページが述べる | 紹介（ベンダー） | https://gemini.google/overview/deep-research/ |
| ChatGPT の deep research | 側面パネルに思考と閲覧の様子を表示、最終は引用と思考の要約つき。公式ページは取得できず（403）、公開時期の報道とシステムカードの記述による | 紹介（二次） | https://www.maginative.com/article/openai-unveils-deep-research-an-ai-agent-that-conducts-multi-step-research-tasks/ ／ https://cdn.openai.com/deep-research-system-card.pdf |
| Perplexity Pro Search | 質問を小さな手順に分けて広い出典から探す、と公式ブログ。手順の表示の細部は公式では確認できず | 公式は概要のみ。表示は **未確認** | https://hub-prod.perplexity.ai/hub/blog/getting-started-with-perplexity |
| Microsoft 365 Copilot の Researcher | 検索先（Web・Work 等）の選択、引用つきの報告。活動表示の中身を述べる Microsoft の一次文書は見つからず | 二次のみ。**未確認** | https://www.candede.com/articles/microsoft-365-copilot-researcher-agent-deep-dive |

**読み取れること:** (1) 利用者に出るのは「道具の名前＋対象（検索語・資料）＋状態」。(2) 計画や進捗バーを出す製品は、単純な質問では出さない（Glean）。(3) 生の思考を見せる製品は、公式文書では確認できなかった。生の思考は誤りや内部情報を含みうるため、見せる必然性は薄い（5 章）。

### 1.2 待ち時間と信頼の研究

| 知見 | 出典 |
|---|---|
| 10 秒を超える処理には進捗表示（完了割合、全体が不明なら処理した項目を 1 つずつ名指す）、最後の手段としてスピナー | 事実（Nielsen Norman Group の古典的指針）https://www.nngroup.com/articles/response-times-3-important-limits/ |
| 初回応答まで 2 秒の群は、9 秒・20 秒の群より「考えていない・役に立たない」と評価。遅延は多くの参加者が「AI が考えている」と解釈し、非常に長い待ちでは不満や信頼低下に傾くことがある。待ち時間は設計変数であり単に短ければよいわけではない（CHI 2026 採択予定。arXiv 番号と投稿日に食い違いがあり、**書誌は要再確認**） | 事実（論文）https://arxiv.org/abs/2604.06183 |
| 仮想エージェントの実験で、4 秒を超えると体験が悪化し、会話のつなぎ（フィラー）が体感を改善した。人工的な待機表示の効果は有意でなかったという要約があるが、これは検索結果の二次要約で、原文では未確認 | 事実（論文、一部 **未確認**）https://arxiv.org/abs/2507.22352 |
| 生成検索エンジン 4 種の評価で、文の 51.5% しか引用で完全に裏づけられず、引用の 74.5% しか該当の文を支えていなかった。複数出典を組み合わせる場面で悪い | 事実（論文、2023 年の旧世代）https://arxiv.org/abs/2304.09848 |

**示唆:** (a) 進捗は「待たされる不安」の軽減に効くが、**内容のある進捗**（何を探しているか）でないと意味が薄い。(b) 出典を並べても根拠になるとは限らない。引用の裏づけ検証が別途必要（2.5 節）。(c) 速さだけを目標にしない。ただし本システムの生成は平均 12 秒・最大 17 秒で、ツールを足すと 29 秒を超えるため、待ち時間の長さではなく**待ち時間の中身を見せる**ことが課題になる。

## 2. 作り方のパターン

### 2.1 4 つの型

| 型 | 内容 | 長所 | 短所 | 本件での位置 |
|---|---|---|---|---|
| A 固定ワークフロー | 決まった順で検索・生成（D6、現行、先輩のまとめ試作） | 予測可能、費用と時間が読める、評価しやすい | 想定外の質問で追加検索できない | ベースライン |
| B 計画つきワークフロー＋適応的な後退 | 決まった下準備（並列検索）のあと、LLM が十分性を判断し、不足時だけ再検索 | 速い、上限が明確 | 判断の質に依存 | **推奨の中核** |
| C 有界ツールループ | LLM が道具を選んで繰り返す（上限つき） | 想定外の質問に強い、ユーザーの想像に近い | 遅い、検索のしすぎ、評価が難しい | B の拡張として段階導入 |
| D 多エージェント | 主エージェント＋サブエージェント | 広い調査に強い | 通常チャットの約 15 倍のトークン | 対象外（D6、設計§9.1） |

Anthropic は、エージェントを「LLM が自分の手順と道具使用を動的に決めるもの」、ワークフローを「あらかじめ決めたコードの経路で LLM と道具を組むもの」と定義し、**まず最も単純な方法から始め、効果が示せるときだけ複雑にする**こと、反復回数の上限などの停止条件を置くこと、計画の手順を見せることを勧めている。https://www.anthropic.com/engineering/building-effective-agents

### 2.2 「案内を先に読む」の作り方

- Anthropic は、必要な情報を事前にすべて入れず、軽い参照（ファイルパス・保存した検索語）だけを持って**必要になったときに読み込む**「ジャストインタイム」と、段階的に開示する探索を勧める。Claude Code は CLAUDE.md を最初に読み込み、glob や grep で探す**ハイブリッド**。文脈が膨らむと想起精度が落ちる（コンテキストの腐敗）。https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Agent Skills は 3 段階: 起動時に名前と説明だけ（1 件あたり約 100 トークン）、該当時に本文（5k トークン未満）、必要時に付属ファイル。信頼できない Skill は、道具の悪用やデータ漏えいにつながるので監査が必要、と警告している。https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- **ノウハウカードへの当てはめ（提案）:** 段 1 = カード索引（ID・題・対象機種・制御方式・適用条件・出典の資料番号）を、字句検索で数件に絞って渡す。段 2 = 必要なカードの本文（`get_card`）。段 3 = 出典の原資料（技術 KB の該当ページ）。これは設計§9.1「Markdown は手がかりで、原資料で確認する」と同じ向き。現行のカードは約 398 件、全件が未承認の下書きなので、**「未承認・参考」の印を最後の回答まで持ち回す**。
- Claude Code のコード検索については、開発者が「初期はベクトル DB を使っていたが、エージェント検索（grep 等）の方が良かった」と述べたと報じられている（二次、公開された対照実験は確認できず）。一方 Cursor は、grep だけの探索に意味検索を足すと、評価で正答率が平均 12.5%（モデルにより 6.5〜23.5%）上がり、A/B で 1,000 ファイル以上のコードベースでの定着率が 2.6% 上がったと報告している（ベンダー自己報告）。**結論は「探索ループ単独」ではなく「意味検索とループの併用」。** https://smartscope.blog/en/ai-development/practices/rag-debate-agentic-search-code-exploration/ ／ https://cursor.com/blog/semsearch

### 2.3 道具（ツール）設計の原則と、先輩チャットの道具案

Anthropic の道具設計の指針（要点）: 関連する操作は 1 つの道具にまとめる／名前に接頭辞をつける／ID より人が読める値を返し、必要なら `response_format`（concise / detailed）で詳しさを選ばせる／ページ分割・切り詰め・既定値でトークンを節約／誤りの返し方は「何が悪く、どう直すか」を書く／説明は新人への説明のように書く／現実的な複数手順の評価で改善する。https://www.anthropic.com/engineering/writing-tools-for-agents ／ 道具が多いと選択が悪化する報告もある（RAG-MCP: 大量の道具の説明を渡す基準 13.62% に対し、関連する道具だけを検索して渡すと 43.13%。条件は MCP 道具選択の人工的な負荷試験で、二次要約による確認）。https://arxiv.org/html/2505.03275v1 → **道具は 5〜7 個に絞る。**

| 道具名（案） | 入力 | 出力（要点） | 注意 |
|---|---|---|---|
| `knowhow_find` | `query`、`model_hint?` | 上位 N 件のカード要約（id・版・題・対象機種・制御方式・適用条件・出典資料番号・状態=下書き）と件数 | 既存の字句マッチャー。**LLM を使わず ms 単位**。最初に必ず 1 回、アプリ側が実行してもよい |
| `knowhow_get` | `card_id` | 本文（上限文字数、先頭 600 字から段階拡張可） | 本文は「資料」として囲って返す（5 章）。命令として扱わない |
| `tech_search` | `query`、`model_filter?`（サーバーが機種範囲と積集合を取る）、`top_k?` | 抜粋（資料名・ページ・score・短い本文）、重複除去済み、`sufficiency_hint`（最高 score と件数） | 既存の閾値（score 0.3、1 資料 2 件等）をツール内に持つ |
| `law_search` | `query` | 法令名・条・施行日・抜粋 | 法令 KB ＋全文補強。同上 |
| `doc_page_get` | `doc_id`、`page` | 該当ページの本文／画像参照 | 表・図は現行 KB で平文化されるため限界がある（前回調査） |
| `ask_user` | `question`、`options?` | （ループを止めて利用者へ返す） | 機種や制御方式が不明なとき。答えを AI が補わない（設計§9.1） |

**入力の原則:** 利用者 ID・権限・機種範囲は**モデルに渡させない**。サーバーが JWT とセッションから注入する。`query` は長さ上限と文字種を検証する。**出力の原則:** 件数と上限到達の印（`truncated`）、`next_action_hint`（「別の言い回しで再検索」「資料ページを開く」）を返し、同じ結果の再取得を防ぐため結果 ID を持たせる。

### 2.4 停止条件と予算

- Anthropic の目安: 単純な事実確認は 1 エージェントで道具 3〜10 回、比較は 2〜4 のサブエージェントで各 10〜15 回。失敗例に「単純な質問に 50 のサブエージェントを起動」「存在しない出典を延々と探す」。https://www.anthropic.com/engineering/multi-agent-research-system
- Claude の Web 検索ツールは `max_uses` で上限を持たせ、超過は結果内のエラーとして返す。単純な事実は通常 1〜3 回、比較は 10 回以上。**本件も道具側で上限を強制し、超過は「予算切れ」の結果を返してモデルに答えさせる**のがよい。
- 提案する既定値（実測で調整。根拠のある数値ではなく出発点）: 検索系の道具合計 6 回、モデル往復 4 回、ジョブ全体 60 秒、費用上限は じっくりモードの 0.60 ドル/ジョブより小さく、同じ検索語・同じ結果の再取得は拒否、「新しい資料が増えなかった」往復が 2 回続いたら終了。

### 2.5 検索結果が足りないとき・根拠の裏づけ

- **Corrective RAG**: 軽量な評価器で検索結果の品質を「正しい／誤り／曖昧」に分け、悪いときは別の検索（Web）で補い、無関係な文を除く。小型モデルの設定では標準 RAG に対し PopQA +4.4〜7.0pt、PubHealth +36.6pt（Self-RAG 設定）などの改善が報告された。論文の自己報告で、評価器は学習済みの小型モデル。https://arxiv.org/abs/2401.15884 → 本件は評価器を学習しなくても、`sufficiency_hint` の閾値（既存の弱い検索ゲート）と LLM の十分性判断で近い役割を作れる（効果は未測定）。
- **再検索に使う道具は意味が違うものにする。** 同じ道具に似た語を投げ直すだけでは「検索のしすぎ」になる（前回調査の 27.7%）。言い換え・機種フィルタの変更・法令側への切り替え・資料ページの直接取得、のように手が違うときだけ許す。
- **取得済みの根拠を使い切れない・根拠がないのに断らない**という失敗が、25 モデルの評価で観察された（WebDetective）。検索の十分性・知識の利用・拒否を分けて測る必要がある。https://arxiv.org/abs/2510.05137 → 回答前に「主張→根拠（資料 ID・ページ）」の対応を構造化出力させ、**アプリ側で、その ID が実際に取得した結果に含まれるかを機械的に検査**する（モデルが作った引用を信用しない）。
- Bedrock の Managed Knowledge Base の `AgenticRetrieveStream`（質問分解・十分性判定・反復・全文展開、計画／検索／先行検索／全文展開／履歴復元のトレースイベントをストリーム）は**管理型の KB のみ対応**（公式）。共有 KB（D4）は管理型ではないため現時点では使えない。https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-agentic-retrieve.html ただし**進捗イベントの設計の見本**になる。

## 3. 本当に探したい情報に早く届くか

### 3.1 新しい証拠（前回調査との重複を除く）

| 証拠 | 内容 | 注意 |
|---|---|---|
| Anthropic 多エージェント Research | 主 Opus 4＋サブ Sonnet 4 は単独 Opus 4 を内部評価で 90.2% 上回った。トークン使用量は通常チャットの約 15 倍（エージェント単体は約 4 倍）。BrowseComp の性能差の 95% を 3 要因が説明し、トークン使用量だけで 80% | ベンダーの内部評価、調査タスク。因果ではなく「多く使えば強い」の側面が強い。https://www.anthropic.com/engineering/multi-agent-research-system |
| BrowseComp-Plus（ACL 2026） | 固定コーパス約 10 万文書・830 問。GPT-5 は BM25 で 55.9%、強い埋め込み検索に替えると 70.1% で検索回数も減った。強いエージェントは検索回数を増やし、強い検索は精度と効率の両方を上げる。十分な証拠に到達できない問題が残る | 学術。検索の質がループより支配的 https://arxiv.org/pdf/2508.06600 |
| WebDetective | 取得済みの根拠を使い切れない、根拠不足でも断らない、経路を自力で見つけにくい | 要旨のみ確認。数値は **未確認** https://arxiv.org/abs/2510.05137 |
| Fishing for Answers | 法令・規制の政府文書で、1 回検索と反復検索を比較。反復側に「クエリの漂流」と「検索の怠慢」への対策を設計 | 要旨のみ。どちらが勝つかの数値は **未確認** https://arxiv.org/abs/2509.04820 |
| 産業保守・取扱説明書での比較 | 見つからなかった | **未確認** |

### 3.2 本件への正直な評価

- **効きそうな場面:** (1) 技術と法令にまたがる質問（先輩のまとめ試作の対象）、(2) 機種・制御方式が曖昧で、ノウハウの条件を読んで絞らないと別機種の資料が混ざる質問、(3) 1 回目の検索が弱く、言い換えで届く質問、(4) ノウハウに答えの手がかりがあり、原資料のページで裏づけたい質問。
- **効かない・悪化しそうな場面:** 1 資料の 1 ページで答えが出る質問（前回調査: 単一ホップで差なし〜悪化、時間 3〜9 倍）。KB が表を平文化して数値の行列が失われる、図の中の情報が入らない、といった**取り込み側の欠陥**は、ループでは直らない（BrowseComp-Plus が示す通り、検索の質の寄与が大きい）。
- **「ユーザーの想像する動き」との差:** 順番に A→B→C と探す形は遅い。独立な検索は並列にし、依存があるところ（ノウハウの機種範囲 → 技術検索の絞り込み）だけを直列にするのが、正確さと時間の両面で合理的。
- **待ち時間の見込み（仮定、未測定）:** 現行の回答生成は平均約 12 秒・最大約 17 秒。ツール選択の往復は出力が短いので数秒と仮定すると、(案内の読込 ms)＋(並列検索 数秒)＋(十分性判断 数秒)＋(最終生成 約 12 秒)＋(必要時の追加検索 1 往復) で概ね 25〜45 秒になりうる。**API Gateway REST の 29 秒に収まらない前提で設計する**（4 章）。費用は前回調査の目安（上限つき 3 検索で約 0.07〜0.10 ドル）を使い、実測で置き換える。

### 3.3 測り方（既存の評価の拡張）

既存資産: `scripts/eval/run_retrieve_eval.py`（検索の到達評価。23 問）、[golden set v2 候補](./eval-2026-09-25-golden-set-v2.md)（24 問、正解資料・保留可否は**未確定**で、mona と itai の確認待ち）、[retrievalTrace 設計](./design-2026-09-10-retrieval-trace.md)。Anthropic も約 20 件の小さな評価から始め、LLM 判定（0〜1 と合否、事実・引用・網羅・出典品質・道具の効率）に人の確認を併用している。

| 比べる腕 | 内容 |
|---|---|
| 0 | 現行の通常モード（単発） |
| 1 | 固定の並列（ノウハウ→技術＋法令を並列→まとめ）。先輩のまとめ試作に近い |
| 2 | 有界ツールループ（本調査の推奨） |

| 指標 | 方法 |
|---|---|
| 正式資料・ページへの到達率 | 既存ランナー。ノウハウだけで止まっていないか |
| 保留すべき質問で保留できたか | 設計§9.1 の受入確認（根拠なし・条件違い・古い資料・検索上限） |
| 機種の誤帰属率 | 回答中の主張の機種と、根拠の機種の突き合わせ |
| 引用の裏づけ率 | 主張ごとに根拠が支えるか（LLM 判定＋人の標本抽出）。機械検査でまず「存在しない ID」を除く |
| 検索回数・往復数・過剰検索率 | トレース。十分な後の追加検索を数える |
| 時間 p50/p95、費用/問 | トレース |
| 注入耐性 | 悪意あるカード・資料を混ぜた試験（5 章） |

層別: 単純な検索／複数資料・技術×法令／機種が曖昧／根拠なし／注入。**採否の基準は、評価の前に決めて記録する**（案: 単純な層で腕 0 に劣らず、複合層で到達率か保留の正しさが改善し、p95 が許容内）。件数が少ないため統計的な有意差は主張せず、失敗例の質的確認を併用する。

## 4. AWS で途中経過を出す方法

### 4.1 前提と確認できた事実

- **今の制約:** REST API の結合タイムアウトは 29 秒、現行は JSON の要求・応答。ブラウザは `NEXT_PUBLIC_RAG_API_URL` 経由で API を直接呼ぶ構成に見える（コード上の設定名による推測。Next.js のサーバー経由かは **未確認**）。API の公開形態（リージョナル／エッジ最適化）と CloudFront・WAF の前段の有無も **未確認**。
- **API Gateway REST のレスポンスストリーミング**（2025-11-19 発表、全リージョン）: 結合の応答転送モードを `STREAM` にする。Lambda プロキシ、HTTP プロキシ、プライベート結合のみ。最大 15 分。アイドルのタイムアウトはリージョナル／プライベートが 5 分、エッジ最適化が 30 秒。キャッシュ、内容エンコード、VTL 変換は不可。オーソライザー、WAF、スロットリング、アクセスログは使える。Lambda は `InvokeWithResponseStream` で呼ばれ、先頭に JSON のメタデータ、8 個の NUL バイトの区切り、続けて本体、の形式を出す必要がある。既存の Lambda が単に STREAM にするだけでは動かない。https://aws.amazon.com/about-aws/whats-new/2025/11/api-gateway-response-streaming-rest-apis ／ https://docs.aws.amazon.com/apigateway/latest/developerguide/response-transfer-mode.html ／ https://docs.aws.amazon.com/apigateway/latest/developerguide/response-transfer-mode-lambda.html ／ https://aws.amazon.com/blogs/compute/building-responsive-apis-with-amazon-api-gateway-response-streaming/
- **Lambda のレスポンスストリーミング:** マネージドランタイムでの対応は Node.js のみ。Python などは、カスタムランタイムか Lambda Web Adapter を使う（公式）。Function URL では VPC 内でのストリーミング不可。ストリーム中にクライアントが切断しても処理は止まらず、関数時間の全体が課金される。https://docs.aws.amazon.com/lambda/latest/dg/configuration-response-streaming.html ／ Lambda Web Adapter は `AWS_LWA_INVOKE_MODE=response_stream` で FastAPI 等のストリーミング例があるが、README に API Gateway REST のストリーミングの記載はない（**API Gateway REST ＋ LWA ＋ Python の組み合わせは未確認。PoC が必要**）。https://github.com/awslabs/aws-lambda-web-adapter
- **Lambda Function URL:** 認証は IAM か認証なしのみ（Cognito の JWT は自前検証）。CloudFront の OAC で前段に置けるが、POST では本文の SHA256 を `x-amz-content-sha256` に入れる必要があり、ブラウザからの扱いが重い。https://docs.aws.amazon.com/lambda/latest/dg/urls-auth.html ／ https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-lambda.html ／ 比較: https://docs.aws.amazon.com/lambda/latest/dg/furls-http-invoke-decision.html
- **API Gateway WebSocket API:** 接続は最大 2 時間、アイドル 10 分、メッセージ 128 KB・フレーム 32 KB（検索結果の要約。AWS ドキュメントの引用を検索要約で確認、全文は未読）。https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-execution-service-websocket-limits-table.html
- **AppSync Events:** WebSocket のパブサブ。認証は API キー・IAM・Cognito・OIDC・Lambda オーソライザー。HTTP で発行、WebSocket で購読。WAF と統合、Lambda から発行できる。料金は **未確認**。https://docs.aws.amazon.com/appsync/latest/eventapi/event-api-welcome.html
- **Bedrock Agents（従来型）:** 前回調査のとおり 2026-07-30 から新規顧客の受付停止（既存顧客は継続）。後継は AgentCore。https://docs.aws.amazon.com/bedrock/latest/userguide/agents-supported.html
- **Amazon Bedrock AgentCore:** 東京リージョンで Runtime（microVM）、Gateway、Memory、Identity、Observability が利用可（公式の対応表）。Runtime は `/invocations` で JSON または SSE、`/ws` で WebSocket。認証は SigV4 か JWT（Cognito 可、どちらか一方のみ）。要求は最大 15 分、ストリーミングは最大 60 分、非同期ジョブは最大 8 時間、ペイロード 100 MB、既定で 1 アカウント 2,500 セッション（東京）。料金は v1 で 1 vCPU 時間 0.0895 ドル、1 GB 時間 0.00945 ドル、I/O 待ちの間は CPU を課金しない。コンテナは ARM64 で作る。https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-regions.html ／ https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-service-contract.html ／ https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-oauth.html ／ https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/bedrock-agentcore-limits.html ／ https://aws.amazon.com/bedrock/agentcore/pricing/ ／ ブラウザから直接呼ぶ場合の CORS と、現行の IP 制限（WAF）との整合は **未確認**。
- **Strands Agents SDK:** Python のエージェント SDK。`stream_async` やコールバックでイベント（テキスト断片、道具使用）を受け取れる。道具使用イベントのキー名は版により異なり、現行版の正確な名前は **未確認**。https://strandsagents.com/latest/documentation/docs/user-guide/concepts/streaming/overview
- **Bedrock Converse の道具使用:** 道具使用ブロックの開始に `toolUseId` と `name` があることは API 参照で確認した。https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ToolUseBlockStart.html 入力 JSON の差分イベントの形、並列の道具呼び出し、`toolChoice` は公式ガイド（https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html ）を実装時に再確認する（今回は本文を取得できず **未確認**）。Sonnet 5 は適応的な思考で、道具呼び出しの間にも思考が挟まる（interleaved は自動）。
- **Amplify Hosting の Next.js SSR のストリーミング・タイムアウト:** 公式の記載を見つけられなかった。**未確認。** 進捗の配信を Next.js のルートハンドラー経由にしない設計にすれば、この論点を避けられる。

### 4.2 方式の比較

| 方式 | 複雑さ | Cognito＋WAF＋IP 制限との相性 | Python | 時間制約 | 運用負担 | 段階イベントの出し方 |
|---|---|---|---|---|---|---|
| ① DynamoDB の進捗記録を取りに行く（じっくりモードと同じ） | 低（既存の設計） | 変更なし（既存の REST と認可のまま） | そのまま | ジョブは非同期。1 回の要求は短い | 低〜中（ジョブ表、TTL、ワーカー） | ワーカーがステップの開始・完了を表に追記。画面は 1.5〜3 秒ごとに取得 |
| ② API Gateway REST の STREAM ＋ Python（LWA か カスタムランタイム） | 中〜高（NUL 区切りの前置き形式、LWA、PoC が要る） | オーソライザー・WAF は使える（公式）。前段の構成は未確認 | LWA が必要 | 最大 15 分、アイドル 5 分（エッジ最適化は 30 秒）。定期的な空イベントが必要 | 中 | 応答に 1 行 1 JSON（NDJSON）か SSE を書き出す |
| ③ Lambda Function URL ＋ ストリーミング | 中 | Cognito の JWT を自前検証。WAF は CloudFront 経由が必要で、POST の署名が重い | LWA が必要 | 長い | 中 | ②と同じ |
| ④ API Gateway WebSocket | 中〜高（接続管理表、@connections） | 認可は接続時のみ。WAF は可 | 可 | 接続 2 時間、アイドル 10 分 | 中〜高 | `post_to_connection` で送る |
| ⑤ AppSync Events | 中（新サービス） | Cognito 直結、WAF 統合 | 発行は HTTP で可 | 長い | 中（チームの習熟） | チャンネルに発行、画面が購読 |
| ⑥ AgentCore Runtime | 高（コンテナ・ARM64、新しい実行基盤） | JWT（Cognito）可。WAF/IP 制限との整合は未確認 | 可 | 15 分／60 分 | 高（新基盤） | SSE を返す |
| ⑦ Bedrock Agents（従来型） | — | — | — | — | 新規受付停止 | 対象外 |

### 4.3 推奨

- **第 1 候補: ① DynamoDB のジョブ＋進捗イベントの取得。** 理由: (1) じっくりモードの決定（D7・D8、受付 Lambda → ワーカー Lambda → ジョブ表）と同じ土台で、二重に作らない。(2) 認可・WAF・IP 制限・Python に手を入れない。(3) 29 秒の制約を受けない。(4) 進捗イベントの形（6 章）は輸送方式に依存しないので、後で②に差し替えられる。弱点: 取得間隔ぶんだけ表示が遅れる。最終回答の文字がぱらぱら出る体験はない（ただし待ち時間の中身を見せることが目的なので許容できる）。
- **第 2 候補: ② API Gateway REST のレスポンスストリーミング（PoC 後）。** 既存の認可と WAF を保てる公式機能で、文字の逐次表示が必要になった場合の移行先。条件: Python の方式（LWA かカスタムランタイム）での動作確認、前段の CloudFront のタイムアウト、エッジ最適化の場合は 30 秒のアイドルに対する空イベント、ブラウザ側は `fetch` ＋ `ReadableStream`（`EventSource` は Authorization ヘッダーを付けられないため）。
- **今は使わない:** AgentCore Runtime（新しい基盤を増やす価値は、多数の長時間セッションや複数エージェントが要るとき。再検討条件に記録）、API Gateway WebSocket と AppSync Events（接続・購読の運用が増える。双方向性は今の用途で要らない）、Function URL（WAF/IP 制限を迂回しやすく、署名が重い）。
- **エージェントの実装:** まず Bedrock Converse の道具使用を素手で回す（約 100 行。Anthropic も「まず LLM の API を直接使い、抽象化を減らす」ことを勧める）。Strands は、道具やイベントの管理が増えたときの選択肢。**段階イベントはモデルの出力から作らず、アプリ側が道具を実行する前後に作る**（ラベルと件数は自前で生成。生の思考を表示に混ぜない）。

## 5. 安全性と品質

| 論点 | 方針 | 根拠 |
|---|---|---|
| 生の思考を見せない | 画面に出すのは、アプリが作る道具ステップの要約のみ。Claude の思考は API が返すのも要約で、さらに表示・保存を運用の前提にしない（設計§9.1） | 公式文書（上記）、設計§9.1 |
| 間接プロンプトインジェクション | 検索結果・カード本文・将来の OneNote 内容は「資料」として明示的に囲み、命令として扱わない。道具は読み取り専用、出力形式をコードで検証、人の承認が要る操作はそもそも持たせない | OWASP LLM01（緩和策: 役割の限定、出力形式の検証、入出力のフィルタ、最小権限、人の承認、外部コンテンツの分離、敵対的試験）https://genai.owasp.org/llmrisk/llm01-prompt-injection/ |
| 致命的な三点 | 機密データへのアクセス、攻撃者が書ける入力、外部への送信手段の 3 つが揃うと情報が漏れる。**本件は 3 つ目（Web・URL 取得・書き込み・メール送信）を持たせない**ことで避ける | 提唱者の整理 https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/ |
| 利用者ごとの認可 | `userId`・権限・機種範囲はサーバーがセッションから注入。モデルが渡す引数には含めない。失効した公開版・権限外資料は返さず、存在も漏らさない | 設計§9.1、AGENTS.md |
| 費用の上限 | 道具・往復・時間・トークンを道具側とワーカー側で二重に制限。1 人 1 日の回数制限（D2）を流用 | 2.4 |
| ログ | 道具名、結果件数、資料 ID・版、時間、終了理由のみ。検索語の全文・ナレッジ引用全文・回答本文は出さない（CloudWatch に引用全文を出さない原則）。Anthropic も会話の中身を見ずに判断パターンだけを追跡 | AGENTS.md、Anthropic 記事 |
| 人が確認できる引用 | 主張ごとに資料 ID・ページ・版を付け、アプリ側でその ID が取得結果に実在するか検査。引用があっても裏づけの保証にならない（1.2 の 51.5%） | 論文 |
| 止めて利用者に聞く | 機種・制御方式が不明で結果が機種により変わる／ノウハウの条件と質問が食い違う／正式資料に届かず安全に関わる数値を答える必要がある／道具が上限に達し根拠が混在、のとき。聞く内容は利用者が答えられる具体的な質問にする | 設計§9.1 |
| 未承認カード | カードは全件が下書き。回答では「ノウハウ（未承認・参考）」と明示し、正式な値は原資料で確認できた場合のみ断定する | 先輩のまとめ試作、設計§9.1 |

## 6. 先輩チャットへの具体案

### 6.1 構成（テキスト図）

```text
[ブラウザ] --(JWT)--> [API Gateway REST] -> [受付Lambda] --非同期起動--> [ワーカーLambda]
   ^   (1.5-3秒ごとに GET /jobs/{id}?after=seq)       |                       |
   |                                                    v                       v
   +<-------------- [DynamoDB: ジョブ表 + steps(seq,...)]  <---- 追記 ---- [有界ツールループ]
                                                                                 |
   0. 案内を読む  knowhow_find (LLMなし, 字句)  --> カード要約 N件 (機種範囲・制御方式・出典番号)
   1. 並列        tech_search(機種絞り込み) || law_search      (独立なので同時)
   2. 判断(1往復) 十分か? 不足 → 言い換え / 別の道具 / ask_user  (合計の上限つき)
   3. まとめ      主張→根拠ID の構造化出力 → アプリ側で実在検査 → 回答 + 出典
```

「案内を先に読む」は**アプリ側が必ず先に実行**する（モデルの判断に任せない）。ノウハウは機種・制御方式の範囲と出典の資料番号を運ぶので、技術検索の絞り込みに使える（依存があるのでここだけ直列）。技術と法令は独立なので並列。

### 6.2 段階イベントの形（案）

```json
{
  "jobId": "…", "seq": 7, "step": "tech_search", "tool": "tech_search",
  "labelJa": "技術資料を検索中", "detailJa": "「…（検索語・短縮・資料内容は含めない設定も可）」",
  "status": "running | done | failed | skipped | budget_exhausted",
  "counts": { "hits": 8, "selected": 4, "documents": 3 },
  "startedAt": "2026-10-20T09:00:01.234Z", "endedAt": null,
  "reason": null
}
```

- `labelJa` は道具名ごとの固定文言（例: 「ノウハウを確認中」「技術資料で検索中」「法令を確認中」「足りない点を再検索中」「まとめ中」「利用者への確認待ち」）。`detailJa` は検索語を出す場合に長さを制限し、利用者本人にだけ返す。
- 保存・ログ用の別形式では、検索語と本文を持たず、`tool`・件数・時間・資料 ID・終了理由だけにする（5 章）。
- 追記専用で `seq` を単調増加にし、画面は `after=seq` で差分取得する。完了時に `type: "final"` で回答・出典・未確認点・ノウハウの状態を返す。

### 6.3 画面（案）

- **一般の利用者:** 統合した 1 つの回答、完了後に折りたたまれる**ステップの時系列**（Glean の計画カードに近い。単純な質問では出さないか短く）、出典一覧（資料名・ページ・版・ノウハウは「未承認・参考」の印）、確認できなかった点と次に確認すること。生の思考と道具の生出力は出さない。10 秒を超える待ちでは完了割合ではなく、処理した項目を名指しする進捗（NN/g の指針）。
- **開発者表示（admin、dev のみ）:** 道具ごとの入力・出力の件数、score、除外理由、`retrievalTrace`（既存設計）への入口、予算の消費、各レーンの生の結果。

### 6.4 予算（初期案、実測で調整）

| 項目 | 初期値 | 備考 |
|---|---|---|
| 検索系の道具 | 合計 6 回 | 同一検索語・同一結果は拒否 |
| モデル往復 | 4 回 | 最終生成を含む |
| ジョブ全体 | 60 秒 | じっくりモード（180 秒）より短く |
| 費用 | 0.30 ドル/ジョブ | じっくりモードの上限 0.60 ドルの半分。Bedrock 上の正式単価は未確認 |
| 利用回数 | 通常の先輩チャット枠と別に管理 | D2 の枠を共有するか別枠にするかは決定事項 |
| 終了条件 | 新資料なしが 2 往復、十分性の充足、予算切れ、`ask_user` | 予算切れは「確認できた範囲と不足」を返す |

### 6.5 D1〜D8 との関係

| 決定 | 関係 |
|---|---|
| D1 2 モード | 先輩チャットは通常モード（単発）に残すか、独立した第 3 の入口にするかを決める。新しい入口は D1 の整理を更新する |
| D2 回数 | ツールループは 1 回の費用が大きいので、回数枠を別立てするか既存枠に含めるか決める |
| D3 既定 OFF | 維持。新機能は既定 OFF の機能フラグで入れる |
| D4 共有 KB | 維持。Managed KB の `AgenticRetrieveStream` は使えない（管理型のみ）。KB 側の欠陥（表の平文化など）は、改善要望の実例として [kb-change-requests.md](./kb-change-requests.md) に蓄積 |
| D5 KB プロファイル | `tech_search` / `law_search` は KB プロファイル経由にし、差し替え可能にする |
| D6 固定ワークフロー | **ここが論点。** じっくりモードは固定の流れの単一 AI で、マルチエージェントではない、と決めた。有界ツールループは単一 AI だが、手順を AI が選ぶ。マルチエージェントでないので `PRODUCT_INTENT.md` の方針には反しないが、D6 の「固定ワークフロー」の前提は変わる。**新しい共同決定（D9 案）が必要**: 「先輩チャットは、dev の `beta` に限り、単一 AI の有界ツールループ（上限つき、読み取り専用、案内先読み）を試行する。評価で腕 1（固定の並列）より良くなければ止める」 |
| D7 機能フラグ・開発中表示 | 同じ `off` / `beta` / `on` を使い、画面に「開発中」と出す |
| D8 評価を待たず dev で試行 | 同じ進め方を踏襲 |

**業務スコープ変更の共同確認（AGENTS.md）:** 検索・表示・利用の対象資料・機種・部門・利用者を変えない限り対象外。ただし (a) 下書きカードを一般利用者に出す、(b) OneNote / Lists を道具にする、を行う場合は別途、共同確認と記録が必要。

### 6.6 段階計画

| 段階 | 内容 | 判断材料 |
|---|---|---|
| P0 | golden set v2 の 24 問のラベル確定（mona と itai）。腕 0 の基準値を取る | 到達率、保留、時間、費用 |
| P1 | **段階イベント＋取得方式を、今の固定の並列（先輩のまとめ試作）に付ける。** モデルの挙動を変えずに待ち時間の体験だけ改善 | 利用者の反応、離脱 |
| P2 | dev の `mona` ブランチ上に有界ツールループを実装（機能フラグ、既定 OFF）。SAM のデプロイは itai | 道具呼び出しの質、予算の妥当性 |
| P3 | 腕 0・1・2 を P0 の評価で比較。注入試験を含める | 3.3 の基準 |
| P4 | D9 の採否を mona・itai で決定 | 継続／止める／ノウハウ範囲の拡大 |
| P5（任意） | ストリーミング（②）の PoC。文字の逐次表示が必要と分かった場合のみ | Python の方式、タイムアウト |

### 6.7 リスク

| リスク | 対応 |
|---|---|
| ループが遅く、29 秒を超える | 非同期ジョブで受ける。往復数と時間を制限し、並列化する |
| 検索のしすぎ・同じ検索の繰り返し | 重複拒否、新資料なし 2 往復で終了、予算切れでも回答する |
| 下書きカードを根拠のように述べる | 「未承認・参考」の印を出力検査で強制、正式な値は原資料で確認できたときだけ |
| 注入（カード・資料の命令） | 5 章。悪意のある資料での試験を P3 に含める |
| 進捗表示が実態とずれる | イベントは道具の実行前後にアプリ側で生成。モデルの文章から作らない |
| 評価が小さく、結論が揺れる | 層別の失敗例を人が読む。採否の基準を事前に記録 |
| 費用が想定を超える | 道具側とワーカー側の二重上限、1 日の回数制限 |
| KB の欠陥が支配的で、ループの効果が見えない | 腕 1 と 2 の差だけでなく、失敗の原因分類（検索／利用／拒否）で見る |
| 新サービスを増やして運用が増える | まず①。AgentCore などは再検討条件に記録 |

## 7. 未確認事項

- ChatGPT / Perplexity / Microsoft 365 Copilot の画面の見せ方の一次情報（公式文書が取得できず、二次または概要のみ）
- OpenAI が生の思考を見せない理由と、要約の仕様（一次情報）
- API Gateway REST の STREAM ＋ Python Lambda（LWA／カスタムランタイム）の実動作、必要な前置き形式の実装細部
- 現行 API の公開形態（リージョナル／エッジ最適化）、CloudFront・WAF の前段の有無、ブラウザからの呼び出し経路（Next.js 経由か直接か）
- Amplify Hosting の Next.js SSR のストリーミング対応と要求の時間制限
- AppSync Events の料金、AgentCore の WAF/IP 制限との整合、ブラウザからの CORS
- Bedrock Converse の道具使用ストリームの入力差分イベントの形、並列呼び出し、`toolChoice` の対応（今回は本文を取得できず）
- Strands の現行版の道具使用イベントのキー名
- WebDetective・Fishing for Answers の数値、産業保守・取扱説明書での反復検索の比較研究
- 仮想エージェント研究（arXiv:2507.22352）の「人工的な待機表示は有意でない」という要約の原文での確認、arXiv:2604.06183 の書誌（番号と投稿日の食い違い）、参加人数
- 本システムでの、ツール選択の往復の所要時間、ノウハウ字句検索の実測時間、Bedrock 上の Sonnet 5 の正式単価
- 工事技術の質問でのループの効果（未測定。3.3 の評価が最初の実測）

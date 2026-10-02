# 実装ログ: RAG retrieval layer（2026-09-24）

> **目的:** 通常モードの既定挙動を維持したまま、KB差し替え・検索語書き換え・リランクの評価基盤を追加する。

## 方針

この変更は通常モードの改善土台であり、既定値では既存のRetrieve引数、フィルタ、閾値、
弱検索ゲート、回答生成の挙動を維持する。KBごとの差分は `KbProfile` に集約し、
`KB_PROFILE_JSON` で必要な項目だけを上書きできるようにした。

`model_type_key` または `category_key` を変えるときは、必ず実データでキーの存在と値を確認すること。
`model_type_key` が欠落した結果は、既存仕様どおり全機種共通扱いになるため、欠落を許容してはいけない。

リランクはKnowledge Base Retrieveの設定に埋め込まず、Retrieve後にBedrock Agent Runtime
のRerank APIを別呼び出しする。これにより、現行のハイブリッド検索 `score` と閾値
（0.22 / 0.3）を保ったまま、選択時の並び順だけを評価できる。失敗時は元のscore順へ戻る。

## 有効化パラメータ

既定ではすべて現行互換またはOFFである。ONにする前に、通常モードの検索正解率、
弱検索ゲート、引用の妥当性、回答品質、レイテンシ、Bedrock費用を実データで比較する。

| Parameter / Environment | 既定値 | 用途 |
| --- | --- | --- |
| `KbProfileJson` / `KB_PROFILE_JSON` | 空 | KBメタデータ契約のJSON上書き |
| `RerankModelArn` / `RERANK_MODEL_ARN` | 空 | 別呼び出しのRerankを有効化 |
| `RerankMaxCandidates` / `RERANK_MAX_CANDIDATES` | `30` | リランク対象のテキストチャンク上限 |
| `QueryRewriteModelId` / `QUERY_REWRITE_MODEL_ID` | 空 | 会話を踏まえた検索語書き換え |
| — / `OPTIONAL_FEATURE_RESERVE_SECONDS` | `18` | 任意呼び出し後に残す生成・保存の予備時間（秒） |
| `GenerationThinking` / `GENERATION_THINKING` | `disabled` | 新APIモデルのthinking設定 |
| `GenerationEffort` / `GENERATION_EFFORT` | `low` | adaptive thinkingの `output_config.effort` |

評価で差分を確認した後、SAMのパラメータを指定して段階的に有効化する。Rerankを有効に
する場合はRerankモデルARNに対する `bedrock:InvokeModel` と `bedrock:Rerank` の権限が
配線される。クエリ書き換えは履歴・質問をデータとしてモデルへ渡し、1行200文字以内の
検証に失敗した場合は元の検索語を使う。thinkingのeffortはBedrockの書式に従い、
`thinking` の中ではなく `output_config` に置く。

検索語書き換えとリランクは、呼び出しの最大時間と生成・保存の予備時間（既定18秒）が
応答 deadline に収まらない場合は呼び出さず、元の検索結果・検索語へフォールバックする。

## 確認手順

1. 既定値でunit test全件とSAMテンプレート検査を実行し、既存パリティテストを確認する。
2. 検証用環境だけで1機能ずつONにし、同じ質問集合で検索結果、回答、引用、弱検索判定、
   p95レイテンシ、エラー率、費用を比較する。
3. 期待する改善とフォールバック動作を確認してから、対象環境のパラメータを更新する。

## 参照

- [Amazon Bedrock Rerank API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Rerank.html)
- [Permissions for reranking in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank-prereq.html)
- [Adaptive thinking - Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html)

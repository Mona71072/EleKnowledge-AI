---
status: development
phase: 3
last-verified: 2026-05-26
related-code: lambda/troubleshooting/, frontend/src/app/troubleshooting/, infrastructure/sam/phase3-template.yaml
---

# トラブルシュートエージェント 処理シーケンス

> **状態:** Phase 3 の開発・参照資料。2026-09-30 に AWS stack / API / Lambda / table の存在は確認したが、利用者向け提供と現在の全フローは未確認。過去の PoC E2E 記録はその確認時点の結果であり、現在の提供状態を示さない。

> 最終検証: 2026-09-30 — AWS CloudFormation による Phase 3 リソース存在のみ。シーケンスの全機能・利用者向け E2E は未検証。

## 概要

Bedrock Agent を中心に、ユーザ入力・DB取得結果・KB検索結果を条件として次アクションを制御し、観点別に整理した回答と引用元バッジ付きドキュメントを提供する。

---

## 処理シーケンス図

```mermaid
sequenceDiagram
    autonumber
    actor User as ユーザー
    participant FE as Frontend<br/>(Next.js)
    participant APIGW as API Gateway<br/>troubleshooting-api
    participant Auth as Authorizer Lambda<br/>(JWT検証)
    participant Orch as Orchestrator Lambda
    participant Agent as Bedrock Agent<br/>(D6FAGLJPPO)
    participant DBSearch as db-search Lambda<br/>(① GetSiteInfo)
    participant KB1 as kb-search-cases-{env} Lambda<br/>(② searchTroubleCases)
    participant KB2 as kb-search-manuals-{env} Lambda<br/>(③ searchTroubleshootManuals)
    participant KB3 as kb-search-materials-{env} Lambda<br/>(④ searchCMaterialDocs)
    participant DDB as DynamoDB<br/>(sessions / sites)
    participant KB as Bedrock<br/>Knowledge Base
    participant S3 as S3<br/>(ドキュメント)

    %% ─── ユーザー入力 ───
    User->>FE: 工事番号（任意）・機種（任意）・不具合内容・エラーコード（任意）を入力
    FE->>FE: フロント側バリデーション
    FE->>APIGW: POST /analyze<br/>Authorization: Bearer {CognitoIDToken}

    %% ─── 認証 ───
    APIGW->>Auth: Token Authorizer 呼び出し
    Auth->>Auth: JWKS取得（Cognito）・RS256検証<br/>sub → userId 抽出
    Auth-->>APIGW: Allow policy + context.userId

    %% ─── Orchestrator 前処理 ───
    APIGW->>Orch: invoke（userId が context に付与済み）
    Orch->>Orch: validate_input()<br/>・不具合内容 (5〜2000文字) は必須<br/>・工事番号・機種・エラーコードは任意
    Orch->>DDB: init_session()<br/>sessions-{env} に空レコード作成（TTL: 30日）
    Orch->>Orch: format_agent_input()<br/>各入力値の有無を明示した日本語プロンプトを整形

    %% ─── Bedrock Agent 呼び出し ───
    Orch->>Agent: invoke_agent()<br/>agentId / aliasId / sessionId<br/>sessionAttributes: {session_id}

    Note over Agent: ReAct ループ開始<br/>（各ステップの結果を観察して次アクションを決定）

    %% ─── ① サイト情報取得（条件付き）───
    opt 工事番号がユーザ入力に含まれる場合のみ実行
        Agent->>DBSearch: ① GetSiteInfo<br/>constructionNumber
        DBSearch->>DDB: Get_item（sites テーブル）
        DDB-->>DBSearch: 現場名・現場番号・機種・制御システム・担当者
        DBSearch-->>Agent: 構造化サイト情報<br/>{ siteName, model, controlSystem, ... }
        Note over Agent: 機種 = ①で取得した値を優先採用
    end

    Note over Agent: 一時対応として controlSystem=VFGLF を固定使用<br/>エラーコードを確定（ユーザ入力値 or なし）

    %% ─── ② トラブル事例検索 ───
    Agent->>KB1: ② searchTroubleCases<br/>query = 不具合内容<br/>controlSystem = VFGLF<br/>errorCode = 確定済みエラーコード（任意）
    KB1->>KB1: build_metadata_filter()<br/>control-system・errorCode でフィルター構築
    KB1->>KB: retrieve() セマンティック検索<br/>（Trouble-Cases / Trouble-Reports）上位5件
    KB-->>KB1: 検索結果
    KB1->>DDB: write_citations()<br/>source_action = "trouble_cases" タグ付きで保存
    KB1-->>Agent: トラブル事例テキスト（上位5件）

    %% ─── ③トラブルシュートマニュアル検索 ───
    Agent->>KB2: ③ searchTroubleshootManuals<br/>query = 不具合内容<br/>controlSystem = VFGLF<br/>errorCode = 確定済みエラーコード（任意）
    KB2->>KB2: build_metadata_filter()<br/>control-system・errorCode でフィルター構築
    KB2->>KB: retrieve() セマンティック検索<br/>（マニュアル）上位3件
    KB-->>KB2: 検索結果
    KB2->>DDB: write_citations()<br/>source_action = "manual" タグ付きで保存 ★新規追加
    KB2-->>Agent: マニュアルテキスト（上位3件）

    %% ─── ④ C資料検索 ───
    Note over Agent: ②③の結果テキストから<br/>C資料検索用キーワードを抽出・生成
    Agent->>KB3: ④ searchCMaterialDocs<br/>query = ②③結果から抽出したキーワード<br/>model = 確定済み機種（任意）
    KB3->>KB3: build_metadata_filter()<br/>model・document=C資料 でフィルター構築
    KB3->>KB: retrieve() セマンティック検索<br/>（C資料）上位5件
    KB-->>KB3: 検索結果
    KB3->>DDB: write_citations()<br/>source_action = "c_material" タグ付きで保存
    KB3-->>Agent: C資料テキスト（上位5件）

    %% ─── ⑤ 回答生成 ───
    Note over Agent: ReAct ループ終了 → 回答生成フェーズへ
    Agent->>Agent: ⑤ 回答生成（Claude Haiku）<br/>【サイト情報】①で取得した現場・機種情報を整理<br/>【トラブル事例】②をもとに類似事例・過去対処を提示<br/>【マニュアル】③をもとに推奨手順を提示<br/>【C資料】④をもとに技術詳細・部品情報を提示<br/>【推奨アクション】①〜④を総合した具体的対処手順

    %% ─── Orchestrator 後処理 ───
    Agent-->>Orch: EventStream（チャンク + 引用情報）
    Orch->>Orch: parse_agent_response()<br/>テキストチャンクと引用情報を抽出
    Orch->>DDB: fetch_citations()<br/>source_action フィールドを含む全引用情報を取得
    Orch->>S3: _presign_source_uri()<br/>各ドキュメントの署名付きURL生成（有効期限: 30日）
    S3-->>Orch: 署名付きURL
    Orch->>Orch: build_source_documents()<br/>EventStream引用 + DDB引用をマージ<br/>source_action フィールドを保持
    Orch->>DDB: save_session_result()<br/>result・sourceDocuments（source_action付き）を保存

    %% ─── レスポンス ───
    Orch-->>APIGW: JSON レスポンス
    APIGW-->>FE: 200 OK<br/>{sessionId, result, sourceDocuments[{..., source_action}]}
    FE->>User: 観点別セクション（サイト情報・トラブル事例・マニュアル・C資料・推奨アクション）<br/>引用ドキュメントに ② ③ ④ バッジを表示
```

---

## 条件分岐サマリ

| アクション | 実行条件 | 検索クエリ | フィルター |
|---|---|---|---|
| ① GetSiteInfo | 工事番号あり | constructionNumber | — |
| ② searchTroubleCases | 常に実行 | 不具合内容 | control-system=VFGLF ＋ エラーコード（あれば） |
| ③ searchTroubleshootManuals | 常に実行 | 不具合内容 | control-system=VFGLF ＋ エラーコード（あれば） |
| ④ searchCMaterialDocs | 常に実行 | ②③結果からAgentが抽出したキーワード | control-system=VFGLF |

## 機種（model）の優先順位

```
① GetSiteInfo の取得値
      ↓ なければ
ユーザ入力の機種
      ↓ なければ
フィルターなしで検索
```

## source_action タグと UI バッジの対応

| source_action | UI バッジ | 取得元 |
|---|---|---|
| `trouble_cases` | ② | `kb-search-cases-{env}` Lambda |
| `manual` | ③ | `kb-search-manuals-{env}` Lambda（★ write_citations を新規追加） |
| `c_material` | ④ | `kb-search-materials-{env}` Lambda |

> サイト情報（①）はドキュメント引用ではなく DB テキストのため、バッジ対象外。回答本文の「サイト情報」セクションに表示する。

## 既存実装からの主な変更点

| 変更対象 | 変更内容 |
|---|---|
| Bedrock Agent システムプロンプト | 条件分岐ロジック・機種優先順位・④のクエリ生成方法を指示として追加 |
| kb-search1 | citations に `source_action = "trouble_cases"` を追加 |
| kb-search2 | `write_citations()` を新規実装、`source_action = "manual"` を付与 |
| kb-search3 | citations に `source_action = "c_material"` を追加 |
| orchestrator | `build_source_documents()` で `source_action` フィールドを保持 |
| frontend | sourceDocuments の `source_action` を元に ② ③ ④ バッジを表示 |

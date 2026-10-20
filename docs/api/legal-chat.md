---
status: development
last-verified: 2026-10-09
related-code: lambda/rag/rag-function/app.py, lambda/chat/chat-management/app.py, frontend/src/app/chat/page.tsx, frontend/src/app/admin/failures/page.tsx, infrastructure/sam/phase2-template.yaml
---

# 法令チャット API補足（developプレリリース）

**目的:** developにマージされた法令チャットの入出力・履歴分離を、現行コードに合わせて定義する。

**範囲:** [RAG API](rag.md)と[チャット管理API](chat.md)の法令モード追加分。照合元はdevelop `b8070f56`（#155 / #156を含む）。実AWS反映・実画面確認の結果は[プレリリース確認記録](../verification-2026-10-09-legal-chat-prerelease.md)で管理し、本書のコード照合をデプロイ済みの証拠にしない。対象法令・利用者・費用条件は[対象一覧](../features/development/legal-rag-target-laws.md)を正とする。

## POST /rag/query

> 最終検証: 2026-10-14 — develop `20871803`（#172）のmode正規化・セッション読取失敗の500をコードと照合。AWSへの反映・実操作はこの照合の対象外。

URLとCognito認証は既存RAG APIを使用する。userIdは検証済みJWTのsubから取得し、本文のuserIdは認可に使わない。

```json
{
  "sessionId": null,
  "query": "労働安全衛生規則第518条の規定を確認したい",
  "mode": "law",
  "filters": {}
}
```

| 項目 | 実装契約 |
| --- | --- |
| 本文 | JSON object。JSON不正・配列・スカラー等は400 `ValidationError` |
| `query` | 必須、空白だけでない文字列、最大2000文字 |
| `sessionId` | 新規は省略またはnull。指定するなら空でない文字列、最大128文字。所有する既存lawセッションだけを再利用できる |
| `mode` | `law`を指定。省略・null・空文字は`normal`。`spec`は従来互換で`normal`へ正規化。未知値・非文字列は400 `ValidationError` |
| `filters` | 省略・nullは空object。非objectは400。既存category / modelTypeの型を検証した後、lawでは空に正規化し検索に使わない |
| 法令ID・分野の指定 | 専用フィルターは未実装。`filters.lawId` / `filters.legalTopics`を有効な絞り込みとして案内しない。法令名や条番号はqueryに書く |
| 基準日 | `asOfDate`による版選択は未実装。2026-10-01基準の収録スナップショットを検索し、過去時点の適用を保証しない |

法令APIは`ENVIRONMENT=dev`かつ`LAW_RAG_ENABLED=true`かつ`LAW_KNOWLEDGE_BASE_ID`ありの場合だけ許可し、条件不成立は403 `FeatureUnavailable`（「法令モードは利用できません」）。法令専用Managed KBへ`managedSearchConfiguration`で検索し、`source_type=law` / `status=current` / `document_granularity=provision_unit`を要求する。取得後も新形式の条文本文を検証し、通常KBへフォールバックしない。

既存セッションが存在しない・所有しない場合は404 `NotFound`。所有するセッションでも保存modeが異なる場合は409 `SessionModeMismatch`。所有者・モード・履歴の読取りに失敗して確認できない場合は、404や空履歴にせず一般化した500を返す（#172）。法令・通常の履歴を生成コンテキストへ混ぜない。

全文補完はdev限定の実験であり、有効かどうかはphase2の設定次第。#177反映後は法令ゲートが有効で、`LawDataBucketName`が指定されている場合に有効になる。顧客管理KMSキーを使う場合だけ`LawDataBucketKmsKeyArn`を指定する。#177のマージだけではAWSの設定は変わらず、反映結果は[確認記録](../verification-2026-10-09-legal-chat-prerelease.md)へ別途記録する。

## 応答と法令出典

共通のsession / message ID、`responseType`、`content`、`sourceDocuments`等は既存形式を使う。次は法令出典1件の形を示す例で、特定の回答・検索スコアを保証するものではない。

```json
{
  "documentName": "昭和四十七年労働省令第三十二号 第518条",
  "title": "労働安全衛生規則",
  "sourceUri": "https://laws.e-gov.go.jp/law/347M50002000032",
  "category": "法令",
  "modelType": "",
  "relevance": 0.8,
  "lawCitation": {
    "lawId": "347M50002000032",
    "lawTitle": "労働安全衛生規則",
    "lawNumber": "昭和四十七年労働省令第三十二号",
    "effectiveDate": "YYYY-MM-DD",
    "provisionType": "main",
    "provisionReference": "第518条",
    "sourceUrl": "https://laws.e-gov.go.jp/law/347M50002000032"
  },
  "referenceCoverage": "full",
  "referenceCoverageReason": "complete"
}
```

- `sourceUri`と`lawCitation.sourceUrl`はe-GovのHTTPS URL。通常資料の内部S3 URI・`/doc`・署名付きPDF URLと区別する。実際の施行版URL・条文アンカーはmetadataの値を返し、`effectiveDate`は実際の施行日を返す。
- `provisionReference`は特定できる場合だけ付く。範囲指定や附則等で直接リンクを保証できない場合は法令全体へのリンクを使い、推定アンカーを作らない。
- `referenceCoverage` / `referenceCoverageReason`は参照補完処理の結果がある場合だけ付く。`full` / `partial`は取得した参照本文の範囲であり、法令全体の網羅や法的正確性の認定ではない。reasonは診断値として扱う。
- UIは法令名・法令番号・特定できた条文・施行日・e-Govリンクを表示する。加工事実と主体（Ele-Knowledge）の表示は設計書 §8.2を参照する。
- 施行日前後の版選択、対象外質問の案内、適用判断の品質はコード照合だけで確認済みにせず、受入確認で検証する。

## チャット履歴・評価・管理者の失敗一覧

> 最終検証: 2026-10-14 — #171・#174のdevelopマージとURLのmode引継ぎ・関連セッションmode保存をコードで照合。AWS反映・管理者画面の再表示成功は未確認。

| 操作 | 実装契約 |
| --- | --- |
| メッセージ保存 | user / assistantに`ragMode: normal|law`を保存。旧データの未設定値はnormal扱い。sourceDocumentsの法令出典も保存 |
| `GET /chat/sessions?mode=law` | 自分のlaw履歴。`normal`なら通常のみ、省略時は既存互換で全モード。未知値は400。各セッションに`ragMode`を返す |
| `GET /chat/sessions/{sessionId}/messages?mode=law` | 保存modeが違えば409。mode省略は既存互換。所有者以外の一般利用者は404。既存の管理者読取りは`readOnly=true`で維持 |
| `DELETE /chat/sessions/{sessionId}` | 既存の所有者限定削除。法令モード専用の削除APIは増やさない |
| 評価・要望 | 既存APIを使用。認可・文字数等の既存契約を維持 |
| 失敗一覧 | 項目に`ragMode`を返し、法令会話のリンクに`mode=law`を引き継ぐ。旧データはnormal |

URLのmodeが反映される前に履歴を取得して409になる問題の修正は[#171](https://github.com/yukiworkspace/EleKnowledge-AI/pull/171)で、要望の関連セッションのmode保存・返却は[#174](https://github.com/yukiworkspace/EleKnowledge-AI/pull/174)で、いずれも2026-10-10 JSTにdevelopへマージ済み。マージ済みであることと、Amplify・Lambdaへの反映および管理者画面での再表示成功は区別して記録する。

各メッセージのTTLは作成時から60日で、追質問しても古いメッセージの期限は延びない。通常チャットと法令チャットは入口・履歴が別であり、「通常／じっくり」という回答の深さとは別の軸である。

## 検証・運用への入口

- [公開・受入確認手順](../legal-chat-prerelease.md)
- [今回の確認記録](../verification-2026-10-09-legal-chat-prerelease.md)
- [法令RAG設計](../features/development/legal-rag-design.md)
- [対象法令一覧](../features/development/legal-rag-target-laws.md)

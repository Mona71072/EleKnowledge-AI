---
status: development
phase: 3
last-verified: 2026-10-01
related-code: infrastructure/sam/phase2-template.yaml, lambda/rag/rag-function/app.py
---

# 法令RAG データ基盤・検索設計

## 1. 目的

e-Gov法令検索から取得した法令を、昇降機の設置・建築、据付作業、労働安全、電気工事、改修・撤去に関する質問の根拠として検索できるようにする。

本設計は開発・検証用の設計であり、対象法令、自治体条例、告示、通知、業界標準の追加範囲は業務部門の確認を前提とする。

## 2. 設計判断

| 項目 | 方針 |
|---|---|
| 保存先 | 法令専用S3バケットを新設する |
| Knowledge Base | 既存の共有Knowledge Baseとは分離し、法令専用Knowledge Baseを作る |
| 原文 | e-Gov XMLを改変せず保存する |
| 検索本文 | XMLから条・項・号の構造を維持したUTF-8 TXTまたはMarkdownを生成する |
| メタデータ | 法令専用項目を追加し、既存KBの`category`、`model_type`等は変更しない |
| 検索経路 | 通常RAGと法令RAGを分離する |
| 出典 | 回答にはe-Govの本文URLを表示し、S3の派生本文を一次情報として扱わない |
| 版選択 | 質問の基準日時点で施行済みの最新版を選択する |

### 2.1 推奨する初期構成

| 項目 | 推奨値 |
|---|---|
| S3 | 法令専用バケット（開発・本番で分離） |
| KBデータソース | 法令専用KBに1つだけ作成 |
| S3データソースprefix | `kb/egov/` |
| S3原文prefix | `raw/egov/`（KBの対象外） |
| 検索本文 | UTF-8 TXT（条文構造を見出しで保持） |
| メタデータ | `<本文ファイル名>.metadata.json`を本文と同じprefixに配置 |
| 版管理 | `effective_date`で現行・未施行・過去を識別 |
| 出典 | e-Gov本文URLをメタデータと回答に保持 |

原文と検索本文を同一バケットに置く場合でも、Knowledge BaseのS3データソースは`kb/egov/`だけを対象にする。バケット全体を対象にして`raw/`のXMLを誤って取り込まない。

既存KBは外部スタック所有であり、社内資料、quick-start、web-crawler等のデータソースと共有されている。法令を同じKBへ追加すると検索境界、Sync、運用責任が混在するため、本番構成では分離する。

## 3. 論理構成

```text
e-Gov API / XML一括ダウンロード
        |
        v
  取得・検証ジョブ
        |
        +--> raw/       XML原文（不変・履歴保持）
        +--> kb/        検索用TXT/Markdown
        +--> metadata/  Bedrockメタデータ
        +--> manifest/  取得・版・ハッシュ台帳
                         |
                         v
              法令専用Knowledge Base
                         |
                         v
             法令検索モード / 法令Agent
                         |
                         v
              e-Gov本文URL付き回答
```

## 4. S3構成

```text
s3://<law-rag-bucket>/
├── raw/egov/<law-id>/<version-folder>.xml
├── kb/egov/<law-id>/<version-folder>.txt
├── kb/egov/<law-id>/<version-folder>.txt.metadata.json
├── manifest/laws.csv
└── quarantine/<run-id>/
```

`.metadata.json`は、対応する本文ファイルと同じディレクトリに置くBedrock Knowledge Basesのサイドカーファイルである。`metadata/`など別prefixに分けると、本文との対応付けができず、Knowledge Baseの文書メタデータとして扱われないため、この配置を固定する。

`version-folder`は、e-Gov一括ダウンロードのフォルダ名を使用する。例:

```text
322AC0000000149_20250601_504AC0000000068
```

S3バケットでは次を有効化する。

- Block Public Access
- Versioning
- SSE-KMS
- CloudTrail data events（本番で必要な場合）
- ライフサイクルルール（rawは長期保持、quarantineは短期保持）
- 本番書き込み主体とKB読み取り主体のIAM分離

## 5. XMLから検索本文への変換

Amazon Bedrock Knowledge BasesのS3データソースはXMLを対応する検索本文形式として扱わないため、XMLをそのままKBの検索対象にしない。XMLは原文保管用とし、検索用にTXTまたはMarkdownを生成する。

変換時は次を保持する。

- 法令名
- 法令ID
- 法令種別
- 施行日
- 編・章・節
- 条・項・号
- 附則
- 経過措置
- 改正法令情報

生成例:

```text
【法令名】建築基準法施行令
【法令ID】325CO0000000338
【施行日】2025-12-01
【出典】https://laws.e-gov.go.jp/law/325CO0000000338/20251201_507CO0000000377

第三章 建築設備

第百二十九条の三　...
```

本則、附則、経過措置は検索上区別できるよう、本文中の見出しとメタデータの両方で表現する。

## 6. メタデータ

既存の`category`、`model_type`、`document`、`product`、`department`の意味・型・値は変更しない。法令専用KBでは、法令用に次の属性を追加する。

| 属性 | 型 | 用途 |
|---|---|---|
| `source_type` | STRING | `law`を設定し、法令資料を識別する |
| `law_id` | STRING | e-Gov法令ID |
| `law_title` | STRING | 法令名 |
| `law_type` | STRING | 法律、政令、府省令等 |
| `law_number` | STRING | 法令番号 |
| `effective_date` | STRING | ISO形式の施行日。例:`2025-12-01` |
| `promulgation_date` | STRING | 公布日 |
| `amending_law_id` | STRING | 改正法令ID。存在する場合 |
| `legal_topics` | STRING_LIST | 建築、昇降機、消防、石綿等 |
| `provision_type` | STRING | `main`、`supplementary`、`transitional` |
| `status` | STRING | `current`、`future`、`historical` |
| `source_url` | STRING | e-Gov本文URL |
| `retrieved_at` | STRING | 取得日時 |
| `content_sha256` | STRING | 正規化前XMLのハッシュ |

`effective_date`等の日付は、Knowledge Baseのフィルター互換性を優先してSTRINGで保存する。`legal_topics`のみSTRING_LISTとする。

対象事象の初期タグは次とする。

```text
建築
昇降機
消防
バリアフリー
据付
墜落防止
クレーン
石綿
電気工事
廃棄物
騒音
振動
搬入
```

## 7. 版管理

同じ法令IDに複数の施行版が存在する。フォルダ名の形式は次のとおりである。

```text
<元法令ID>_<施行日>_<改正法令ID>
```

`manifest/laws.csv`には少なくとも次を保存する。

- `law_id`
- `law_title`
- `law_type`
- `law_number`
- `effective_date`
- `amending_law_id`
- `status`
- `source_url`
- `retrieved_at`
- `content_sha256`

現行法令検索では、質問の基準日以下の`effective_date`を持つ版から、最も新しい版を選択する。`future`は通常検索から除外し、将来施行情報として別表示する。

## 8. 検索・回答

### 8.1 検索モード

通常RAGと法令RAGは検索入口を分ける。

```text
通常モード
  - 既存のcategory / model_typeフィルターを使用
  - 法令Knowledge Baseは検索しない

法令モード
  - 法令Knowledge Baseだけを検索
  - source_type=lawを確認
  - legal_topics、law_title、effective_dateを利用
```

既存KBへ法令データを追加する場合は、通常検索へ法令が混入しないことをテストで確認する。法令専用KBを採用する場合は、この混入リスクを構造的に排除する。

### 8.2 回答の出典

回答には次を表示する。

- 法令名
- 条文番号
- 施行日
- e-Gov本文URL
- 法令の基準日時点
- 条例・告示・通知を未確認の場合の注記

S3のTXT/Markdownは検索・引用生成の内部資料であり、法令の真正性を示す一次情報URLにはしない。最終確認先としてe-Gov本文URLを案内する。

### 8.3 回答制御

次の場合は断定を避ける。

- 建物用途、規模、自治体、工事内容が不明
- 適用条文を特定できない
- 施行日を確認できない
- 自治体条例、告示、通知の確認が必要
- 検索結果が0件、または根拠条文が不足

回答は「違法」「必須」「不要」と断定する場合に、適用条件と根拠条文を併記する。

### 8.4 API契約案

既存のRAGクエリAPIを拡張し、新しいAPI URLは増やさない。通常RAGとの分離は`mode`によるサーバールーティングと専用Knowledge Baseで保証する。`docs/api/rag.md`はproduction文書のため、この開発設計を実装・承認する段階で別途更新可否を確認する。

#### `POST /rag/query`

既存フィールドを維持し、`mode: "law"`を追加する。

```json
{
  "sessionId": "session_xxxxx",
  "query": "昇降機の据付作業で必要な安全措置は？",
  "mode": "law",
  "filters": {
    "lawId": "347AC0000000057",
    "legalTopics": ["昇降機", "墜落防止"]
  }
}
```

| フィールド | 法令モードでの扱い |
|---|---|
| `sessionId` | 既存会話なら必須。新規会話では既存APIの新規セッション生成規則に従う |
| `query` | 必須。既存APIと同じ入力検証を適用 |
| `mode` | `normal`（既定）または`law`。旧`spec`は従来どおり`normal`へ正規化。その他の値は`400 InvalidMode` |
| `filters.lawId` | 任意。e-Gov法令IDとの完全一致 |
| `filters.legalTopics` | 任意。文字列リストのいずれかに一致（OR）。`lawId`との併用はAND |

- 法令モードでは`category` / `modelType`を使わず、サーバーが`source_type=law`と`status=current`を必須フィルターとして適用する。専用KB IDはサーバー設定から選び、リクエストからKB IDを受け取らない。
- `userId`はリクエスト本文に含めず、Cognito IDトークンの`sub`から決定する。クライアントから送られた値を認可に使わない。
- `asOfDate`は初期API契約に含めない。初期データは2026-10-01時点の現行版スナップショットで、過去時点の法令適用を保証しない。過去時点の法令を問われた場合は、対象版未収録の可能性を明示し、現行版から推測しない。
- レスポンスの共通フィールド（`sessionId`、message ID、`responseType`、`content`、`sourceDocuments`等）は既存形式を維持する。法令出典の追加情報は`sourceDocuments[].lawCitation`に含める。

```json
{
  "mode": "law",
  "responseType": "pages",
  "content": "...",
  "sourceDocuments": [
    {
      "documentName": "労働安全衛生法.txt",
      "sourceUri": "s3://<law-rag-bucket>/kb/egov/...",
      "relevance": 0.91,
      "lawCitation": {
        "lawId": "347AC0000000057",
        "lawTitle": "労働安全衛生法",
        "lawNumber": "昭和四十七年法律第五十七号",
        "effectiveDate": "2026-04-01",
        "promulgationDate": "1972-06-08",
        "provisionType": "main",
        "provisionReference": "第XX条第X項",
        "sourceUrl": "https://laws.e-gov.go.jp/law/347AC0000000057/20260401_507AC0000000033"
      }
    }
  ]
}
```

`lawCitation`の`provisionReference`は検索チャンクから条・項・号を確実に特定できる場合のみ返し、特定できない場合は省略する。推定した条番号を根拠のように表示しない。S3の`sourceUri`は内部識別用で、ユーザー向けの一次情報リンクには`sourceUrl`（e-Gov）だけを使う。

#### チャット履歴

- `eleknowledge-chatlogs`のuser / assistantメッセージに`ragMode: "normal" | "law"`を保存する。既存の`ragMode`なしデータは`normal`として扱う。
- `GET /chat/sessions?mode=normal|law`を追加する。mode省略時は既存互換のため全モードを返す。法令チャットは`mode=law`、通常チャットは`mode=normal`で取得する。
- `POST /rag/query`で既存`sessionId`を再利用するときは、所有者と保存済み`ragMode`を検証する。異なるmodeのセッションを送信に使った場合は`409 SessionModeMismatch`とし、会話履歴を検索コンテキストへ混在させない。
- セッション所有者の判定は既存どおりCognito `sub`で行い、クライアント指定`userId`を信用しない。

### 8.5 UI導線案

- ホーム画面の既存「機能」カードに「法令チャット」を追加し、`/chat?mode=law`へ遷移する。カードは認証済み全利用者に表示し、導入直後はPoC利用可能状態を表示する。
- 既存のチャット画面を再利用し、URLの`mode=law`を画面状態として固定する。ヘッダーに「法令チャット」を表示し、通常チャットへ戻る導線を用意する。modeはリロード・セッション再表示後も維持する。
- 法令モードでは機種・資料カテゴリーフィルターを隠し、初期UIフィルターは「法令ID」「対象分野」のみとする。未指定は法令専用KB内の全対象を検索する。
- 履歴は法令セッションだけを表示する。通常チャット画面も通常セッションだけを表示し、共通APIの`mode`クエリーを使う。
- 出典は法令名、法令番号、特定できた条・項・号、施行日、e-Govリンクを表示する。条文箇所を特定できないときは法令へのリンクまでに留める。S3 URIは表示・リンクしない。
- 入力欄の近くに「収録している現行法令を基に回答。条例・告示・通知等や、過去時点の適用確認は別途必要」と常時表示する。検索0件、日付不一致、根拠条文不明の場合は法的結論を断定しない。
- 検索モードの切替ではなく専用カード・専用URLで入口を分け、リクエストのmodeとセッションのmodeをサーバーで照合する。

## 9. 更新フロー

### 開発時

1. e-Gov XMLを取得
2. XMLスキーマと法令IDを検証
3. XMLのSHA-256を計算
4. rawへ保存
5. TXT/Markdownとmetadata.jsonを生成
6. manifestを更新
7. 法令専用KBをSync
8. 条文番号・施行日・出典URLを検証

### 本番時

定期実行ジョブで取得する。取得失敗時は既存の現行版を削除・置換せず、quarantineへ隔離する。

```text
取得
  -> XML検証
  -> 差分判定
  -> raw保存
  -> 派生データ生成
  -> metadata検証
  -> KB Sync
  -> 検索回帰テスト
  -> manifest確定
```

KB Sync失敗時は、失敗した版を現行版として扱わない。改正内容の反映後は、変更法令、施行日、代表質問の回帰テストを実行する。

## 10. 受け入れ条件

- XML原文と検索用本文を分離して保存できる
- 同一法令の現行版・過去版・未施行版を区別できる
- 条・項・号単位で検索結果を表示できる
- 法令モードで法令専用KBだけを検索できる
- 通常モードの検索結果に法令が混入しない
- 既存の`category`と`model_type`の検索結果が変わらない
- 回答にe-Gov本文URLが表示される
- `mode=law`は法令専用KBだけを検索し、`mode=normal`の検索結果に法令が混入しない
- 法令チャットと通常チャットでセッション一覧・会話履歴が相互に混ざらない
- 法令チャットのカードから法令モードで開き、再読み込み後も法令モードを維持する
- 引用条文を特定できない場合は条番号を捏造せず、e-Gov法令本文へのリンクを表示する
- 取得日時、施行日、改正法令、ハッシュを追跡できる
- XML不正、未施行版、Sync失敗を現行検索へ反映しない

## 11. 未決事項

- 法令専用KBのKnowledge Base ID、埋め込みモデル、ベクトルストア
- 取得ジョブの実行基盤（Lambda、CodeBuild、Step Functions等）
- e-Gov API移行時のレート制限・障害時リトライ
- 国土交通省・消防庁の告示・通知の取得範囲
- 自治体条例を対象にする自治体と取得方法
- JIS・業界標準・メーカー資料の利用許諾
- 条・項・号の参照箇所を検索チャンクから誤りなく抽出する方式（抽出不能時は条文番号を出さない）
- 法令専用S3バケットを保持する失敗CloudFormationスタックの整理・リソース管理方法
- 法務・業務部門による代表質問と回答承認フロー

## 12. 参照

- [対象法令フォルダ一覧](legal-rag-target-laws.md)
- [e-Gov法令検索](https://laws.e-gov.go.jp/)
- [e-Gov法令API Version 2](https://laws.e-gov.go.jp/api/2/swagger-ui#/)
- [e-Gov XML一括ダウンロード](https://laws.e-gov.go.jp/bulkdownload/)
- [公共データ利用規約（第1.0版）](https://www.digital.go.jp/resources/open_data/public_data_license_v1.0)
- [Amazon Bedrock Knowledge Baseデータの前提条件](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-ds.html)
- [Amazon Bedrockメタデータ](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-metadata.html)
- [Amazon BedrockのS3データソース](https://docs.aws.amazon.com/bedrock/latest/userguide/s3-data-source-connector.html)

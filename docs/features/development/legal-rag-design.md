---
status: development
phase: 3
last-verified: 2026-10-01
related-code: infrastructure/sam/phase2-template.yaml, lambda/rag/rag-function/app.py, scripts/legal_rag/upload_egov_laws.py, frontend/src/app/chat/page.tsx
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

### 2.2 推奨する初期Knowledge Base構成

> 最終検証: 2026-10-01 — AWS公式Bedrock/S3/CloudFormation資料およびap-northeast-1のモデル可用性API

| 項目 | 推奨値 | 根拠・注意 |
|---|---|---|
| Knowledge Base | Amazon Bedrock Managed Knowledge Base | 保存・索引・取得ストアをBedrockに任せ、別の常時稼働ベクトルDBを運用しない |
| リージョン | `ap-northeast-1` | 既存の法令S3、RAG APIと同一リージョン |
| Bedrock検索 | Managed KBのHybrid検索 | 管理KBは常にHybrid検索。法令番号・条文番号などの語句一致と意味検索を併用する |
| 埋め込み | カスタム `amazon.titan-embed-text-v2:0`、1024次元、FLOAT | 東京で利用可能。日本語を含む多言語対応だが英語最適化モデルのため、法令の評価質問で品質確認を必須とする |
| ベクトルストア | Bedrock管理ストア | 外部ストアのID、容量、更新、運用をアプリ側で管理しない。別途S3 Vectors/OpenSearchを作らない |
| Knowledge Base名 | `eleknowledge-law-rag-dev` / `eleknowledge-law-rag-prod` | Nameは環境別に固定。Knowledge Base ID自体はAWS生成値を使う |
| データソース名 | `egov-current-laws` | 環境ごとに1データソース。初期は手動/on-demand Sync |
| S3対象 | 既存法令バケットの`kb/egov/`のみ | `raw/`、`manifest/`を検索索引へ混入させない |
| ID連携 | CloudFormation Outputを`LawKnowledgeBaseId` / `LawDataSourceId`として公開 | Phase 2 Lambdaの環境変数へ明示的に渡す。IDをソースコードへ直書きしない |

#### 選定理由と代替案

- `AWS::Bedrock::KnowledgeBase`のCloudFormationリソースは`Type: MANAGED`をサポートし、`Ref`で生成されたKnowledge Base IDを取得できる。`AWS::Bedrock::DataSource`もManaged KB用S3 connectorと`inclusionPrefixes`を設定できるため、リソースの再現性を保ったまま既存バケットを参照できる。
- Managed KBの標準埋め込みはモデルIDを選ばず、管理Rerankerも使えるが、サービス管理モデルの言語仕様をアプリ側で固定できない。法令本文が日本語であるため、初期は日本語を含む多言語対応とIDを明示できるTitan Text Embeddings V2をカスタム埋め込みとして採用する。
- AWS公式仕様では、Managed KBにカスタム埋め込みモデルを使う場合は1024次元のFLOAT埋め込みが必要で、Managed Rerankerは利用できない。一方、Managed KBのHybrid検索は継続して利用できる。初期PoCではRerankerなしで検索品質を測定し、必要なら別途Rerankerを評価する。
- Cohere Embed Multilingual v3は100以上の言語を対象とする候補だが、2026-10-01時点で現在の開発アカウントはモデルAgreementが`NOT_AVAILABLE`。第三者モデルのMarketplace課金もあるため、Agreement承認とTitanとの比較評価が済むまで採用しない。
- S3 Vectorsは従量課金で低頻度検索に向く有力候補だが、今回優先するHybrid検索との組み合わせを避ける。AWS公式資料でHybrid検索が明記される顧客管理ストアはOpenSearch Serverless / RDS / MongoDBであり、OpenSearch ServerlessはPoCに対して運用・固定費が重い。将来、semantic-onlyで十分と実測できた場合はS3 Vectorsを再評価する。

#### Knowledge Base IDとIaC

> 最終検証: 2026-10-02 — 昨日の会話、AWS CLI read-only（ROLLBACK_COMPLETE / DELETE_SKIPPED bucket / HTTPS拒否policy / tags）、CloudFormation import公式資料を照合。旧stack削除/bucket importは未実施。KB作成とdev反映の結果は後段に記録。

- 法令S3バケットの旧CloudFormationスタック`eleknowledge-legal-rag-dev`は、2026-10-02のread-only確認で`ROLLBACK_COMPLETE`、唯一のstack resource `LawDataBucket`は`DELETE_SKIPPED`だった。既存bucketのownerはprofileのcaller accountと一致し、TLS必須のDeny policyが存在するが、stack resourcesには含まれていない。昨日の会話ではraw XML 53件、旧形式の派生本文106件とsidecar 106件、manifest 1件の保存が確認されている。既存データを維持し、同名bucketを新規作成しない。
- 推奨は保持bucketをCloudFormation管理へimportすること。失敗stackは削除しかできないため、削除前に全resourceと`DeletionPolicy: Retain`を確認し、削除の明示承認後にのみstackを削除する。このstack削除・importはAWS上の変更であり、このPRでは実行しない。
- 旧stackの削除後、既存bucketと現存するTLS policyを別名の新しい管理stack `eleknowledge-legal-data-dev-managed`へimportする。`AWS::S3::Bucket` / `AWS::S3::BucketPolicy`はimport対象としてサポートされる。import change setではresourceの作成・削除・property変更はできないため、resource import完了後にdrift detectionを行い、次のstack updateでタグを`Project=EleKnowledge`・`Env=dev`・`ManagedBy=SAM`へ揃える。bucket policyはimport前に実物とtemplateを照合する。
- Knowledge Base用スタック`eleknowledge-law-kb-dev`はデータバケット管理スタックと分ける。KB用S3データソースは保持bucketの`kb/egov/`のみを参照する。import/change setは実bucket名と現在のpolicyをread-backしてから行い、AWS変更の前に共同レビューを得る。
- 新設テンプレート`infrastructure/sam/legal-rag-kb-template.yaml`にKnowledge Base、S3データソース、Bedrockサービスロールを定義する。BedrockロールのS3読み取り権限は`kb/egov/*`に限定し、KMS復号もソースバケットのキーに限定する。RAG Lambdaには`bedrock:Retrieve`の対象Knowledge Base IDだけを付与する。
- `Ref`で得たIDをテンプレートOutputへ出し、RAG実行環境の`LAW_KNOWLEDGE_BASE_ID`へ接続する。開発と本番でID・役割・データソースを混ぜない。

#### 取込本文の粒度

> 最終検証: 2026-10-02 — 開発S3の本文・sidecar件数とmetadataを確認し、RAGのManaged KB filter/post-filterをコード照合

初回Sync前に、検索用本文を法律全体の大きなファイルではなく、条・項・号を維持した条文単位のTXTへ分割する。各ファイルにBedrock sidecarを付け、`provision_reference`（例:`第129条の3第1項`）と`provision_type`を設定する。長い条文は固定サイズ300 tokens / 20% overlapで追加分割し、全チャンクに同じ条文メタデータを引き継ぐ。条番号を特定できない附則は`provision_reference`を省略し、番号を推測しない。

取込開始前の記録: 2026-10-01時点のS3には旧形式の検索本文106件とsidecar 106件が保存されていた。2026-10-02のPR #156 dry-runでは、53 XMLから検索本文10,321件（15,374,504 bytes）と同数のsidecarを生成し、AWS/S3への追加書込み前に確認した。初期計画は既知の旧派生本文を明示フラグで整理し、費用上限/終了条件の合意までKB作成・初回Syncを待つものだった。以降のdev実施結果は下記に分けて記録し、業務対象範囲やmonaとの共同合意を実施済みと読み替えない。

#### 現在のdev実験・決定記録・利用ゲート

> 最終検証: 2026-10-06 — itai提示の決定事項とPR #155の履歴を照合。AWS上のfeature gate状態、認証利用者数、請求額はread-back未実施。

- 決定・確認者はitai（実施担当）、記録日は当初記録をpushした2026-10-02。itaiの申告では、dev作業に進む前にmonaから口頭同意を得ていた。口頭同意を正式な対象部門承認や今回の条件への書面同意とは扱わず、今回の更新記録をmonaへ提示してYes/Noを再確認する。
- 対象範囲はdev環境の認証済み利用者全員、最大約300人（概数）。記録済みの5送信は認証済みitaiによる。実際の利用者数は未read-back。dev限定・本番OFFを方針とするが、実AWSのgateが現在ONかOFFかは未確認。
- 初期計画には費用条件の合意までKB作成・初回Sync・実利用を待つと記載されていた。実際には、itai申告のmona口頭同意後にdev同期・案Bのdev実験・5送信を実施した。実施済みの事実と当時の承認状態を分けて記録し、後から書面承認済みとみなさない。
- 案Bは標準採用ではなくdev実験として扱う。入力token数と費用見積もりは別途測定する。対象外の法令・資料を尋ねられたときは、収録範囲外と明示し、モデルの一般則は補助情報としてのみ扱う。該当するe-Gov法令ページ、特定できない場合はe-Gov法令検索を案内して一次情報の確認を促す。
- 仮上限は月額100 USD、見直し責任者はitai、評価期限は2026-12-31。12月に費用対効果で継続／拡大／停止を判断する。個別の判断条件は事前設定しない。100 USDを超える支出はこの仮設定に含まれない。
- 業務スコープに関する最新の書面確認が揃うまでは、本番有効化、法令対象・利用者の拡大、追加同期、データ削除を行わない。現行gate状態、利用者実数、実請求額のread-backも別途必要。

#### 条文直接リンクと正式見出し

> 最終検証: 2026-10-02 — 53法令の本則7,229条と8階層を照合し、S3更新・KB再同期完了・認証済みitaiでの正式見出し/直接リンクとe-Gov対象条文への移動を確認

- 本則の`Article`は、元の版指定URLにXML階層から生成したfragmentを付け、検索本文の出典とsidecarの`source_url`へ保存する。回答時の追加API呼出しは行わない。
- アンカーは`MainProvision=Mp`、`Part=Pa`、`Chapter=Ch`、`Section=Se`、`Subsection=Ss`、`Division=Di`、`Article=At`とし、各`Num`の枝番号（`129_13_3`など）は変更しない。
- 対応階層は、本則直下の条、章/条、章/節/条、章/節/款/条、章/節/款/目/条、編/章/条、編/章/節/条、編/章/節/款/条の8種類に限定する。未知の階層・番号欠損・不正な番号はアンカーを推測せず、元の法令全体URLを使用する。附則・経過措置・別表も法令全体URLを使用する。
- `Num="29:31"`などの範囲指定は単一条のアンカーとして扱わず、全体URLへ戻す。対象本則7,229文書のうち24文書がこの形式であり、直接リンクは残る7,205文書が対象となる。範囲指定も正式な`ArticleTitle`を保持する。
- 本則の`provision_reference`はXMLの`ArticleTitle`（例:`第百二十九条の十三の三`）を使用し、`Num`から表示文字列を組み立てない。見出し欠損時は同属性を省略する。
- 既存のAPI/画面は`source_url`と`provision_reference`を引き継ぐ。新しいリンクの反映には派生本文・sidecarの再生成とS3更新、KB再同期が必要。原文XML・旧aggregate・保存済みの過去回答を削除または書き換えない。
- e-Govアンカーは実ページで確認した形式であり、APIの永続的なURL契約とは扱わない。更新時は代表リンクを再検証する。ローカル実装完了とS3/KBへの反映完了を分けて記録する。

2026-10-02にdev S3の10,321本文/sidecarを更新し、KB再同期 `DGXCWFHOWN`は`COMPLETE`。本文・metadata各10,427件scan、変更本文/metadata各10,321件、失敗・削除・skipは0件。認証済みitaiの新規回答で正式見出しと条文リンクを確認し、e-Govの対象条文へ移動できた。今回の反映はデータ更新であり、API/画面のコード再デプロイと本番変更、過去回答の書換えは行っていない。

#### 既知の不具合: 収録済み条文の参照不足

> 最終検証: 2026-10-02 — 同期統計・S3/XML・実KB検索・モデル参照生成を照合。案Bを採用し、実装後のdev動作確認を完了条件とする。

収録済みの条文について「本参照資料に含まれていない」と回答する事象を確認した。最新同期は本文/metadata各10,321件更新、失敗・削除・skipは0件。建築基準法34条、施行令129条の13の2/13の3、労働基準法36条、消防法17条、労働安全衛生規則519条の6条文は、複数の条文指定検索結果を合わせるとS3全文を100%覆う（空白・表記幅を正規化）。この範囲で索引欠落はない。

原因は、関連チャンク検索が全文読出しではないことと、法令モードにも適用された全体10チャンク・同一本文2チャンクの選別制限。施行令129条の13の3はKBで13チャンクを確認できるが、通常検索4・モデル参照2になった。他の3法令でも再現。1,200文字/チャンクの切詰めは今回の6サンプルでは発生していない。53法令の本則7,229文書中、3項以上は1,751文書/50法令であり、これは潜在リスクの指標で、実際の失敗件数ではない。2項でも複数チャンクに分かれるため短い条文も影響する。

CloudWatchの当時のログはHTTP 200と出典件数を残すが、モデルへ渡した本文は保存していない。過去の入力は完全復元できず、以下は現KB・現コードの再取得とメモリ内試作による比較である。生成回答の正確性・Lambda遅延の評価は別に必要。

| 案 | 比較結果 | 判断 |
|---|---|---|
| A: 取得100件、全体30/本文8チャンクへ拡大 | 6条文中5条文で参照が全文に届かない。例:施行令129条の13の2は38.48%、13の3は41.08%、労働基準法36条は55.74% | 単独採用しない |
| B: 検索で採用した条文のS3全文を補完 | 対象6条文の全文を参照へ渡せる。上限付き試作で今回の関連3条文を補完 | 今回採用 |
| C: 名指し条文・関連条文を追加取得 | 検索に当たらない条文も救えるが、番号解決・誤接続・取得範囲の制御が必要 | 別の次段階 |

案Bの仕様:

- devの法令モードだけで、採用済み結果をS3 URI単位で集約して全文補完する。通常RAGの検索・選別・権限は変更しない。生成と引用は同じ補完済み参照集合を使う。
- 初期上限は全文6本文、単体8,000文字/32KB、参照本文合計20,000文字。巨大な本文は全文と称して切らず、既存検索断片を部分参照として渡す。合計枠がなくなった参照は生成・引用の両方から除外する。
- 元の版・正式見出し・e-Gov出典を保持する。モデルへ全文/部分参照と部分化の理由を明示し、部分参照を「未収録」と断定させない。
- S3読取りは構成済み法令bucket、同一account、`kb/egov/<law-id>/<version>/<provision_type>/<5桁>.txt`のみ。外部bucket・不正URIへのアクセスは禁止。dev有効時だけGetObject/KMS復号を追加し、書込み・ListBucket・raw XML読取りは追加しない。
- 短い接続/読取りtimeout、retryなし、補完時間枠と生成に残す時間の確認を行う。権限不足・欠損・timeout時は部分参照へ戻し、質問本文・引用全文・個人情報をログへ出さない。ログは補完件数/状態/理由とrequest IDのみとする。
- KBの再同期・チャンク設定変更・S3再uploadは不要。実装後は6条文の後半の項・要件、巨大本文・不正URI・読取り失敗/timeout、引用一致、通常RAG回帰、実Lambdaの遅延と生成量を確認する。費用の確定は実運用計測とし、試作のローカル読取り時間を本番p95と扱わない。

2026-10-02の案B実装・dev確認結果:

- 全unit tests 481件成功（既存deprecation warnings 6件）、cfn-lint成功。全文の末尾保持、引用集合一致、重複読取り抑止、単体/合計/件数上限、不正URI、権限不足・欠損・timeout・不正UTF8、時間不足、dev以外の拒否、本文を出さないログを確認。
- 実KB/S3の6条文で最終項がモデル参照に残ることを確認。ローカル補完処理は約0.33〜1.19秒だが、実Lambdaのp95ではない。
- `law-full-text-20261002` change setは`UPDATE_COMPLETE`。詳細評価の変更はRagFunctionのCode/EnvironmentとRagLambdaRoleのPoliciesのみ、置換なし。Sonnet5・KB ID・dev gate・既存パラメータを保持。法令派生本文GetObjectは許可、raw XML読取りと法令S3書込みは拒否。本番は変更していない。
- 認証済みitaiの5送信で6条文を確認し、HTTP 200・対象本文`referenceCoverage=full`。施行令の除外条件/乗降ロビー/予備電源/第13項、労基法36条の後半、消防法17条の第2/3項、安衛則519条の第2項、建築基準法34条第2項が回答され、e-Gov出典を保持した。これは運用の参照不足修正の確認であり、法的判断・回答の完全性を認定するものではない。
- 5送信のサーバー処理は9.57〜25.95秒、参照本文は3,455〜10,495文字、全文6本文/送信。速度目標p95 < 3秒は達成と扱わない。費用はS3/KMS読取りとモデル入力が増えるため実運用の利用量/請求で確認し、文字数から確定料金を推定しない。
- 複合質問では検索から外れた34条が未提示になる例もあった。単独質問で全文を確認できたが、未取得の名指し条文/関連条文を救う案Cは未実装。過去回答は書き換えず、S3再upload・KB再同期は行っていない。ソース修正と共同確認用の本記録は別PRでレビューする。

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
├── kb/egov/<law-id>/<version-folder>/main/<provision-key>.txt
├── kb/egov/<law-id>/<version-folder>/main/<provision-key>.txt.metadata.json
├── kb/egov/<law-id>/<version-folder>/supplementary/<provision-key>.txt
├── kb/egov/<law-id>/<version-folder>/supplementary/<provision-key>.txt.metadata.json
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
| `provision_reference` | STRING | 条・項・号の表示用参照。例:`第129条の3第1項` |
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

> 最終検証: 2026-10-06 — デジタル庁「公共データ利用規約（第1.0版）」§1.1(1)(2)を確認し、出典・加工表示を反映

回答には次を表示する。

- 法令名
- 条文番号
- 施行日
- e-Gov本文URL
- 法令の基準日時点
- 条例・告示・通知を未確認の場合の注記

S3のTXT/Markdownは検索・引用生成の内部資料であり、法令の真正性を示す一次情報URLにはしない。最終確認先としてe-Gov本文URLを案内する。

e-Gov公共データ利用規約（PDL1.0）に沿い、回答/出典UIでは出典名とe-Govの原文URLを示し、原文を一次情報とする。S3検索本文などの加工物を表示・利用する箇所には、出典とは別に、加工した事実と主体を表示する。表示例は「e-Gov XMLをもとにEle-Knowledgeが検索用に加工して作成」です。加工物をe-Govまたは国が作成した未加工の原文と誤認させない。データ利用条件は[公共データ利用規約（第1.0版）](https://www.digital.go.jp/resources/open_data/public_data_license_v1.0)を参照する。

### 8.3 回答制御

次の場合は断定を避ける。

- 対象法令・資料が収録範囲外の場合はその旨を明示する。モデルが一般則を補助情報として示す場合も、法的根拠・適用判断とは区別し、特定できる場合はe-Govの該当法令ページ、特定できない場合はe-Gov法令検索を案内して一次情報の確認を促す。
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
- 法令モードの`Retrieve`は`managedSearchConfiguration`を指定し、既存KB向け`vectorSearchConfiguration`や`overrideSearchType`は渡さない。通常モードの既存検索設定には変更を加えない。
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

> 最終検証: 2026-10-06 — dev認証済み全利用者（最大約300人の概数）を対象範囲として記録。実人数・AWS gate状態は未確認。

- ホーム画面の既存「機能」カードに「法令チャット」を追加し、`/chat?mode=law`へ遷移する。開発環境では現在の認証済み利用者全員がテスト対象であり、dev gateがONならカードを全員に表示する。カードには「プレリリース」を表示する。PoCのgateは既定OFFとし、本番では常にOFFにする。
- `/chat?mode=law`のヘッダーにも「プレリリース」を表示する。ゲートOFF、本番環境、未認証の場合はAPI側でも拒否し、UIの非表示だけを認可として扱わない。現時点では個別Cognito group/allowlistを設けない。テスト対象の変更やdev利用者以外への展開は別途mona / itaiで共同確認する。
- 既存のチャット画面を再利用し、URLの`mode=law`を画面状態として固定する。ヘッダーに「法令チャット」を表示し、通常チャットへ戻る導線を用意する。modeはリロード・セッション再表示後も維持する。
- 法令モードでは機種・資料カテゴリーフィルターを隠し、初期UIフィルターは「法令ID」「対象分野」のみとする。未指定は法令専用KB内の全対象を検索する。
- 履歴は法令セッションだけを表示する。通常チャット画面も通常セッションだけを表示し、共通APIの`mode`クエリーを使う。
- 出典は法令名、法令番号、特定できた条・項・号、施行日、e-Govリンクを表示する。条文箇所を特定できないときは法令へのリンクまでに留める。S3 URIは表示・リンクしない。
- 法令モードの出典表示に「e-Gov XMLをもとにEle-Knowledgeが検索・回答用に加工して作成」と表示し、e-Gov原文へのリンクを併記する。加工した検索本文を画面に直接表示するときは、その本文にも同じ加工表示を隣接させる。
- 入力欄の近くに「収録している現行法令を基に回答。条例・告示・通知等や、過去時点の適用確認は別途必要」と常時表示する。検索0件、日付不一致、根拠条文不明の場合は法的結論を断定しない。
- 検索モードの切替ではなく専用カード・専用URLで入口を分け、リクエストのmodeとセッションのmodeをサーバーで照合する。

### 8.6 PoC E2Eシナリオ

> 最終検証: 2026-10-06 — dev認証済み全利用者（最大約300人）と記録済み5送信（認証済みitai）を照合。実人数・AWS gate状態は未確認。

**実施範囲:** 開発環境`ap-northeast-1`のみ。dev環境の認証済み利用者全員（最大約300人の概数）を対象とし、本番KB・本番利用者は対象外。記録済みの5送信は認証済みitaiによる。実際の利用者数とAWS上のgate状態はread-back未確認。

**前提条件:**

- 53法令の条文単位TXTと各`.metadata.json`を`kb/egov/`へ登録し、原文XMLは`raw/egov/`だけにある。
- Bedrock Managed KBのManaged S3データソースが`kb/egov/`のみを対象とし、初回Ingestion jobの状態が`COMPLETE`。
- CloudFormation出力のKB IDがRAG Lambdaの`LAW_KNOWLEDGE_BASE_ID`に設定済み。
- dev gateをONにし、Cognito認証済みの現行dev利用者全員を対象とする。カードと法令チャット画面の両方に「プレリリース」を表示し、本番ではgateをOFFにする。
- ユーザー入力・ID token・法令引用全文をCloudWatch Logsに残さない。

| ID | 操作 | 合格条件 |
|---|---|---|
| LAW-E2E-01 | 認証済みdev利用者でログイン後、ホームの「法令チャット」カードを開く | 現行dev利用者全員にカードを表示し、「プレリリース」表示を付ける。dev gate ONなら`/chat?mode=law`となり、法令モード表示と収録範囲の注意書きが出る。ゲートOFFまたは本番ではカードを表示しない |
| LAW-E2E-02 | 収録済み法令について質問する | `POST /rag/query`の`mode=law`からManaged KBだけを取得し、`source_type=law` / `status=current`で絞る。通常KB IDへのフォールバックはしない |
| LAW-E2E-03 | 条・項・号を含む代表質問を行い出典を開く | `provision_reference`、法令ID、施行日が同じTXTのsidecar/e-Gov本文と一致し、リンクはe-Govを開く。S3 URIを利用者にリンクしない |
| LAW-E2E-04 | 同じテーマを通常チャットと法令チャットの両方で質問する | 通常結果に法令文書が混入せず、法令結果に社内KB文書が混入しない |
| LAW-E2E-05 | lawセッションを作成し、一覧から再表示して追質問する | `GET /chat/sessions?mode=law`に表示され、law履歴だけが検索コンテキストになる。normalセッションIDの再利用は`409 SessionModeMismatch` |
| LAW-E2E-06 | 未ログイン、dev gate OFF、本番環境、別ユーザーsessionId、改ざんしたmodeでAPIを呼ぶ | 未ログイン401、gate OFF/本番のlaw modeは拒否、他ユーザーの履歴は既存の所有権ルールどおり拒否、未知modeは400。利用者間データが混ざらない |
| LAW-E2E-07 | 工事条件が不足した質問を送る | `clarify`となり、必要情報を聞き返す。検索・回答で適用法令を決め打ちしない |
| LAW-E2E-08 | 法令一覧外、条例・告示、2026-10-01より過去時点の法令を質問する | 収録範囲外/版であることを明示し、モデルの一般則は補助情報に限る。該当法令ページまたはe-Gov法令検索を案内し、現行版から過去の法的判断を推測しない |
| LAW-E2E-09 | KBが未Sync、取得障害、0件の条件で質問する | 共通エラー形式または`not_found`を表示し、法令モードから通常KBへ暗黙fallbackしない |
| LAW-E2E-10 | 法令モードで回答と加工済み検索本文を表示する | e-Govの出典URLに加えて「e-Gov XMLをもとにEle-Knowledgeが検索・回答用に加工して作成」を表示し、加工済み本文をe-Govが作成したと誤認させない |

各ケースは実行者、日時、API request ID、結果、実際に参照した法令ID/条文/e-Gov URLを記録する。失敗時はrequest IDでCloudWatchを調べ、token・個人情報・引用全文は記録しない。

### 8.7 検索品質評価と合格基準

> 最終検証: 2026-10-06 — 24問構成と月額100 USDの仮上限、itai責任、2026-12-31評価期限を反映。token数・実費は未計測。

既存の[`docs/eval-2026-07-29-retrieve-golden-set.md`](../../eval-2026-07-29-retrieve-golden-set.md)の第1層機械評価を踏襲するが、通常RAGの正本`tests/eval/golden_set.jsonl`は変更しない。法令専用候補を`tests/eval/legal_golden_set_candidates.jsonl`に作り、既存ランナーをManaged KB / `mode=law` / 法令メタデータ用に拡張する。

**24問の候補構成:**

- 法令番号・条番号の完全一致質問: 8問
- 建築/昇降機/消防/労働安全/電気/環境の単一分野質問: 8問
- 複数法令の突合質問: 4問
- 条件不足・一覧外・条例/告示・過去時点など断定回避質問: 4問

各JSONL行に`id`、一般化済み`query`、`filters`、`expected_law_ids`、`expected_provisions`、`expected_gate`、`tags`、`skip`を持たせる。`expected_law_ids`と条・項・号はe-Gov原文を参照し、mona / itaiが共同確認した行だけ`skip: false`にする。既存評価方針どおり、ラベル済みN<10では率を意思決定に使わない。

**PoCの初期合格基準案（Draft。実施前にmona / itaiがYes/Noで確定）:**

- 全9 E2Eケースが合格し、normal/law間の検索混入と履歴混在が0件。
- ラベル済み質問の`law_hit@5`が全体90%以上、`hard`タグ群80%以上。
- 表示した法令ID・版・施行日・e-Gov URLが相互に一致する割合100%。条文番号の誤表示0件。
- `clarify` / `not_found` / 対象外質問で根拠のない法的断定0件。
- 既存プロジェクトSLOに合わせ、法令回答のp95を3秒未満とする。超過時は検索と生成を分けて計測する。

2026-10-02にitaiは、開発PoCの初期費用は小さく、開始に追加の費用承認は不要との認識を記録した。2026-10-06時点の仮上限は月額100 USD、見直し責任者はitai、評価期限は2026-12-31とする。実費、入力token数、更新/監視/問い合わせ対応などの運用工数は別途計測・確認する。

**12月の評価:** 2026年12月に費用対効果を評価してPoCの継続・拡大・停止を判断し、結果と判断者を記録する。個別の継続／拡大／停止条件は事前に設定しない。月額100 USDは仮上限であり、上限を超える支出の承認を意味しない。

機械指標は取得到達・ゲートの評価であり、回答の法的妥当性を自動認定しない。代表質問の期待条文は業務確認し、回答文の正確性・断定回避は引用元本文に照らして人が承認する。

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
9. LAW-E2E-01〜10を開発環境で実施し、実行結果とrequest IDを記録
10. 法令golden setの共同ラベルを確定してretrieve評価を実行。合格基準案は§8.7を参照

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
- 条文単位ファイルのメタデータから条・項・号を出典表示でき、特定不能箇所は番号を捏造しない
- LAW-E2E-01〜09を開発環境で全件通過し、normal/law検索混入とユーザー間セッション漏えいが0件
- 共同ラベル済みの法令質問セットで、§8.7の`law_hit@5`・引用整合性・断定防止基準を確認する
- 取得日時、施行日、改正法令、ハッシュを追跡できる
- XML不正、未施行版、Sync失敗を現行検索へ反映しない

## 11. 未決事項

> 最終検証: 2026-10-06 — 提示された利用者範囲、費用仮上限、評価期限を反映。実gate・利用者実数・実費は未確認。

- 取得ジョブの実行基盤（Lambda、CodeBuild、Step Functions等）
- e-Gov API移行時のレート制限・障害時リトライ
- 国土交通省・消防庁の告示・通知の取得範囲
- 自治体条例を対象にする自治体と取得方法
- JIS・業界標準・メーカー資料の利用許諾
- 法令専用S3バケットを保持する失敗CloudFormationスタックの整理・リソース管理方法
- 53法令の分野別選定理由が十分か、monaのYes/Noと正式な対象部門の確認
- dev認証済み全利用者（最大約300人）・対象外質問時の案内・本番OFFについて、今回更新した記録に対するmonaの書面Yes/No
- AWS上の現在のdev feature gate状態と実際の認証利用者数のread-back
- 月額100 USD仮上限内の実費、入力token数とモデル費用の確認（別途測定）
- 2026年12月の費用対効果評価と継続／拡大／停止判断の記録
- 正式な業務対象部門・確認者の特定
- Titan V2の日本語法令検索品質（代表質問の評価結果が不十分な場合は、Cohere Embed Multilingual v3のAgreement取得後に比較）
- 現行`run_retrieve_eval.py`の法令Managed KB / `mode=law`対応、法令候補JSONL、API/UI E2Eハーネスの実装と実行結果
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
- [Amazon Bedrock Managed Knowledge Base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-build-managed.html)
- [Managed Knowledge Baseのリージョン](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-regions.html)
- [Managed Knowledge BaseのS3コネクター](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-ds-s3.html)
- [Managed Knowledge Baseの検索](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve.html)
- [Titan Text Embeddings V2](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-titan-text-embeddings-v2.html)
- [Cohere Embed Multilingual](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-cohere-embed-multilingual.html)
- [Amazon S3 Vectors](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html)
- [CloudFormation: AWS::Bedrock::KnowledgeBase](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-bedrock-knowledgebase.html)
- [CloudFormation: AWS::Bedrock::DataSource](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-bedrock-datasource.html)

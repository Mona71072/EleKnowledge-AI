---
schema_version: 1
record_id: "catalog-elv-touchless-reference"
record_version: 4
title: "タッチレスボタン資料の参照記録"
category: "技術メモ【ELV】２"
record_type: "catalog"
product: "エレベーター"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["タッチレス", "乗場ボタン", "不具合", "最下階", "意図しない登録"]
source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/タッチレス.md"
source_filename: "タッチレス.md"
onenote_id: "883faf8b-0724-4840-beff-cfb701e7d784:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-touchless-001"
    source_type: "vault_original"
    title: "タッチレス"
    source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/タッチレス.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["初期設定/操作不具合の情報共有リンクがあること"]
  - source_id: "evidence-list-elv-touchless-nshr-329"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: NSHR時にタッチレス機能で解除できない件（ID329）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "特殊なセキュリティ仕様と他社製認証器を併用した際のタッチレス動作差に関する報告"
  - source_id: "evidence-list-elv-touchless-operation-fault-321"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: タッチレス動作不良（ID321）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "タッチレス全体または戸閉ボタンのみの不作動、設定/部品関連の原因説明、対応後の改善報告"
  - source_id: "evidence-list-elv-touchless-unintended-registration-110"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: 最下階乗場ボタン（タッチレス仕様）が意図せずに登録される件（ID110）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "対象機種VFGLBとして記録された、最下階のタッチレス仕様乗場ボタンが意図せず登録される報告"
      - "一次リスト上の対応状況表示が対応済みであること。復旧・再発有無の独立確認ではない"
structured_data:
  source_notes:
    - "リンク先未閲覧。設定・解除条件・不具合処置を転載していない。"
    - "協力会社展開用Excel ID329は、特殊なセキュリティ仕様と他社製認証器の併用時にタッチレス登録/解除動作が一貫しない事例を報告する。原リストは仕様回答としているが、対象条件・仕様書・現行性は未確認。時間値・操作順序・解除方法は転載しない。"
    - "協力会社展開用Excel ID321は、タッチレス全体が不作動の事例と戸閉ボタンのみ不作動の事例を分けて報告し、それぞれ設定関連/部品関連の原因説明と対応後の改善を記録する。原因・結果は独立確認していない。電圧/診断値、基板・コネクタ識別、初期化/再設定・差替え手順は転載しない。"
    - "首都工・不具合情報共有リストID110は、VFGLBの最下階乗場ボタン（タッチレス仕様）が意図せず登録される件として記録され、対応状況は対応済み。詳細な原因・処置内容、復旧確認、再発有無、外部リンク先は未確認。ID329/321/365とは別事例として扱い、操作・設定手順を推定しない。"
---

# タッチレスボタン資料の参照記録

原資料はタッチレスボタンの初期設定や動作不具合に関する情報共有リンクを含む。具体的な設定、解除条件、復旧方法は記録していない。

協力会社展開用Excel ID329は、特殊なセキュリティ仕様と他社製認証器の併用時にタッチレス登録/解除動作が一貫しない事例を報告し、仕様上の動作との回答があったとしている。対象条件、参照仕様書、現行性は未確認であり、他の機種・認証器に一般化しない。時間値・操作順序・解除方法は記録しない。

協力会社展開用Excel ID321は、(1)複数のタッチレス操作が不作動となり、設定関連の原因説明と対応後の改善があった事例、(2)戸閉ボタンのタッチレスのみ不作動となり、ボタン/信号経路関連の原因説明と対応後の改善があった事例を別々に報告する。原因・結果・適用範囲は独立確認していない。電圧/診断値、基板・コネクタ識別、初期化/再設定・差替え手順は記録しない。ID329とは別事例である。

首都工・不具合情報共有リストID110は、VFGLBの最下階乗場ボタン（タッチレス仕様）が意図せず登録される件として記録され、対応状況は対応済み。詳細な原因・処置内容、復旧確認、再発有無、外部リンク先は未確認のため記載しない。ID329/321/365とは別事例であり、操作・設定手順を推定しない。

リンク先と対象機種の現行資料を確認するまで、設定・運転・不具合対応に使用しない。

出典: `技術メモ【ELV】２/ELV-付加仕様（その他）/タッチレス.md`（OneNote ID `883faf8b-0724-4840-beff-cfb701e7d784:1`）。確認日: 2026-10-08。

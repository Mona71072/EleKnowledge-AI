---
schema_version: 1
record_id: "elv-customer-breaker-capacity-relationship-id214"
record_version: 1
title: "エレベーターと客先ブレーカー容量の関係（ID214）"
category: "技術メモ【ELV】２"
record_type: "technical_reference"
product: "エレベーター"
model_type:
  - "全エレ機種（原リスト記載。適用範囲未確認）"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "客先ブレーカー"
  - "エレベーターブレーカー"
  - "容量関係"
  - "保護協調"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "elv-breaker-grounding-safety-review-hold"
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "品目表（ID214が参照。対象品目・版未特定）"
    locator: "NV 20A、BL-2C 30Aの例を記載"
    source_path: ""
  - document_number: ""
    title: "据付図 工事区分表（ID214が参照。版未特定）"
    locator: ""
    source_path: ""
  - document_number: ""
    title: "内線規程（ID214が参照。版・条項未特定）"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-customer-elevator-breaker-capacity-214"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト.xlsx: エレベーターと客先のブレーカー容量（ID214）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "1台1回線の回路構成と客先側容量をエレベーター側より大きくするとの原リスト記載"
      - "他設備への給電停止と上位側遮断器の先行トリップによる復旧・救出遅延リスクの説明"
      - "NV 20AおよびBL-2C 30Aの品目表例"
structured_data:
  specifications:
    - name: "回路構成"
      value: "1台1回線"
      unit: ""
      condition: "エレベーターと客先側のブレーカーを個別回線とするとの原リスト記載。"
    - name: "客先側とエレベーター側の容量関係"
      value: "客先側 > エレベーター側"
      unit: ""
      condition: "原リストが客先側ブレーカー選定について示す関係。現行設計基準として独立確認していない。"
    - name: "動力電源エレベーター側ブレーカーの品目表例"
      value: "20"
      unit: "A"
      condition: "NV 20Aとの原リスト記載例。対象機種・現行品目表との対応未確認。"
    - name: "照明電源エレベーター側ブレーカーの品目表例"
      value: "30"
      unit: "A"
      condition: "BL-2C 30Aとの原リスト記載例。対象機種・現行品目表との対応未確認。"
  safety_warnings:
    - "容量関係・回線構成・品目表例は一次リストの記載であり、現行の設計基準、機器選定値、保護協調または現場への適用として承認・検証されたものではない。"
    - "電源設備・遮断器の選定、施工、保護協調、停電・救出判断には使用しない。"
  source_notes:
    - "リストは、他設備への給電停止回避と、メーカー間の動作特性差により客先側遮断器が先に動作して復旧・救出が遅れる可能性を理由として挙げる。因果・リスク評価は独立確認していない。"
    - "同容量で引き渡す例外について、リストは客先了承とブレーカー位置の事前確認に言及する。これは原リスト上の調整事項であり、承認済みの設計手順とは確認できていない。"
    - "品目表、据付図工事区分表、内線規程は参照先として列挙されるが、資料番号・版・本文は確認できていない。内線規程1350-13を挙げる別資料とは出典を混同しない。"
---

# エレベーターと客先ブレーカー容量の関係（ID214）

首都工・不具合情報共有リストID214は、エレベーター側と客先側のブレーカーを1台1回線とすること、客先側ブレーカー容量をエレベーター側より大きくすることを周知事項として記載する。

リストは理由として、エレベーター側ブレーカー交換時に客先側を遮断すると他設備への給電まで止まり得ること、容量を同格とした場合はメーカー間の動作特性差により客先側が先にトリップし、復旧・救出が遅れる可能性を挙げる。これは原リストの設計上の説明であり、現行の保護協調資料で独立確認していない。

品目表の例として、動力電源エレベーター側にNV 20A、照明電源エレベーター側にBL-2C 30Aを挙げる。対象機種・回路・現行品目表との適合は未確認であり、選定値として一般化しない。同容量での引渡し例外についても客先了承等への言及があるが、承認済み手順とは確認できていない。

参照先として品目表、据付図工事区分表、内線規程を挙げるが、資料番号・版・本文は未確認。関連するブレーカー種別・接地記述は[[ELV_ブレーカー・接地_安全レビュー保留]]を参照する。本記録を遮断器選定・施工・保護協調・停電/救出判断に使用しない。
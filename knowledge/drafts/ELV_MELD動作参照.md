---
schema_version: 1
record_id: "elv-meld-operation-reference"
record_version: 5
title: "MELD動作に関する不具合共有参照"
category: "不具合対応(ELV)"
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
keywords:
  - "MELD"
  - "M14コネクタ"
  - "コネクタ差し忘れ"
source_path: "不具合対応【ELV】/現象（不具合対応）/バッテリー（不具合対応）/MELD動作（不具合）.md"
source_filename: "MELD動作（不具合）.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:149"
related_ids:
  - "case-elv-vfglf-meld-connector-omission-id132"
  - "case-vfglf-m14-meld-pin-assignment-id429"
  - "case-elv-meld-contactor-damage-id167"
  - "case-elv-vfglb-low-battery-meld-failure-entrapment-id174"
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "M14コネクタ ピンアサイン間違い"
    locator: "不具合共有リスト ID 429"
    source_path: ""
  - document_number: ""
    title: "コネクタ差し忘れにて、客先ブレーカー遮断時にMELDが実動作しない件"
    locator: "不具合共有リスト ID 132"
    source_path: ""
  - document_number: ""
    title: "MELD接続時のコンタクタ焼損報告"
    locator: "不具合共有リスト ID167"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-meld-reference-original"
    source_type: "vault_original"
    title: "MELD動作（不具合）（原文）"
    source_path: "不具合対応【ELV】/現象（不具合対応）/バッテリー（不具合対応）/MELD動作（不具合）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "MELD関連不具合共有の題名と添付画像の参照"
  - source_id: "evidence-elv-meld-contactor-damage-167"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: MELD接続時のコンタクタ焼損（ID167）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "ID167の個別ケース記録への導線と、対応欄間の復旧状態の不一致"
  - source_id: "evidence-list-elv-vfglb-low-battery-meld-entrapment-id174"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: バッテリー電圧低下によりMELDへ移行せず閉じ込めとなった報告（ID174）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "VFGLBのバッテリー低電圧、MELD移行不成立、閉じ込めの報告"
      - "対応欄は「対応不要」だが、閉じ込め解消とMELD機能の独立確認は不明"
  - source_id: "evidence-list-elv-vfglf-meld-connector-omission-id132"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: コネクタ差し忘れによるMELD不動作（ID132）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "VFGLFのコネクタ差し忘れとブレーカー遮断時のMELD不動作の報告"
      - "対応欄は完了表示だが、是正内容・復旧結果・独立確認は不明"
structured_data:
  items:
    - item: "M14コネクタ ピンアサイン間違い"
      detail: "共有リストID429の個別事例は [[ELV_VFGLF_M14コネクタ誤配線_ID429事例]] を参照。原因説明と現地是正の報告を整理したが、是正後の運転・復旧結果は未記載。"
    - item: "コネクタ差し忘れによるMELD不動作"
      detail: "共有リストID132の一次本文を確認。VFGLFのコネクタ差し忘れにより客先ブレーカー遮断時にMELDが実動作しないとの報告。是正内容・復旧・独立確認は未確認。詳細は[[ELV_VFGLFコネクタ差し忘れ_MELD不動作_ID132事例]]。"
    - item: "MELD接続時のコンタクタ損傷"
      detail: "共有リストID167の個別報告は [[ELV_MELDコンタクタ焼損_活線作業リスク_ID167事例]] を参照。地絡/活線状態との説明は未独立確認。対応状況欄と詳細欄の復旧状態が一致しない。"
    - item: "VFGLBの低電圧によるMELD移行不成立・閉じ込め報告（ID174）"
      detail: "一次リストID174はバッテリー電圧低下によりMELDへ移行せず閉じ込めとなったと報告する。対応欄は「対応不要」だが、閉じ込め解消・電池状態是正・MELD復旧の独立確認は不明。詳細は[[ELV_VFGLB低電圧_MELD移行不成立_閉じ込め_ID174事例]]。電圧値、端子、測定/交換/救出手順は転載しない。ID101の極性誤接続・M1カード損傷とは別事例。"
  source_notes:
    - "原文は添付画像2点を参照するが、2026-10-07時点で指定パスに実ファイルを確認できず、過去の画像確認記録を再検証できない。"
    - "Excel出力のID429本文を確認し、個別事例記録へ接続した。表示・原因・現地対応は出典上の報告として記録し、復旧結果は未記載。一次リストID132はVFGLFのコネクタ差し忘れによるMELD不動作を報告し、個別事例記録へ接続した。対応欄は完了表示だが、是正内容・復旧結果・独立確認は未確認。ID429のピンアサイン誤りとは別事例。一次リストID167は個別記録へ接続し、対応欄間の復旧状態の不一致を保持した。一次リストID174は低電圧によるMELD移行不成立・閉じ込め報告を個別記録へ接続。対応欄「対応不要」を復旧確認とせず、ID101とは原因の異なる別事例として区別した。"
---

# MELD動作に関する不具合共有参照

原文は、M14コネクタのピンアサイン違い、およびコネクタ差し忘れにより客先ブレーカー遮断時にMELDが動作しない件を共有リストの題名として列挙している。一次リストID429の個別経過は[[ELV_VFGLF_M14コネクタ誤配線_ID429事例]]、ID132の個別経過は[[ELV_VFGLFコネクタ差し忘れ_MELD不動作_ID132事例]]を参照。ID132の対応欄は完了表示だが、是正内容・復旧結果・独立確認は未確認。

ID167の個別経過は一次リストで確認し、[[ELV_MELDコンタクタ焼損_活線作業リスク_ID167事例]]へ分けて記録した。盤内作業の活線リスクに関する警告を保持し、対応状況欄と詳細欄にある復旧状態の不一致は解消していない。

一次リストID174は、VFGLBでバッテリー低電圧によりMELDへ移行せず閉じ込めとなったと報告する。対応欄は「対応不要」だが、閉じ込め解消やMELD機能の確認結果を示すとは確認できない。詳細は[[ELV_VFGLB低電圧_MELD移行不成立_閉じ込め_ID174事例]]。ID101の極性誤接続によるM1カード損傷とは原因・症状の異なる別事例であり、互いの根拠にしない。

過去の内容確認記録では、添付にMELD動作試験機能の説明図と、図面番号YE317C142のM14コネクタ注釈図が含まれるとされている。ただし、2026-10-07時点で画像実体を確認できず再検証できない。ピン・電圧・配線変更の指示として扱わない。

## 概略確認フロー（試験・配線手順ではない）

対象機・制御盤・MELD構成と不具合状況を特定し、適用する承認済み接続図・試験要領を確認する。M14コネクタの結線や試験機能を扱う場合は、図面番号・改訂・対象範囲を設計担当に照合する。個別の共有リスト本文が未確認のため、掲載された事例名だけから原因・対策を断定しない。

## 出典

- 原文ノート: [[不具合対応【ELV】/現象（不具合対応）/バッテリー（不具合対応）/MELD動作（不具合）]]
- 原文は添付画像2点を参照するが、2026-10-07時点で指定パスに実ファイルを確認できない。過去の内容確認記録を再検証できず、個別配線値は転載していない。共有リストURLや閲覧トークンは複写していない。
---
schema_version: 1
record_id: "elv-touchless-button-initial-setup-id365"
record_version: 1
title: "タッチレス釦交換後の不作動事例（ID365）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGLF"
  - "VFGLB"
  - "VFGH"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "タッチレス釦"
  - "非接触センサー"
  - "初期設定"
  - "中継基板"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-32-A902.1"
    title: "タッチレス中継基板の設定に関するC資料"
    locator: "リスト参照。本文・改訂・適用範囲未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-touchless-button-no-response-365"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 初期設定不良によるタッチレス釦不作動（ID365）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "操作盤交換後のタッチレス釦不作動、初期設定実施後に動作したとの報告、原因推定と別の可能性に関する記載"
structured_data:
  equipment: "エレベーター。リストの対象機種欄はVFGLF・VFGLB・VFGH。"
  symptom: "かご内操作盤交換後、タッチレス釦が反応しなかった。一方、釦を押し込む操作では正常に動作したとの報告。"
  cause_assessment: "原リストは、工場出荷後に何らかの理由で初期設定が解除された可能性を挙げるが、当該機で独立確認された原因ではない。センサー部の損傷や内部接触不良は原リストが挙げる別の可能性であり、本件で確認された所見とは区別する。"
  reported_actions:
    - "C-32-A902.1を参照して中継基板の設定を行い、タッチレス動作が回復したとの報告。具体的な設定項目・操作は記録しない。"
  outcome: "設定後にタッチレス動作したとの出典報告。継続動作、原因、再発有無は未確認。"
  limitations:
    - "中継基板の設定項目、認識・通信・釦種別設定の具体手順は転載しない。"
    - "C-32-A902.1の本文、改訂、適用機種、承認状態は未確認。"
    - "現場・建物・号機・担当者等の識別情報は記録しない。"
---

# タッチレス釦交換後の不作動事例（ID365）

## 症状と対応

首都工・不具合情報共有リストID365は、かご内操作盤の交換後にタッチレス釦が反応しなかった一方、釦を押し込む操作では正常に動作したと報告する。リストはC-32-A902.1を参照して中継基板の設定を行い、その後タッチレス動作が回復したとしている。設定後の継続動作、再発有無は未確認である。

## 原因に関する記載

原リストは、工場出荷後に何らかの理由で初期設定が解除された可能性を挙げる。これは確定原因ではない。センサー部の損傷や内部接触不良も原リスト上の別の可能性として記載されているが、本件で確認された所見としては扱わない。

C-32-A902.1の本文・改訂・適用範囲は未確認。中継基板の設定項目、センサー認識・基板間通信・釦種別などの具体的な設定内容や操作順は転載しない。本記録を設定変更・点検・復旧の手順として使用しない。
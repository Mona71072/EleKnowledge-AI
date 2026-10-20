---
schema_version: 1
record_id: "catalog-elv-door-speed-change-reference"
record_version: 2
title: "VFGLB/Fの戸開閉速度上限制約とVFGH資料参照"
category: "技術メモ【ELV】２"
record_type: "knowhow"
product: "エレベーター"
model_type: ["VFGLB", "VFGLF", "VFGH"]
document_number: ""
revision: "原資料記載。現行性未確認"
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["戸開閉速度", "機種別資料"]
source_path: "技術メモ【ELV】２/ELV-一般/かご/戸開閉速度変更.md"
source_filename: "戸開閉速度変更.md"
onenote_id: "40bc21ee-a01e-4579-88ad-e30bc3b03f17:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-18-D60.2-J"
    title: "ドア基板 据付資料"
    locator: "原資料内iTDocリンク。未閲覧"
    source_path: ""
  - document_number: "C-18-D31.1-J"
    title: "VFGHドア駆動装置資料"
    locator: "原資料内社内PDFリンク。未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-door-speed-change-001"
    source_type: "vault_original"
    title: "戸開閉速度変更"
    source_path: "技術メモ【ELV】２/ELV-一般/かご/戸開閉速度変更.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["機種別戸開閉速度に関する注意/画像と参照資料があること"]
structured_data:
  knowledge_items:
    - topic: "VFGLB/Fの電動戸開閉速度は工場設定値を超えない"
      statement: "原文はVFGLB/Fについて、電動開閉速度を工場設定値より速く設定しないことと記載している。"
      conditions: ["原文でVFGLB/Fと指定された機種の電動開閉速度に関する制約。"]
      exceptions: ["VFGH向けの記載には同じ速度上限制約の本文がないため、この制約をVFGHへ拡張しない。"]
      rationale: "機種別条件を維持し、工場設定値を超える速度設定を避けるための原文注意事項として記録する。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-door-speed-change-001"]
  source_notes:
    - "C-18-D60.2-JとC-18-D31.1-Jは原資料が参照する別資料であり、このOneNoteノート自体のdocument_numberではない。両資料の本文・最新版は未確認。"
    - "速度の具体値、操作手順、図版の内容は未確認。原文埋め込み画像3点はVault全体の画像名検索で実ファイルを確認できず、原文のVFGLB/Fに対する速度上限制約のみを記録し、VFGHの条件へ一般化していない。"
---

# VFGLB/Fの戸開閉速度上限制約とVFGH資料参照

## VFGLB/Fの原文注意

原文は、VFGLB/Fの電動開閉速度について「工場設定値より速く設定しないこと」と記載している。これは原文にある機種限定の制約として記録したもので、速度の具体値や設定変更の手順を示すものではない。

## VFGHの参照状態

原文はVFGHについてC-18-D31.1-Jを参照し、図版を含むが、本文には速度上限の説明がない。参照資料と図版の内容は未確認のため、VFGLB/Fの制約をVFGHへ当てはめない。

## 適用上の注意

- 戸開閉速度の変更・性能判断には、本記録だけを使用しない。対象機種の承認済み現行資料と必要な安全レビューを確認する。
- C-18-D60.2-JとC-18-D31.1-Jは原文に挙がる参照資料であり、本文の内容・改訂・適用条件は未確認。
- 原文に埋め込まれた図版3点はVault全体検索で実ファイルを確認できず、内容・速度値・操作手順は確認していない。

出典: `技術メモ【ELV】２/ELV-一般/かご/戸開閉速度変更.md`（OneNote ID `40bc21ee-a01e-4579-88ad-e30bc3b03f17:1`）。本文確認日: 2026-10-09。

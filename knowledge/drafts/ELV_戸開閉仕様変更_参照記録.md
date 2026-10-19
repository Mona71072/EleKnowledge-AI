---
schema_version: 1
record_id: "catalog-elv-door-operation-spec-change-reference"
record_version: 2
title: "機種別の戸開閉設定方式に関する原文知見"
category: "技術メモ【ELV】２"
record_type: "knowhow"
product: "エレベーター"
model_type: ["VFGLF", "VFGLB", "VFGH"]
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["戸開閉", "センサー", "仕様変更"]
source_path: "技術メモ【ELV】２/ELV-一般/かご/戸開閉仕様の変更.md"
source_filename: "戸開閉仕様の変更.md"
onenote_id: "a47e5377-35e7-41d5-af5e-683e72561a8c:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-18-D31.1-J"
    title: "VFGHかご上ステーション/ドア駆動装置"
    locator: "原資料内社内PDFリンク。未閲覧"
    source_path: ""
  - document_number: "C-18-D50.1-J"
    title: "VFGLBドア基板"
    locator: "原資料内社内PDFリンク。未閲覧"
    source_path: ""
  - document_number: "C-18-D39.1-J"
    title: "MRL/容量拡張機種かご上ステーション/ドア駆動装置"
    locator: "原資料内社内PDFリンク。未閲覧"
    source_path: ""
  - document_number: "C-18-D60.1-J; C-18-D60.2-J"
    title: "VFGLFドア基板 保守/据付資料"
    locator: "原資料内社内PDFリンク。未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-door-spec-change-001"
    source_type: "vault_original"
    title: "戸開閉仕様の変更"
    source_path: "技術メモ【ELV】２/ELV-一般/かご/戸開閉仕様の変更.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["機種別のセンサー/戸開閉仕様変更に関する説明と図版、複数資料への参照があること"]
structured_data:
  knowledge_items:
    - topic: "VFGLF/VFGLBのセンサー・戸開閉速の変更方式"
      statement: "原文は、VFGLF/VFGLBではセンサーと戸開閉速をドア駆動基板のSWで変更できると記載している。"
      conditions: ["原文でVFGLF/VFGLBとして示された説明。具体的なSW位置・設定・機種適用条件は未確認。"]
      exceptions: ["具体的な設定値や操作手順へ展開しない。"]
      rationale: "変更方式の原文記載を機種限定の概要として保持し、設定操作とは区別する。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-door-spec-change-001"]
    - topic: "MRL機種に関するSW変更の原文補足"
      statement: "原文は、MRL機種については基本的にSWで変更可能で、メンテコン不要と記載している。"
      conditions: ["原文の「基本的に」という限定を保持。個別機種・仕様での例外や現行適用は未確認。"]
      exceptions: ["すべてのMRL機種・設備で必ず成立する条件として扱わない。"]
      rationale: "原文の限定表現を維持し、一律の作業判断へ読み替えない。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-door-spec-change-001"]
    - topic: "VFGHのセンサー・戸開閉速の変更方式"
      statement: "原文は、VFGHではセンサーと戸開閉速をドア駆動基板のJPで変更できると記載している。"
      conditions: ["原文でVFGHとして示された説明。具体的なJP位置・設定・機種適用条件は未確認。"]
      exceptions: ["具体的な設定値や操作手順へ展開しない。"]
      rationale: "VFGLF/VFGLBのSW記載とVFGHのJP記載を混同しないため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-door-spec-change-001"]
  source_notes:
    - "C-18-D31.1-J、C-18-D50.1-J、C-18-D39.1-J、C-18-D60.1-J、C-18-D60.2-Jは原資料が参照する別資料であり、このOneNoteノート自体のdocument_numberではない。各資料本文・改訂・適用条件は未確認。"
    - "原資料には設定図と「工事使用前後」への内部リンクがあり、VFGHのセンサー無効方法等に触れる旨が記されている。リンク先は未確認で、無効化方法や設定値・操作手順は転載していない。"
---

# 機種別の戸開閉設定方式に関する原文知見

## 原文に記載された変更方式

- VFGLF/VFGLB: センサーと戸開閉速は、ドア駆動基板のSWで変更できると記載されている。
- MRL機種: 原文は「基本的に」SWで変更可能で、メンテコン不要としている。例外や個別機種条件は示されていない。
- VFGH: センサーと戸開閉速は、ドア駆動基板のJPで変更できると記載されている。

これらは原文に書かれた変更方式の概要であり、SW/JPの位置、設定値、具体的操作を示すものではない。

## 適用上の注意

- SWとJPの方式を機種間で読み替えない。個別設備の設定変更には本記録を使用せず、対象機種の承認済み現行資料と所管者の確認を要する。
- 原文は内部リンク「工事使用前後」にVFGHのセンサー無効方法等があると案内するが、リンク先の内容は未確認であり、無効化方法は記録していない。
- 参照資料C-18-D31.1-J、C-18-D50.1-J、C-18-D39.1-J、C-18-D60.1-J、C-18-D60.2-Jは未閲覧。図版の内容、機種適用、現行性、安全条件も未確認。

出典: `技術メモ【ELV】２/ELV-一般/かご/戸開閉仕様の変更.md`（OneNote ID `a47e5377-35e7-41d5-af5e-683e72561a8c:1`）。本文確認日: 2026-10-09。

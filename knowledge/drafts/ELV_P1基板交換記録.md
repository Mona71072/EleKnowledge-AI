---
schema_version: 1
record_id: "elv-p1-board-replacement"
record_version: 1
title: "LINKs P1基板交換ノートの構造化記録"
category: "不具合対応(ELV)"
record_type: "procedure"
knowledge_domain: "engineering_business"
organizational_scope: "unknown"
product: "エレベーター"
model_type:
  - "LINKs"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "P1基板"
  - "UCMP"
  - "フラッシュメモリ4"
  - "FMS"
source_path: "不具合対応【ELV】/部品交換/P1基板交換（Links）.md"
source_filename: "P1基板交換（Links）.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:141"
related_ids:
  - "elv-group-operation-issues"
attachment_paths:
  - "不具合対応【ELV】/部品交換/OneNote/P1基板交換（Links） image.emf"
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-p1-board-replacement-original"
    source_type: "vault_original"
    title: "P1基板交換（Links）（原文）"
    source_path: "不具合対応【ELV】/部品交換/P1基板交換（Links）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "バックアップ・書込み・交換確認に関する原文記載"
  - source_id: "evidence-elv-p1-board-layout-photo"
    source_type: "vault_original"
    title: "LINKs P1基板の注釈写真"
    source_path: "不具合対応【ELV】/部品交換/OneNote/P1基板交換（Links） image.emf"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "基板固定部・クリップ・コネクタ周辺を色枠で示す写真の存在"
      - "写真だけでは対象機・基板改訂・取外し手順の現行性を裏付けない"
structured_data:
  preconditions:
    - "原文は交換前の設定読込み、全ブレーカー遮断に言及。安全・資格・機種適用条件は別途確認が必要。"
  steps:
    - order: 1
      action: "原文はフラッシュメモリ4でUCMPを含むデータを読込むと記載。"
      expected_result: "原文記載の退避内容。検証未実施。"
    - order: 2
      action: "原文はブレーカー遮断後のコネクタ取外しとP1基板取外しに言及。"
      expected_result: "原文の記載。図示の取外し位置は未確認。"
    - order: 3
      action: "原文はボタン電池・ジャンパーピン移設に言及。"
      expected_result: "原文の記載。適用条件未確認。"
    - order: 4
      action: "原文は交換後のデータ書込みと複数モードの動作確認に言及。"
      expected_result: "原文記載の確認項目。承認済み試験条件ではない。"
  source_notes:
    - "VFGHとVFGLB/VFGLFでUCMPソフトウェア取得方法が異なるとの原文記載。"
    - "かご上UP運転不可時のUSL操作やFMS書込みに関する記述は別共有情報に依存し、条件・妥当性未確認。"
    - "EMF写真1点は実在と内容を確認し、赤/緑/青の枠で固定部・クリップ・コネクタ周辺を示す。原文参照のPNG1点は2026-10-07時点で指定パスに見つからない。対象基板の適用性は未確認。"
    - "具体的な取外し位置、電池/ジャンパー移設、コネクタ操作は画像・本文から手順として転載しない。"
---

# LINKs P1基板交換ノートの構造化記録

## 原文の構成

原文は、交換前のフラッシュメモリ読込み、電源遮断・コネクタ取外し、P1基板の取外し、ボタン電池・ジャンパーピン移設、交換後のデータ書込み・動作確認を列挙している。VFGHとVFGLB/VFGLFでUCMPソフトウェアの取得方法が異なるとも記載。

## 図版から確認できる範囲

添付写真はP1基板の全景を示し、固定部・クリップ・コネクタ周辺に色枠が付いている。写真は交換対象を理解する補助に留まり、型式・基板改訂・実機の取外し位置を特定する根拠にはしない。

## 概略確認フロー（交換手順ではない）

対象機・制御方式・基板型式を特定し、交換前に全体設定とUCMPソフトウェアのバックアップ可否・入手元を確認する。VFGHとVFGLB/VFGLFでは原文上の取得方法が異なるため、現行の承認済み要領と設計担当へ照合する。交換・部品移設は有資格者が安全措置と復旧計画を確認して実施し、書込み後は適用済み試験要領で確認する。

## 安全・適用上の注意

この整理は未承認の原文ノートであり、基板交換・通電・運転試験の作業手順ではない。機種、ソフトウェア版、感電防止、設定バックアップ、試験範囲を含め、必ず承認済み最新版と有資格者の指示で確認すること。画像内の取外し位置は未読解。

## 出典

- 原文ノート: [[不具合対応【ELV】/部品交換/P1基板交換（Links）]]
- 原文はEMFとPNGの2点を参照。EMFは実在と色枠注釈を確認したが、PNGは2026-10-07時点で指定パスに見つからない。取外し・移設の具体操作は転載していない。
- 共有リストURLは転記していない。

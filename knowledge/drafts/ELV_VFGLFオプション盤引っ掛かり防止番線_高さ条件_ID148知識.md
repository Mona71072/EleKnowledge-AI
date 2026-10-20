---
schema_version: 1
record_id: "knowhow-elv-vfglf-option-board-anti-snag-wire-height-id148"
record_version: 1
title: "VFGLFオプション盤の引っ掛かり防止番線と昇降路高さ条件（ID148）"
category: "不具合対応(ELV)"
record_type: "knowhow"
product: "エレベーター"
model_type:
  - "VFGLF"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "VFGLF"
  - "オプション盤"
  - "引っ掛かり防止番線"
  - "制御ケーブル"
  - "昇降路全高"
  - "15m"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "YA176A980"
    title: "番線施工図"
    locator: "原リスト記載の参照。図面本文・改訂・現行適用は未確認。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-vfglf-option-board-anti-snag-wire-height-148"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: オプション盤手配時の引っ掛かり防止番線有無の件（ID148）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "VFGLFに関する番線施工図の高さ・オプション盤手配条件"
      - "制御ケーブルのU字部と最下部オプション盤との位置関係に基づく設計説明"
      - "AXIEZ/LINKsでは制御盤位置が異なるとの注意、図面本文・現行適用が未確認であること"
structured_data:
  knowledge_items:
    - topic: "オプション盤の引っ掛かり防止番線と昇降路全高"
      statement: "一次リストID148は、VFGLFの番線施工図で、昇降路全高15m以下かつオプション盤を手配した場合に引っ掛かり防止番線を設ける条件を示す。15mを超える場合は、オプション盤を最大個数取り付けても、かご下のU字状制御ケーブルが最下部オプション盤の位置まで上がらないため、設計上不要との説明である。"
      conditions:
        - "対象機種欄はVFGLF。原リストが照会した設計説明であり、他機種・構成への一般適用は未確認。"
        - "15m以下の条件には15mちょうどを含み、15mを超える条件とは区別する。"
        - "オプション盤の手配有無と個数、機器配置が条件に含まれる。"
      exceptions:
        - "AXIEZとLINKsでは制御盤位置が異なるため認識を混同しないようにとの注意がある。各機種の具体的な配置・適用条件は確認していない。"
        - "しきい値は一次リストの設計説明であり、現行図面や個別設備の設計判断・施工指示として確認されたものではない。"
      rationale: "制御ケーブルのU字部が最下部オプション盤の位置まで到達する可能性の有無を、昇降路全高とオプション盤の設置条件で説明する。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-elv-vfglf-option-board-anti-snag-wire-height-148"
  source_notes:
    - "対応欄は『対応不要』。原リストの説明を記録したもので、YA176A980の本文・改訂・現行適用は未確認。番線の施工方法、取付位置、寸法、結線方法は転載していない。"
---

# VFGLFオプション盤の引っ掛かり防止番線と昇降路高さ条件（ID148）

## 概要

首都工・不具合情報共有リストID148は、VFGLFにおけるオプション盤の引っ掛かり防止番線について、昇降路全高と手配条件に関する設計説明を記録する。原リストは対応欄を「対応不要」とし、設計関係者へ確認した説明として以下の理由を挙げている。

## 高さ条件と説明

原リストが参照する番線施工図には、昇降路全高15m以下で、かつオプション盤が手配された場合に番線を設ける条件があると記載されていた。説明では、かご下のU字状制御ケーブルがオプション盤に引っ掛かる可能性があるため番線を設ける一方、昇降路全高が15mを超える場合は、オプション盤を最大個数取り付けても制御ケーブルのU字部が最下部オプション盤の位置まで上がらず、設計上不要としている。

15m以下と15m超は原文の条件区分であり、15m以下には15mちょうどを含む。これはID148の設計説明で、現行図面・個別設備の配置や設計条件と照合した結論ではない。

## 適用上の注意

原リストはAXIEZとLINKsで制御盤位置が異なるため認識を混同しないよう注意している。具体的な機種別配置や本条件の適用範囲は確認できていない。参照図面YA176A980の本文・改訂・現行性も未確認であるため、本記録を番線の要否判断、設計、施工や検査の指示に使用しない。

番線の取付位置、寸法、施工・結線方法は転載していない。個別設備の判断には承認済みの現行図面と機種固有条件の確認が必要である。

## 出典

- 首都工・不具合情報共有リスト.xlsx、ID148（sheet1 row274）。
- YA176A980は原リスト記載の参照資料として記録。図面本文は確認していない。
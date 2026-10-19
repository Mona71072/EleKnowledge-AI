---
schema_version: 1
record_id: "elv-lobby-backup"
record_version: 1
title: "乗場バックアップ回路に関する原文概要"
category: "不具合対応(ELV)"
record_type: "technical_reference"
product: "エレベーター"
model_type:
  - "2C-2BC"
  - "ΣAI-22/220/2200C"
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
  - "乗場バックアップ"
  - "HST"
  - "S1カード"
  - "L1カード"
  - "CAN"
source_path: "不具合対応【ELV】/バックアップ/乗場バックアップ.md"
source_filename: "乗場バックアップ.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:119"
related_ids:
  - "elv-group-operation-issues"
attachment_paths:
  - "不具合対応【ELV】/バックアップ/OneNote/乗場バックアップ image.emf"
reference_links: []
document_references:
  - document_number: "C-8-S450.1-J"
    title: "C-8-S450.1-J"
    locator: "P.10"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-lobby-backup-original"
    source_type: "vault_original"
    title: "乗場バックアップ（原文）"
    source_path: "不具合対応【ELV】/バックアップ/乗場バックアップ.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "乗場バックアップの目的、系統構成、制御別電源条件の原文記載"
structured_data:
  specifications:
    - name: "乗場直電源"
      value: "620H-600H = DC12"
      unit: "V"
      condition: "原文記載の通信成立条件"
    - name: "乗場機器-制御盤直伝信号"
      value: "DIH-DOH = DC3～9"
      unit: "V"
      condition: "原文記載。信号のやりとりが正常に実施されること"
    - name: "HST電源"
      value: "H10-H20 = AC200"
      unit: "V"
      condition: "制御方式によりバックアップ時の状態が異なると原文に記載"
  source_notes:
    - "2C-2BCとΣAI系、VFGLB系とVFGH系でカード・通信・電源供給経路が異なると原文に記載。詳細は承認済み図面で確認すること。"
    - "原文は1箇所以上の乗場機器通信が成立しない場合、高速自動運転できないと記載。現行性未確認。"
    - "添付図は2C-2BCのF/G号機を含むシステム構成図。S1カード、SDC、RS-422、CAN、Z11号機群共通I/O、Z03管制・バック共通I/O等の表記を確認。線の詳細な接続・遮断時動作は承認済み図面で確認すること。"
---

# 乗場バックアップ回路に関する原文概要

## 目的

原文は、マルチカーの保守点検時等に、点検対象外の号機へ影響を及ぼさないためのバックアップ回路として説明している。

## 原文記載の構成・条件

- 原文は高速自動運転に関し、乗場機器との通信が1箇所以上正常であること、乗場直電源620H-600H=DC12V、乗場機器-制御盤の直伝信号DIH-DOH=DC3～9V等を記載。
- 2C-2BCはS1カードとCAN通信、ΣAI系はL1カードとEthernet通信と説明。
- VFGLB系とVFGH系でL1カード電源およびHST電源の遮断時挙動が異なるとの説明がある。

詳細な回路・ブレーカー操作・運転条件は図面と承認済み要領で照合すること。この要約を停電計画や運転継続判断に使用しない。

## 添付図で確認できる2C-2BCの構成

添付のシステム構成図にはF号機・G号機の制御盤、各盤のS1カード、SDCおよびRS-422の表記がある。乗場側には複数号機に関係する機器が描かれ、Z11「号機群共通I/O」とZ03「管制・バック共通I/O」の表記も確認できる。図中にはCANの表記があるほか、破線枠の凡例は「通信系ドライバ 新規、変更開発」となっている。

これは構成を示す図であり、個々の線の詳細な接続条件、ブレーカー遮断時に運転を継続できる号機、点検時の操作順序を定めるものではない。対象機の承認済み回路図・作業要領で照合すること。

## 出典

- 原文ノート: [[不具合対応【ELV】/バックアップ/乗場バックアップ]]
- C-8-S450.1-J P.10参照。
- 添付の2C-2BCシステム構成図を確認し、構成上の表記のみを反映。線の詳細な接続条件と運転・遮断条件は未検証。
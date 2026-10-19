---
schema_version: 1
record_id: "catalog-elv-olt-clt-position-adjustment-reference"
record_version: 3
title: "OLT/CLTの原文電圧表記と位置確認上の注意"
category: "技術メモ【ELV】２"
record_type: "technical_reference"
product: "エレベーター"
model_type: ["LV5", "LV6", "VFGH"]
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["OLT", "CLT", "位置スイッチ"]
source_path: "技術メモ【ELV】２/ELV-一般/かご/OLT-CLT.md"
source_filename: "OLT-CLT.md"
onenote_id: "6ba79df1-5eac-487b-ba83-2ec0bcf4e471:1"
related_ids: ["elv-lv5k-lv6k-clt-dimension-acceleration-case"]
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-18-D45.1-B"
    title: "2光軸タイプ位置スイッチ"
    locator: "原資料記載の社内資料。未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-olt-clt-001"
    source_type: "vault_original"
    title: "OLT-CLT"
    source_path: "技術メモ【ELV】２/ELV-一般/かご/OLT-CLT.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["L型ドア/VFGH総点時のLED確認注意、状態別OLT/CLT電圧表記、2光軸センサーとLV5/LV6のCLT寸法注意が原文にあること"]
structured_data:
  specifications:
    - name: "全開(OLT)時の各4ピン電圧と基板LED"
      value: "OLT=12V、CLT=0V。ドア駆動基板LED点灯と記載"
      unit: "V"
      condition: "原文の状態表記。測定基準・許容範囲・対象基板の適用は未確認"
    - name: "中間位置の各4ピン電圧"
      value: "OLT=-0V、CLT=0V"
      unit: "V"
      condition: "原文表記をそのまま保持。負号の意味・測定基準・許容範囲は未確認"
    - name: "全閉直前の各4ピン電圧と基板LED"
      value: "OLT=0V、CLT=12V。ドア駆動基板LED点灯と記載"
      unit: "V"
      condition: "原文の状態表記。測定基準・許容範囲・対象基板の適用は未確認"
    - name: "全閉時の各4ピン電圧と基板LED"
      value: "OLT=12V、CLT=12V。ドア駆動基板LED点灯と記載"
      unit: "V"
      condition: "原文の状態表記。測定基準・許容範囲・対象基板の適用は未確認"
  safety_warnings:
    - "原文は、L型ドアでドア駆動装置が桁上にある場合、ドア駆動装置内基板LEDでOLT/CLTを調整しないよう注意し、位置スイッチのLEDを確認するよう記載。VFGHの総点時にも注意としている。現行性・個別設備への適用・作業要領としての承認は未確認。"
    - "原文は、CLTの全閉付近で約12Vが出てドア駆動基板のLEDが点灯すると注意している。LED点灯のみを位置状態や合否の判定基準としない。"
    - "原文は、2光軸センサーでLV5/LV6が適用されるLINKs機種についてCLT寸法に注意と記載。寸法基準と対象範囲は未確認。"
  source_notes:
    - "状態別電圧は原文の表記を転記した未検証の観測値であり、仕様値、許容差、合否基準、測定手順を示さない。中間位置の-0Vは原表記を保持し意味を推定していない。"
    - "CLT寸法を扱う首都工・不具合情報共有リストID 432の事例は [[整備済み資料/技術資料/ELV_LV5K_LV6K_CLT寸法_事例記録]] に分離した。リスト記載値は本記録の原資料で検証した仕様ではない。"
    - "C-18-D45.1-Bと00203014.pdfは原文内参照先で、本文未閲覧。認証付き不具合共有リストのリンク先も未閲覧。"
    - "埋め込み図版4点の内容は未確認。原文の注意・電圧表記を現行の調整要領や作業指示へ置き換えない。"
---


# OLT/CLTの原文電圧表記と位置確認上の注意

## 原文に記載された注意

- L型ドアでドア駆動装置が桁上にある場合、原文はドア駆動装置内基板LEDでOLT/CLTを調整しないよう注意し、位置スイッチのLEDを確認するよう記載している。VFGHの総点時にも注意としている。
- 原文は、CLT全閉付近で約12Vが出てドア駆動基板のLEDが点灯すると説明している。
- 2光軸センサーでLV5/LV6が適用されるLINKs機種について、CLT寸法に注意するよう記載している。

## 原文にある状態別の電圧表記

次の値は原文からの転記であり、測定方法・許容範囲・仕様値・合否基準として検証したものではない。

| 原文の状態 | OLT(4ピン) | CLT(4ピン) | 原文の補足 |
|---|---:|---:|---|
| 全開(OLT) | 12V | 0V | ドア駆動基板LED点灯 |
| 中間 | -0V | 0V | 原文の負号をそのまま保持 |
| 全閉直前 | 0V | 12V | ドア駆動基板LED点灯 |
| 全閉 | 12V | 12V | ドア駆動基板LED点灯 |

## 適用上の制約

- 上記は原文記録の保存であり、調整、電圧測定、故障判定、合否判定の手順ではない。LED点灯だけで位置状態を確定しない。
- 現行の機種別資料、対象基板、測定条件、CLT寸法基準、専門レビューは未確認。確認済みの承認要領なしに作業へ使用しない。
- 参照資料C-18-D45.1-B、故障情報PDF、認証付き不具合共有リスト、埋め込み図版4点は未確認。

出典: `技術メモ【ELV】２/ELV-一般/かご/OLT-CLT.md`（OneNote ID `6ba79df1-5eac-487b-ba83-2ec0fbc4e471:1`）。本文確認日: 2026-10-09。

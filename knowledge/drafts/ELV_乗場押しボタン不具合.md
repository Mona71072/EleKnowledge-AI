---
schema_version: 1
record_id: "elv-landing-button-lantern-anomaly"
record_version: 1
title: "乗場押しボタン・ホールランタンの不具合記録"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
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
  - "乗場押しボタン"
  - "ホールランタン"
  - "620A"
  - "CLL2"
source_path: "不具合対応【ELV】/現象（不具合対応）/仮スロー・本スロー・自動運転/乗場押しボタン、ホールランタン（不具合）.md"
source_filename: "乗場押しボタン、ホールランタン（不具合）.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:158"
related_ids: []
attachment_paths:
  - "不具合対応【ELV】/現象（不具合対応）/仮スロー・本スロー・自動運転/OneNote/乗場押しボタン、ホールランタン（不具合） image.png"
  - "不具合対応【ELV】/現象（不具合対応）/仮スロー・本スロー・自動運転/OneNote/乗場押しボタン、ホールランタン（不具合） image 1.png"
  - "不具合対応【ELV】/現象（不具合対応）/仮スロー・本スロー・自動運転/OneNote/乗場押しボタン、ホールランタン（不具合） image 2.png"
reference_links: []
document_references:
  - document_number: "C-6-S1200.1-J"
    title: "C-6-S1200.1-J"
    locator: "P.21"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-landing-button-original"
    source_type: "vault_original"
    title: "乗場押しボタン、ホールランタン（不具合）（原文）"
    source_path: "不具合対応【ELV】/現象（不具合対応）/仮スロー・本スロー・自動運転/乗場押しボタン、ホールランタン（不具合）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "発生状況、交換後も継続した事象、電圧・導通確認の原文記録"
structured_data:
  equipment: "乗場押しボタン・ホールランタン系"
  symptom: "4階のUP押しボタン・ホールランタンが反応しない、または点滅する。制御盤エラーなしとの原文記載。"
  verified_actions:
    - "原文では乗場ステーションのRSW再設定後も解消しなかったと記録。"
    - "原文では乗場ステーションと乗場押しボタンの交換後も解消しなかったと記録。"
    - "押しボタン裏コネクタの620Aを測定し、DC12V記載に対し3Vだったと記録。"
    - "乗場ステーションから押しボタン間のRHLAケーブルで、620AとCLL2（押しボタン灯）の混触を確認したと記録。"
  outcome: "混触を確認したところまでの記録。修理後の復旧結果は原文に記載なし。"
  source_notes:
    - "原文の電圧測定・導通確認は事例記録であり、手順・判定基準として一般化していない。"
    - "原文は添付画像3点を参照しているが、2026-10-07時点で指定パスに実ファイルを確認できず、内容を確認できない。"
---

# 乗場押しボタン・ホールランタンの不具合記録

## 事象と調査記録

原文は4階のUP押しボタン・ホールランタンが反応しない、または突然点滅する事象を記録している。制御盤エラーはなく、他階の呼び出しが良好なため乗場伝送ラインは問題ないと判断した、と記載。

乗場ステーションのRSW再設定、乗場ステーション・押しボタンの交換では解消しなかった。押しボタン裏の620AはDC12V表記に対して3Vを測定し、RHLAケーブルの導通確認で620AとCLL2（押しボタン灯）の混触を確認したとある。

## 未確認

原文は混触の確認までで、修理後の復旧結果や他機種への一般化は確認できない。電気測定・交換を指示する手順として使用しない。

## 出典

- 原文ノート: [[不具合対応【ELV】/現象（不具合対応）/仮スロー・本スロー・自動運転/乗場押しボタン、ホールランタン（不具合）]]
- 参照資料 C-6-S1200.1-J P.21 の本文・版は未確認。原文は添付画像3点を参照するが、2026-10-07時点で指定パスに実ファイルを確認できない。
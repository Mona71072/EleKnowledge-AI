---
schema_version: 1
record_id: "elv-axiez-links-bk2-brake-contact-setting-id63"
record_version: 1
title: "AXIEZ-LINKSのBK2接点設定不良による不動報告（ID63）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "AXIEZ-LINKS"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "BK接点"
  - "BK2"
  - "QB1基板"
  - "ブレーキ"
  - "かご不動"
related_ids:
  - "elv-normal-slow-issues"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-4-A90"
    title: "原リスト記載のC資料"
    locator: "参考資料欄記載。本文・版・適用性未確認。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-axiez-links-bk2-setting-063"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: BK接点の設定不良によりかごが動かない件（ID63）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "不動症状、QB1基板交換での変化なし、BK2接点の所見、原因報告、C資料に基づく設定後の運転確認、ブレーキ開放時の危険注意"
structured_data:
  equipment: "AXIEZ-LINKS（原リストの機種欄。個別設備への適用は未確認。）"
  symptom: "引継検査終了後、工事使用に向けた準備中にかごが動かなくなった。乗場インジケーターは「B・K・↓」。ETPのUP/DN信号では戸が閉まり、動き出そうとするがかごは動かない一方、ブレーキ開放は可能だったとの報告。"
  cause: "原因欄はBK2の設定不良とする。進捗欄ではBK2の動作点が不良で、ブレーキを引いても動作しなかったとの所見がある。原因・機構は原リスト上の報告で独立確認していない。"
  verified_actions: []
  outcome: "QB1基板の交換では動作に変化がなく、元の基板に戻したところ基板部の電圧異常が解消したため、接触不良等を推定したと記載。BK2の設定をC資料に基づき行った後、問題なく運転できることを確認したとの報告がある。いずれも原リスト記載で独立確認していない。ブレーキ開放・巻上機アクセス・錘を使う復旧方法の詳細は安全上転記しない。"
---

# AXIEZ-LINKSのBK2接点設定不良による不動報告（ID63）

首都工・不具合情報共有リストID63は、共有日欄を2021-12-03（Excel値44533の換算）とするAXIEZ-LINKSの報告で、現象分類欄は「機械的;#電気的」、重要度は「中」、エラー表示欄は「特筆すべきエラーなし」。引継検査終了後、工事使用に向けて準備中にかごが動かなくなり、乗場インジケーターに「B・K・↓」と表示された。ETPのUP/DN信号時は戸が閉まり動き出そうとするがかごは動かず、ブレーキ開放は可能だったとの記載がある。

## 調査経過

QB1基板部に電圧異常があったため他現場の基板と交換したが、動作に変化はなかった。元の基板に戻すと電圧異常が解消し、原文は接触不良等を推定している。その後のBK接点確認では、UP/DN信号時にBK2側だけ導通が得られず、BK2の動作点が不良との所見を記録する。C資料に基づきBK接点を設定し、問題なく運転できたとの報告がある。これらはリスト上の調査・結果報告であり、独立確認していない。

## 記述差と安全上の制約

進捗欄の電圧記述には不整合がある。比較項目ではブレーキ開放時とUP/DN信号時、左右ブレーキ間に電圧差はなかったとする一方、BK2接点確認の説明では両状態でブレーキへの印加電圧が異なり、UP/DN信号時のみBK2の動作点に届かなかったとしている。本記録ではどちらかに統一せず、原文内の差として保留する。

備考欄は、ブレーキ開放が可能でもかごを下げられなくなる場合がある危険を指摘し、具体的な復旧準備を提案している。危険なブレーキ開放・巻上機アクセス・錘を使う対処の詳細は転記していない。C-4-A90は参考資料欄の記載を保持したが、本文・改訂・対象適用性は未確認である。本記録はブレーキ調整、運転、閉じ込め救出の手順ではない。

本件は本スロー事例一覧のBK接点項目に対応する詳細記録である。[[ELV_本スロー不具合一覧]]に一覧側の要約を置く。
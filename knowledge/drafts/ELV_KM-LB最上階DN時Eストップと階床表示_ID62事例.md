---
schema_version: 1
record_id: "elv-km-lb-top-floor-dn-estop-and-floor-display-id62"
record_version: 1
title: "KM-LBの最上階DN時Eストップと階床表示不具合（ID62）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "KM-LB"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "Eストップ"
  - "DZU"
  - "着床装置"
  - "ベスタクトスイッチ"
  - "R1基板"
  - "階床表示"
related_ids:
  - "catalog-elv-position-switches-reference"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "EA-98"
    locator: "P.80j（6-13-4 特定距離感知装置の確認）、P.106（*4 データ表示・論理データ）と原リストに記載。本文未確認。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-km-lb-dzu-r1-dual-symptoms-062"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 最上階から自動DN時にDZを抜けるとEストップする件（ID62）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "二つの症状、エラー表示欄、DZU検知・DZプレート・ベスタクトスイッチ・R1基板の調査/交換経過、故障品調査依頼中との原因欄"
structured_data:
  equipment: "KM-LB（原リストの機種欄。対象範囲・現行適用は未確認。）"
  symptom: "①最上階から自動DN時にDZを抜けた付近でEストップし、かごが約1000 mm下がったとの報告。②自動運転時、ランダムな階床がかご内インジケーターに表示されないとの報告。重要度は「↑高」。エラー表示欄は61E、61F、631、64C、712、C11、C13、012を列挙するが、各症状との対応・意味は未確認。"
  error_codes:
    - "61E"
    - "61F"
    - "631"
    - "64C"
    - "712"
    - "C11"
    - "C13"
    - "012"
  cause: "原因欄は着床装置（ベスタクトスイッチ）とR1基板の故障と思われるとし、故障品を稲電へ返却して調査依頼中と記載する。DZプレートの食い込みが浅かったこと、着床装置のDZU誤検知も調査経過にある。確定原因、二症状それぞれへの因果、故障品調査結果は未確認。"
  verified_actions: []
  outcome: "リスト上の経過では、①DZプレート是正後にDZU誤検知を確認し、ベスタクトスイッチ交換後に着床装置検知状況が正常となった。②スイッチ交換後も階床表示不具合が続き、R1基板交換後に解消したとの報告。部品交換後の結果は原リスト記載であり独立確認していない。短絡箇所・電気操作・保守コン操作・試験手順は記載しない。"
---

# KM-LBの最上階DN時Eストップと階床表示不具合（ID62）

首都工・不具合情報共有リストID62は、共有日欄を2021-11-30（Excel値44530の換算）とするKM-LBの報告で、重要度は「↑高」。エラー表示欄には61E、61F、631、64C、712、C11、C13、012が並ぶが、各コードの意味やどちらの症状に対応するかは記載されていない。

## 症状と調査経過

**最上階からの自動DN時のEストップ:** DZを抜けた付近でEストップし、かごが約1000 mm下がったと報告する。進捗欄では、状態確認でDZU異常を確認し、トレースデータを稲電へ送付したところ、DZUとR1基板でエラーが出ているとの連絡を受けたと記載する。DZプレートの食い込みが浅かったため是正し、着床装置検知状況を調べてDZUの誤検知を確認、ベスタクトスイッチ交換後に検知状況が正常となったとの報告である。

**ランダムな階床表示欠落:** 自動運転時に一部階床がかご内インジケーターへ表示されず、未表示階はランダムだったとする。ベスタクトスイッチ交換後もこの表示不具合は解消せず、R1基板交換後に解消したとの報告である。

## 原因・結果の位置づけ

原因欄は、着床装置（ベスタクトスイッチ）とR1基板の故障と思われるとし、故障品を稲電へ返却して調査依頼中と記載する。したがって、交換後に各症状が改善したという報告と、故障原因の確定は区別する。返却品の調査結果、恒久対策、現行機種への適用性は未確認である。

原文の調査欄には保守コン・トレース採取、電気的な短絡による回路区分確認、特定の操作点が記載されているが、具体的な操作・識別情報は転記しない。参照資料EA-98の該当ページも未閲覧であり、本記録はEストップ復旧、試験、診断の手順ではない。位置・終点スイッチ一般の用語は[[ELV_各種位置スイッチ_参照記録]]を参照できるが、同記録は本事例の原因を裏付けない。
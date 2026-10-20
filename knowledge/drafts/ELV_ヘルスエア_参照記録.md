---
schema_version: 1
record_id: "catalog-elv-health-air-reference"
record_version: 8
title: "ヘルスエア資料の参照記録"
category: "技術メモ【ELV】２"
record_type: "catalog"
product: "エレベーター"
model_type: []
document_number: "TI-1406"
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["ヘルスエア", "エアコン", "設定"]
source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/ヘルスエア.md"
source_filename: "ヘルスエア.md"
onenote_id: "a7093375-48f1-412b-9975-f83bd3e65ff1:1"
related_ids:
  - "list-id255-manual-operation-air-conditioner-behavior"
  - "case-elv-health-air-aircon-relay-misselection-damage-id221"
  - "case-elv-health-air-aircon-configuration-omission-id207"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "TI-1406"
    title: "ヘルスエア構造変更に関する注意事項"
    locator: "原資料内SharePoint PDFリンク。未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-health-air-001"
    source_type: "vault_original"
    title: "ヘルスエア"
    source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/ヘルスエア.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["電源/動作/適用設定の複数不具合リンクと参考資料があること"]
  - source_id: "evidence-list-elv-health-air-monitor-no-output-360"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: ヘルスエアモニター出力不良（ID360）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "モニター出力が得られなかった症状、電源系部品の故障と交換後の正常化に関する報告"
  - source_id: "evidence-list-elv-health-air-connector-pin-320"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: コネクタピン抜けによるヘルスエア動作不良（ID320）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "ヘルスエア動作不良、電源系統間コネクタのピン抜けとの原因説明"
  - source_id: "evidence-list-elv-health-air-manual-operation-255"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 手動運転時のエアコン停止動作が廃止された件（ID255）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "手動運転時のエアコン動作に関する問い合わせと、ヘルスエア併設構成を踏まえた設計説明"
  - source_id: "evidence-list-elv-health-air-monitor-transformer-225"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 降圧トランス不良によるヘルスエア出力不良（ID225）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "モニター出力不良、降圧トランス故障との原因報告、交換後に解消したとの原リスト記載"
  - source_id: "evidence-list-health-air-aircon-relay-misselection-damage-221"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: ヘルスエア併設空調のリレー誤品・破損（ID221）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "ID221の個別記録に分離したリレー破損、ヘルスエア/空調不動作、メーカー原因説明と対策報告"
  - source_id: "evidence-list-elv-health-air-version-operation-266"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: ヘルスエアのバージョン別動作説明（ID266）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "ヘルスエア構成/バージョンによる動作差と構造変更資料への言及が原リストにあること"
  - source_id: "evidence-list-elv-health-air-resistor-orientation-206"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: ヘルスエア抵抗器の取付方向に関する照会（ID206）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "抵抗器の取付方向に関する照会、設計回答、据付/保守資料への参照が原リストにあること"
structured_data:
  source_notes:
    - "原文は電圧・設定・結線・手動運転動作・部品極性を含む。数値/操作/案件情報は転載していない。"
    - "協力会社展開用Excel ID360を個別報告として追記。降圧トランス借用後の出力回復、電源ユニット内部品の開放故障と交換後の正常化が記載される。電圧・抵抗値、部品識別子、高電圧測定/交換方法、物件情報は転載していない。メーカーが故障原因を特定できなかったとの記載もあるが、原資料・改訂・適用性は未確認。"
    - "協力会社展開用Excel ID320をID360とは別の個別事例として追記。ヘルスエアの出力不良と接続部のピン抜けとの原因説明を記録。電圧値、端子/コネクタ識別、電源確認・測定/結線方法、機種固有設定、物件情報は転載していない。原因・結果・適用性は未確認。"
    - "協力会社展開用Excel ID255の手動運転時のエアコン動作に関する照会と設計説明を追記。具体的な運転条件、回路/負荷情報、参照資料番号は非転載。原リストの説明、対象範囲、現行性は未確認。"
    - "協力会社展開用Excel ID225をID360とは別のモニター出力不良事例として追記。降圧トランス故障との原因説明と交換後解消の報告を記録。電圧/抵抗値、回路追跡/測定、部品識別/交換方法は転載しない。原因/結果/適用性は未確認。"
    - "協力会社展開用Excel ID221は、関連するID98とは別のタイマーリレー誤品/破損事例として個別記録に分離。定格/電圧/部品識別/電気手順は非転載。空調基板不動作原因、メーカー回答、是正/検査対策の実施/有効性は未確認。"
    - "協力会社展開用Excel ID266は、バージョン別動作説明と構造変更資料への言及のみ追記。運転モード別の挙動/時間値/具体構成は転載しない。TI-1406と記載版の本文/現行性/適用範囲は未確認。"
    - "協力会社展開用Excel ID206は抵抗器の取付方向に関する照会/設計回答と据付/保守資料への参照のみ追記。極性/配線長/機種対応/静観判断/社内URL・パスは転載しない。原回答/参照資料の現行性・適用は未確認。"
---

# ヘルスエア資料の参照記録

原資料はヘルスエア本体/併設空調の電源・動作・設定に関する複数の過去事例、構造変更資料と画像を含む。電圧、設定、結線、操作、個別事例の詳細は転記していない。

## モニター出力不良の報告（リストID360）

協力会社展開用Excel ID360は、ヘルスエアモニターの出力が得られない事例を報告する。原リストには、降圧トランスを借用した後に出力が得られた経緯、電源ユニット内の部品が開放故障していたとの調査結果、その部品の交換後に正常動作したとの記載がある。一方、メーカー・部品メーカーとも故障原因を特定できなかったとしている。各判断、交換後の継続動作、他設備への適用は独立確認していない。

電圧・抵抗値、部品識別子、高電圧測定・交換の方法、現場情報は記録しない。原資料・添付の本文、改訂、対象構成も未確認であり、本記録を測定・修理手順として使用しない。

## 降圧トランス故障との報告（リストID225）

協力会社展開用Excel ID225は、ヘルスエアのモニター出力不良について、降圧トランス故障を原因として挙げ、交換後に不具合が解消したと報告する。原因診断、交換後の継続確認、対象構成、ID360との関連性は独立確認していない。ID360の電源ユニット内部品故障報告とは原因説明の異なる別事例として扱う。

電圧/抵抗値、回路追跡/測定、部品識別/交換方法、現場情報は記録しない。本記録を測定・電気作業・修理手順として使用しない。

## 接続部のピン抜けによる動作不良の報告（リストID320）

協力会社展開用Excel ID320は、ヘルスエアの出力不良について、電源系統間の接続部でピン抜けがあったことを原因として説明する。原因・結果・対象構成・現行適用は独立確認していない。ID360の電源ユニット内部品故障事例とは別報告である。

電圧値、端子/コネクタ識別、電源確認・測定/結線方法、機種固有設定は記録しない。本記録を電気診断・結線・修理手順として使用しない。

## 手動運転時のエアコン動作に関する説明（リストID255）

協力会社展開用Excel ID255は、手動運転時のエアコン動作に関する問い合わせと、ヘルスエア併設構成を踏まえた設計説明を記載している。原リストは複数構成に関する変更説明を行うが、具体的な運転条件、回路/負荷情報、機種適用および現行性は未確認のため記録しない。本記録を運転条件や制御仕様の根拠として使用しない。

## 併設空調のリレー誤品・破損報告（リストID221）

ID221のリレー破損とヘルスエア/空調不動作、メーカー原因説明および対策報告は、[[整備済み資料/技術資料/ELVヘルスエア併設空調リレー誤品破損_ID221事例]]に分離した。定格/電圧/部品識別/電気作業情報は記録しない。ID98の別発生報告と同一視しない。

## バージョン別動作説明（リストID266）

協力会社展開用Excel ID266は、ヘルスエアの構成/バージョンによる動作差と構造変更資料への言及を含む。運転モード別の挙動、時間値、具体構成は記録していない。TI-1406と記載版の本文、現行性、対象機種への適用範囲は未確認であり、運転・設定の根拠に使用しない。

## 抵抗器の取付方向に関する照会（リストID206）

協力会社展開用Excel ID206には、ヘルスエア抵抗器の取付方向に関する照会、設計回答、据付/保守資料への参照がある。極性、配線長、機種対応、静観判断、社内URL/パスは記録していない。原回答と参照資料の現行性・適用は未確認であり、取付/配線の判断には使用しない。

## 併設エアコンの設定漏れ報告（リストID207）

設定漏れによるヘルスエア起動不良の報告は、[[ELV_ヘルスエア併設エアコン設定漏れ_ID207事例]]に個別記録した。設定操作は転載せず、対象範囲・現行適用・参照資料本文は未確認。

現行の機種別電気図・承認済み仕様と品質/設計レビューを確認するまで、設定・結線・故障判断に使用しない。

出典: `技術メモ【ELV】２/ELV-付加仕様（その他）/ヘルスエア.md`（OneNote ID `a7093375-48f1-412b-9975-f83bd3e65ff1:1`）。確認日: 2026-10-08。

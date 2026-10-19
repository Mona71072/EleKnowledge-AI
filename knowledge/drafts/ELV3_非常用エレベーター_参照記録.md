---
schema_version: 1
record_id: "catalog-elv3-emergency-elevator-reference"
record_version: 5
title: "非常用エレベーターの浸水保護条件と関連事例の参照記録"
category: "技術メモ【ELV】３"
record_type: "technical_reference"
product: "エレベーター"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["非常用エレベーター", "浸水", "法令", "取付干渉", "中間JB", "ゴムブッシュ"]
source_path: "技術メモ【ELV】３/非常用エレベーター.md"
source_filename: "非常用エレベーター.md"
onenote_id: "f387bd9f-2ae5-4eb5-80db-909992d0ec42:1"
related_ids:
  - "list-id259-emergency-elevator-mounting-plate-interference"
  - "case-elv-emergency-junction-box-grommet-size-id192"
  - "list-id159-emergency-elevator-pit-station-installation"
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "JEAS"
    locator: "原文に表記のみ。正式文書名・番号・版は未記載"
    source_path: ""
  - document_number: "YE320B269"
    title: "非常用エレベーター据付注意"
    locator: "ID192の参考欄に記載されたG65。本文・版・現行性未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv3-emergency-elevator-001"
    source_type: "vault_original"
    title: "非常用エレベーター"
    source_path: "技術メモ【ELV】３/非常用エレベーター.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["JEASの表記に続く防水・設置高さ・ピット内用具固定の本文記載と、関連不具合共有リストの題名3件があること"]
  - source_id: "evidence-list-elv3-grommet-id192"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: 昇降路中間JBに取り付けるゴムブッシュサイズが不足する件（ID192）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "中間JBのゴムブッシュ寸法差、再作業依頼、対応状況欄と詳細欄の完了状態差"
  - source_id: "evidence-list-elv3-emergency-elevator-pit-station-id159"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: 非常用エレのピットステーション設置（ID159）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "MR機種の非常用エレベーターでピットステーションがピットに取り付けられている件と、寸法/図面参照の存在"
      - "対応欄は完了表示だが、適用・現場適合・安全確認は未確認"
structured_data:
  safety_warnings:
    - "原文はJEASとして、リミットスイッチ、ファイナルリミットスイッチ、点検用コンセント（ピットコンセント）に防水機器を使用するか防滴措置を施し、最下階より高い位置に設置すること、ピット内用具を固定して水に浮かないよう措置することと記載。正式な規格番号・版・現行性・適用条件は原文に示されず、現行設計要件として確認していない。"
  source_notes:
    - "原文は『JEAS』とのみ記載し、JEAS/A505Bという正式番号は記載していないためdocument_numberから除外。"
    - "関連する技術情報リストの題名3件は参照として保持するが、認証付きリンク先の内容、原因、対策、現行性は未確認。"
    - "一次リストID159はMR機種の非常用エレベーターにおけるピットステーション設置項目。寸法・図面・設置位置詳細は転載せず、現行性/適用/現場安全確認は未確認。VFGHの既存ピットステーションノートとは機種が異なるため、位置情報を流用しない。"
  - source_id: "evidence-list-elv3-mounting-plate-interference-259"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: パソコン取付板が取り付けられない（ID259）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "特定構成での取付板と配線カバーの干渉、設計考慮不足との説明、対策製作中との報告"
    - "Excel ID259は取付板と配線カバーの干渉を報告し、設計考慮不足との説明と対策製作中の状況を記載。現場/図面識別、寸法、写真は転載/確認していない。対策の完成・適用・是正結果は未確認。"
    - "浸水・防水・設置位置・固定に関する原文条件は未検証の引用情報であり、現行の設計・施工・保守要領や法令解釈として使用しない。"
---

# 非常用エレベーターの浸水保護条件と関連事例の参照記録

## 原文に記載された浸水保護上の注意

原文は「JEAS」と記したうえで、リミットスイッチ、ファイナルリミットスイッチ、点検用コンセント（ピットコンセント）は防水機器を使用するか防滴措置を施して最下階より高い位置に設置すること、ピット内の用具等は固定して水に浮かないようにすること、と記載している。正式な規格番号・版、具体的な高さや固定方法は記載されていない。

## 関連不具合リストの題名

- 昇降路中間JBに取り付けるゴムブッシュサイズが不足する件
- [[#ID259: パソコン取付板と配線カバーの干渉]]
- SAI2200C(即時予報付)でバンク内に非常用エレがある場合の乗場インジは通常運行時に点灯しない

### ID192: 中間JBのゴムブッシュ寸法差

一次リストID192は、複数のゴムブッシュサイズ差で中間JBの開口を覆いきれなかった状況と、非常用エレベーターの一部に固有の据付注意があるとの報告を含む。個別記録 [[ELV_非常用エレ中間JBゴムブッシュ寸法差_ID192事例]] に整理した。具体的な配線位置/経路は転載せず、再作業の実施・結果は未確認。

### ID259: パソコン取付板と配線カバーの干渉

協力会社展開用リストID259は、特定の構成でパソコン取付板と配線カバーが干渉し、取り付けられなかったと報告する。原リストは設計考慮不足との説明と対策製作中の状況を記載するが、対策の完成・適用・是正結果は確認できていない。現場/図面識別、寸法および添付写真は記録・確認していない。

### ID159: 非常用エレベーターのピットステーション項目

一次リストID159はMR機種の非常用エレベーターにおけるピットステーション設置項目を含み、寸法・図面参照がある。対応欄は完了表示だが、設計根拠、現行性、対象構成への適用、現場適合、安全確認は未確認。寸法・設置位置・図面は転載していない。VFGHのピットステーションノートにある位置記載は別機種のため、本件へ流用しない。

上記のうちID192は一次リスト本文を直接確認した。他の題名はリンク先本文・原因・対策を確認していない。認証付きURLは転載していない。

## 適用上の制約

原文のJEAS記載は現行規格・法令・設計要件との照合をしていない。対象機器、設置位置、固定方法、現行法令、承認済み設計図と安全レビューを確認するまで、設計・施工・保守・非常運転判断に使用しない。
出典: `技術メモ【ELV】３/非常用エレベーター.md`（OneNote ID `f387bd9f-2ae5-4eb5-80db-909992d0ec42:1`）。本文再確認日: 2026-10-09。

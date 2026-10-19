---
schema_version: 1
record_id: "elv-group-operation-issues"
record_version: 9
title: "エレベーター群管理関連の不具合共有一覧"
category: "不具合対応(ELV)"
record_type: "catalog"
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
  - "群管理"
  - "バックアップ運転"
  - "E-CAN"
  - "通信"
  - "SCU-20"
source_path: "不具合対応【ELV】/現象（不具合対応）/群管理（不具合対応）.md"
source_filename: "群管理（不具合対応）.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:145"
related_ids:
  - "elv-group-control-error-codes"
  - "knowhow-elv-2bc-group-error-annunciation-topology-caveat-20261009"
  - "case-elv-cm-ma-group-operation-2c-2bc-id384"
  - "case-elv-vfglb-group-call-role-setting-id189"
  - "case-elv-mr-group-panel-power-disconnected-id371"
  - "case-elv-gs3-board-part-number-setting-scu20-communication-id422"
  - "case-elv-vfglf-scu20-gs3-setting-mismatch-id149"
  - "list-id253-multicar-installation-mode-restriction"
  - "case-elv-e-can-special-operation-hall-call-failure-id171"
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "群管理盤への電源供給線が抜かれる事例"
    locator: "不具合情報リスト ID 371"
    source_path: ""
  - document_number: ""
    title: "3carで群管理運転せず2C-2BC運転となる事例"
    locator: "不具合情報リスト ID 384"
    source_path: ""
  - document_number: ""
    title: "2C-2BC時に乗場押しボタンが接続号機側のみ応答した事例"
    locator: "不具合情報リスト ID 189。詳細はVFGLB個別事例記録を参照"
    source_path: ""
  - document_number: ""
    title: "UPS（アップピークサービス）不動作"
    locator: "不具合情報リスト ID 350"
    source_path: ""
  - document_number: ""
    title: "増設盤の誤結線によるZ03/P1基板損傷"
    locator: "不具合情報リスト ID 349"
    source_path: ""
  - document_number: ""
    title: "PMBK（群管理バックアップ運転）"
    locator: "不具合情報リスト ID 294"
    source_path: ""
  - document_number: ""
    title: "マルチカー・群管理盤結線未完時の据付省力乗場運転モード"
    locator: "不具合情報リスト ID 253"
    source_path: ""
  - document_number: ""
    title: "群管理盤GS3基板の品番設定によるSCU-20通信不成立"
    locator: "不具合情報リスト ID 422。詳細はGS3基板事例記録を参照"
    source_path: ""
  - document_number: ""
    title: "E-CAN通信不良による特殊運転時の乗場呼び切放し不作動"
    locator: "不具合情報リスト ID 171。詳細はE-CAN個別事例記録を参照"
    source_path: ""
  - document_number: ""
    title: "VFGLFのエレベーターとSCU-20盤との通信不成立"
    locator: "首都工・不具合情報共有リスト ID 149。詳細はVFGLF事例記録を参照"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-group-operation-issues-original"
    source_type: "vault_original"
    title: "群管理（不具合対応）（原文）"
    source_path: "不具合対応【ELV】/現象（不具合対応）/群管理（不具合対応）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "群管理関連の不具合共有リスト題名と分類"
  - source_id: "evidence-list-elv-multicar-installation-mode-restriction-253"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: マルチカー且つ群管理盤結線未完の場合の据付省力運転制限（ID253）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "特定の群管理構成/施工段階で据付運転モードが使用できないとの報告と、安全上の制限理由の説明"
  - source_id: "evidence-list-elv-e-can-special-operation-hall-call-failure-171"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: E-CAN通信不良によるNS動作しない件（ID171）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "特殊運転時の乗場呼び切放し不動作と、E-CAN接続異常の原因説明が報告されていること"
  - source_id: "evidence-list-elv-vfglb-group-call-id189"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: ジャンパーピンの設定不良で、2C-2B時乗場押釦が接続号機しか聞かない（ID189）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "VFGLBの2C-2BC時に乗場呼びが一方の接続号機のみ応答したとの報告"
      - "対向する制御機器の役割設定が重複していたとの原因説明"
  - source_id: "evidence-list-elv-vfglf-scu20-gs3-setting-mismatch-149"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: エレベーターとSCU-20盤との通信ができない件（ID149）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "VFGLFの通信不成立と、品目表のGS3基板品番表記・設定不一致との原因説明"
      - "設定変更後に通信状態が良好となったとの報告、および現行性・独立確認が未完了であること"
structured_data:
  source_notes:
    - "群管理（不具合対応）の原文は共有リスト題名のみを列挙。Excelで詳細を確認したID371とID384は個別事例記録へ接続し、他項目の内容を推定していない。"
    - "原文の内部リンク『群管理（技術メモ）』に対応するローカルMarkdownを確認できず、リンク先未解決。"
    - "別途確認したExcelリストID47の2BC構成差は、related_idの独立ノウハウ記録を参照。具体的な異常発報操作は同記録にも転載していない。"
    - "Excel出力のID384は個別事例記録へ接続した。原因/対応欄が途中で切れ、進捗欄が空欄のため、詳細・対応結果は未確認。"
    - "Excel出力のID371は個別事例記録へ接続した。群管理盤への給電停止と復帰報告、原因推定の区別は同記録を参照。"
    - "Excel出力のID422は個別事例記録へ接続した。基板品番指定と構成の不一致、是正後の通信回復報告を記録し、品番・スイッチ/ジャンパ位置などの設定情報は転載していない。"
    - "一次リストID189はVFGLBの2C-2BC時に呼びが片側応答した別事例として個別記録へ接続。役割設定不一致は原リストの原因説明として記録し、具体設定・ジャンパー位置・変更操作は転載していない。対応済み欄に対し設定是正と復旧確認は未記載。ID384のCM-MA事例とは区別する。"
    - "Excel出力のID253は、特定のマルチカー構成/施工段階で据付省力運転モードが使用できないとの報告を追記。隣接号機に関する安全上の懸念と制限理由を原リスト説明として区別した。モード/試験/配線条件は非転載。改善提案・注意追記/機能変更の実施、適用範囲、現行仕様は未確認。"
    - "Excel出力のID171は個別事例記録へ接続。現場/担当者、具体的な診断表示値・接続箇所・電気確認操作は転載していない。参照番号C-8-S438.1と別記録のC-8-S438.1-Jは同一性未確認。"
---

# エレベーター群管理関連の不具合共有一覧

原文は、群管理関連として電源供給線、群管理運転、UPS、増設盤誤結線、PMBK、据付省力乗場運転、E-CAN通信、GS3基板設定等の共有事例を列挙している。原文側の一覧は題名とリスト識別子のみで、ID189、ID371、ID384の一次リスト記載内容はそれぞれの個別事例記録で管理する。

別途確認した首都工・不具合情報共有リストID47の2BC構成差は、[[ELV_2BC群管理異常発報_構成差の注意]]を参照。原文にある具体的な異常発報操作は転記していない。

リストID384の工事使用中の2C-2BC運転事例は、[[ELV_CM-MA_群管理運転せず2C-2BC運転_ID384事例]]に記録した。原因/対応欄の記載が途中で終わり、進捗欄も空欄のため、確定原因や復旧結果は不明。

リストID189のVFGLBにおける2C-2BC時の乗場呼び片側応答は、[[ELV_VFGLB群管理呼び片側応答_役割設定不一致_ID189事例]]に記録した。制御役割の設定不一致は原リストの原因説明。対応済み欄に対して設定是正と復旧確認は確認できず、ID384のCM-MA事例とは別件として扱う。設定値・ジャンパー位置・変更操作は記載していない。

リストID371の群管理盤への給電停止事例は、[[ELV_MR群管理盤給電停止_ID371事例]]に記録した。給電復帰後に復帰したとの記載はあるが、原因説明は推定で、対応後結果は独立確認していない。

リストID422のGS3基板構成不一致によるSCU-20通信不成立事例は、[[ELV_GS3品番設定不一致_SCU-20通信不成立_ID422事例]]に記録した。設計段階の品番指定誤りという原因は原リスト記載で、設定位置・品番の具体情報は同記録に転載していない。

リストID149のVFGLFにおけるエレベーターとSCU-20盤との通信不成立は、[[ELV_VFGLF_SCU-20通信不成立_GS3設定不一致_ID149事例]]に記録した。品目表の基板品番表記・設定と正規品番/設定との不一致は原リストの原因説明で、具体値・変更手順は転載していない。ID422とは同じ通信不成立テーマでも、品番不一致の内容が異なる別事例である。

リストID171のE-CAN通信異常に伴う乗場呼び切放し不作動は、[[ELV_E-CAN特殊運転乗場呼び不作動_ID171事例]]に記録した。通信異常と接続不良は原リストの原因説明であり、表示値・接続識別・確認/復旧手順は転載していない。

リストID253は、特定のマルチカー構成/施工段階で据付省力運転モードが使用できず、部分施工中の隣接号機に関する安全上の懸念から制限されると報告する。改善提案や注意追記/機能変更の実施状況は確認できない。具体的なモード選択、試験方法、結線条件、号機識別は記録しない。本記録を据付調整や運転の手順に使用しない。

## 出典

- 原文ノート: [[不具合対応【ELV】/現象（不具合対応）/群管理（不具合対応）]]
- 原文から共有リストのURL・共有トークンは複写していない。アクセス権・版は未確認。
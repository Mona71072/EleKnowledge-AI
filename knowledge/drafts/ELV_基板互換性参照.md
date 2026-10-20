---
schema_version: 1
record_id: "elv-board-compatibility"
record_version: 6
title: "エレベーター基板互換性の照合上の注意"
category: "不具合対応(ELV)"
record_type: "knowhow"
product: "エレベーター"
model_type:
  - "VFGH"
  - "VFGLB"
  - "VFGLF"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "基板互換性"
  - "P-999"
  - "短絡プラグ"
  - "副番"
source_path: "不具合対応【ELV】/部品交換/基板の互換性.md"
source_filename: "基板の互換性.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:139"
related_ids:
  - "elv-ipu-assembly-substitution"
  - "elv-door-board-replacement"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "P-999"
    title: "電子機器互換表検索システム"
    locator: "ZA081100D"
    source_path: ""
  - document_number: "P-6-S682.1-B"
    title: "VFGH制御盤総組立図"
    locator: ""
    source_path: ""
  - document_number: ""
    title: "注意名板（Excel記載）"
    locator: "YX403C012（番号種別・現物・本文・版未確認）"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-board-revision-mismatch-370"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: KM-LDの基板副番不一致事例"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "部品表・図面・現品の基板副番差と、交換後の動作差、注意名板参照に関するリスト記載"
  - source_id: "evidence-elv-board-compatibility-original"
    source_type: "vault_original"
    title: "基板の互換性（原文）"
    source_path: "不具合対応【ELV】/部品交換/基板の互換性.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "基板互換表の注意書きと資料参照の原文記載"
structured_data:
  knowledge_items:
    - topic: "交換候補の副番は部品表だけで決めず図面・現品・適用条件を照合する"
      statement: "首都工・不具合情報共有リストのID 370は、KM-LDで部品表から手配した制御基板の副番が、図面改訂前に出荷された現品の副番と異なっていた事例を記録する。リスト記載では、交換後に戸開閉速度低下とゲートスイッチ認識不良が生じ、元の副番へ戻すと正常動作した。これは一事例の報告であり、交換可否や復旧方法を示すものではない。"
      conditions: ["KM-LDの個別事例", "機器・図面・品目表の改訂と対象仕様は現行の承認済み資料で確認する"]
      exceptions: ["具体的な部品選定、短絡プラグ、コネクタ、ジャンパ、交換・復旧操作は記載しない。", "リスト参照の注意名板および技術研修資料は本文・現行版を未確認。"]
      rationale: "品目表の候補だけで交換適用を決めず、図面改訂時期と現地構成の差を確認する観点を残すため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-list-board-revision-mismatch-370"]
    - topic: "互換表の表示だけで交換適用を確定しない"
      statement: "原文は、電子機器互換表検索システム上で互換性があるように表示されても、実際には短絡プラグを必要とする組合せがあると注意し、P資料の確認を促している。互換表は候補確認の入口として扱い、適用資料で条件を照合できるまで交換適用を確定しない。"
      conditions: ["原文の対象機器・組合せに関する注意。現行互換表と個別機器への適用は未確認。"]
      exceptions: ["必要なプラグ・ケーブル・設定値は本記録から推定・実施しない。"]
      rationale: "検索結果の互換表示だけでは、実機で必要な条件が網羅されていると限らないため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-board-compatibility-original"]
    - topic: "原文記載のKCD予備品専用基板の組合せ"
      statement: "原文本文は、KCD-1061xとKCD-1060x、KCD-1063xとKCD-1062xの組合せについて、KCD-1050xの予備品専用基板とし、ロータリースイッチOCを7、ジャンパSET0・SET1を開放に設定した記載をしている。また、KCD-1073XとKCD-1072Xの組合せについては、KCD-1050xの予備品専用基板とし、OCを7、SET0～SET7を開放に設定した記載をしている。"
      conditions:
        - "出典本文に記載された特定のKCD型式組合せに限る。"
        - "現行部品、個別機器への適用、表記の現行性は未確認。"
      exceptions:
        - "設定変更や部品交換の指示ではなく、原文記載の内容を示す。"
      rationale: "互換表表示だけで交換適用を確定せず、対象機の正式資料で条件を照合するよう原文が注意している。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-board-compatibility-original"]
    - topic: "副番の近さだけで機種間互換を推定しない"
      statement: "原文は、副番違いが他機種にまたがる例（副番CがVFGLB用、副番DがVFGLF用）を挙げて注意している。候補基板の照合では副番だけで同一性・互換性を判断せず、機種と正式資料の適用条件を併せて確認する。"
      conditions: ["原文中の副番/機種例。一般的な副番体系や他機種への適用は未確認。"]
      exceptions: ["添付画像の組合せ表、設定、予備品条件は未確認のため展開しない。"]
      rationale: "同じような部品番号や隣接する副番が、同一機種・同一条件を意味するとは限らないため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-board-compatibility-original"]
  source_notes:
    - "原文は添付画像8点を参照する。2026-10-09の基板の互換性/OneNoteフォルダーおよびVault画像名検索では該当画像を確認できず、画像表の内容は再検証できない。原文本文で読めるKCD予備品注記は図版内容と区別して記録した。"
    - "検索システムの互換表示だけでは短絡プラグ・ケーブル・予備品条件の要否は確定しない。詳細組合せ・部品番号は本記録に転載しない。"
    - "互換性判断、短絡プラグ使用、ロータリースイッチ・ジャンパ設定を本記録から行わない。"
    - "Excel備考は注意名板YX403C012を参照するが、番号種別、現物、本文、改訂は未確認。交換・互換性・設定判断の根拠として扱わない。"
---

# エレベーター基板互換性の照合上の注意

## 原文の注意

原文は、電子機器互換表検索システムで互換性があるように表示されても、短絡プラグが必要な組合せがあるためP資料を確認するよう注意している。また、副番の違いが機種の違いに対応する例を挙げ、番号だけから互換性を判断しないよう促している。

## 原文本文にある予備品専用基板の注記

原文本文は、次のKCD型式の組合せと、KCD-1050x予備品専用基板に関するスイッチ/ジャンパの状態を記載している。これは原文に書かれた内容の記録であり、現行部品・個別号機への適用確認や設定変更の指示ではない。

| 原文にある型式の組合せ | KCD-1050x予備品専用基板について原文が記載する状態 |
| --- | --- |
| KCD-1061x と KCD-1060x | ロータリースイッチOCを7、ジャンパSET0・SET1を開放 |
| KCD-1063x と KCD-1062x | ロータリースイッチOCを7、ジャンパSET0・SET1を開放 |
| KCD-1073X と KCD-1072X | ロータリースイッチOCを7、ジャンパSET0～SET7を開放 |

原文の表記は`KCD-1073X`など末尾の大文字/小文字を含めて保持した。画像表8点は実ファイルを確認できず、表にある他の互換組合せ・部品条件は本表に含めていない。

過去の内容確認記録では、添付図版に半導体ユニット、短絡プラグ、リボンケーブル、予備品条件の表が含まれるとされている。ただし画像実体が見つからず、2026-10-09時点で再検証できないため、これらの表内容は確認済み情報として扱わない。
画像表に記載された全互換組合せ、部品番号、他のプラグ・ジャンパ条件は本記録に転載していない。本文に明記されたKCD予備品注記も現行の交換・設定根拠にはしない。P-999とP-6-S682.1-Bの本文・現行改訂は未確認。

## 適用上の注意

互換表の検索表示は候補確認に留め、対象機に適用する正式資料で機種、型式、副番と特殊条件を照合する。本記録は照合上の注意であり、個別の交換適用や部品選定を承認するものではない。条件が正式資料で確定できない場合は、交換判断を行わず所管設計担当へ照会する。

個別の互換組合せ、部品番号、プラグ・ジャンパ設定は本記録に転載していない。P-999とP-6-S682.1-Bの本文・現行改訂は未確認。

首都工・不具合情報共有リストID 370には、KM-LDの部品表・図面・現品間で基板副番が一致せず、交換後に動作差が出た一事例がある。リスト記載の結果は現行交換可否や復旧手順の根拠ではない。対象機の現行図面、品目表、適用資料を所管設計担当が照合する。

Excel備考は注意名板YX403C012を参照している。番号種別、注意名板の現物・本文・版は未確認であり、具体的な短絡プラグや交換方法を特定・指示する参照として扱わない。

## 出典

- 原文ノート: [[不具合対応【ELV】/部品交換/基板の互換性]]
- 原文は添付画像8点を参照する。2026-10-09の指定フォルダー・OneNoteフォルダー・Vault画像名検索では画像実体を確認できず、画像表は再検証できない。KCD予備品の具体的な設定状態は原文本文の記載に限って転記した。
- P-999およびP-6-S682.1-Bの本文・改訂は未確認。
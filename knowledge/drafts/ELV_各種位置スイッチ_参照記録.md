---
schema_version: 1
record_id: "catalog-elv-position-switches-reference"
record_version: 5
title: "位置・終点スイッチ機能とTSD/SETSの原文整理"
category: "技術メモ【ELV】２"
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
keywords: ["終点スイッチ", "位置スイッチ", "SETS"]
source_path: "技術メモ【ELV】２/ELV-FAQ/各種位置スイッチ.md"
source_filename: "各種位置スイッチ.md"
onenote_id: "52e6ca63-ff89-4aa2-96d6-ad5a49ff4e91:1"
related_ids:
  - "elv-km-lb-top-floor-dn-estop-and-floor-display-id62"
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "3201.pdf（VFGLFエレベーター技術研修）"
    locator: "原資料内PDFリンク。未閲覧"
    source_path: ""
  - document_number: ""
    title: "12-8-6.pdf（12-8．VFGLBエレベーター 6．SETS）"
    locator: "原資料内PDFリンク。未閲覧"
    source_path: ""
  - document_number: ""
    title: "12-8-3.pdf（12-8．VFGLBエレベーター 3．ソフトウェア構成）"
    locator: "原資料内PDFリンク。未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-position-switch-001"
    source_type: "vault_original"
    title: "各種位置スイッチ"
    source_path: "技術メモ【ELV】２/ELV-FAQ/各種位置スイッチ.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["UOT/DOT、UL/DL、UHS/DHS、CWL、TSD、SETSの機能説明、CWT隙間寸法の記載と保守合理化SW搭載時の動作説明が原文にあること"]
  - source_id: "evidence-list-elv-deep-pit-multiple-dot-348"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: ER適用時にDOTが複数となる件（ID348）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "深いピットのER適用構成でDOTが複数設置されるとの記載と、理由が解決されていない照会"
  - source_id: "evidence-list-elv-terminal-switch-functions-209"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 位置/終点スイッチに関する設計照会（ID209）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "USL/PSL/CWL/USR等の機能・適用条件に関する設計照会と回答が原リストにあること"
structured_data:
  specifications:
    - name: "UOT/DOT"
      value: "終点スイッチ。UL/DLを超えて走行させないための最終スイッチと説明"
      unit: ""
      condition: "原文説明。機種別配線・動作条件は未確認"
    - name: "UL/DL"
      value: "行き過ぎ制限スイッチ。最上階・最下階レベルを超える走行を制限すると説明"
      unit: ""
      condition: "原文説明。機種別条件は未確認"
    - name: "UHS/DHSおよびLINKsのUSL/PSL"
      value: "かご頂部・ピットの作業者を守る安全距離用スイッチとして説明。UHSはかご上、DHSは底部。LINKsはUSLを頂部空間、PSLをピット空間のリミットとして記載"
      unit: ""
      condition: "原文の呼称と機能説明。適用機種・具体距離は未確認"
    - name: "CWL"
      value: "LINKsのみの下降制限スイッチと説明"
      unit: ""
      condition: "原文の対象限定。現行適用は未確認"
    - name: "CWLに関するCWT隙間"
      value: "ピット床面からCWT下端まで1.8m確保と記載"
      unit: "m"
      condition: "原文記載。別注記の測定起点表現との差、機種・設計条件、現行基準は未確認"
    - name: "CWT下枠下面に関する寸法注記"
      value: "開発部門の技術資料では、CWT下枠下面からピットまで1800mm以上を全現場共通で設計と記載"
      unit: "mm"
      condition: "原文内の二次的な記載。出典資料・適用条件・現行性は未確認。CWT下端の記載と同一基準と断定しない"
    - name: "USR/DSR/1USD/1DSDとTSD残距離"
      value: "終点スイッチの動作点に残距離をプリセットし、停止までの現在位置カウンタ変化量を加算して残距離を演算すると説明"
      unit: ""
      condition: "原文の機能説明。制御仕様・故障判定条件は未確認"
    - name: "SETS基準位置センサー"
      value: "UP2/DN2、UP1/DN1を使用し、調速機エンコーダーとともにかごを連続検出。CPUがかご位置に応じたOS検出パターンを演算し、加速度検出レベルを下げて上下部スペース縮小を実現すると説明"
      unit: ""
      condition: "原文の機能説明。OS等の定義、機種適用、設計条件は未確認"
  safety_warnings:
    - "原文は、速度・昇降路レイアウトによりUSLとUSRのスイッチが共用となる場合があると記載。名称だけで個別設備の機能を断定しない。"
    - "保守合理化S/W搭載時について、原文はCWLで一旦停止後、運転釦再押下でULまでブザー鳴動下に4m/min運転可能と記載。この記述は未確認の原文情報であり、運転許可・復旧手順・現行機能を示すものではない。"
    - "CWT隙間の1.8m/1800mmの記載は測定起点の表現が異なる。正式図面・現行設計基準と照合するまで安全寸法や合否基準として使用しない。"
  source_notes:
    - "数値・動作説明は原文の記載を条件付きで保存したもの。承認済みの設計仕様、作業手順、現行の安全基準として検証していない。"
    - "参照PDF3件と埋め込み画像2点は未確認。画像の内容、各参照資料の改訂・適用条件は確認できていない。"
    - "協力会社展開用Excel ID348は、深いピットのER適用構成でDOTが計4つあるとするが、回答欄は『DOT』のみ。複数となる理由・各機能は確認できず、既存資料のDOT-A/DL-A記述とも同一視しない。"
    - "協力会社展開用Excel ID209にはUSL/PSL/CWL/USR等の機能・適用条件に関する設計回答がある。安全機能の代替条件/配置/作動説明は転載せず、原回答の妥当性・適用・現行性は未確認。"
---


# 位置・終点スイッチ機能とTSD/SETSの原文整理

## 原文に記載されたスイッチ機能

- UOT/DOTは終点スイッチ、UL/DLは行き過ぎ制限スイッチとして説明されている。
- UHS/DHSはかご頂部・底部の安全距離用スイッチで、原文は作業者を守る機能として説明。LINKsではUSL/PSLを頂部/ピット空間リミットスイッチとして記載している。
- CWLはLINKsのみの下降制限スイッチと記載されている。
- 速度と昇降路レイアウトにより、USLとUSRが共用となる場合がある。

## Excel ID348の未解決照会

協力会社展開用ExcelのID348は、深いピットでER運転を適用する構成に、通常のDOTに加えて複数のDOTがあり、合計4つとなる事例を記録している。理由を問う照会に対し、回答欄には「DOT」とのみあり、各機器の機能や設置数の根拠は確認できない。

この記載を既存資料のDOT-A/DL-Aの位置・機能説明と同一視したり、設置数の理由を推定したりしない。個別設備の構成と適用理由は、承認済み現行図面・仕様で確認する。

## Excel ID209の設計照会

協力会社展開用Excel ID209には、USL/PSL/CWL/USR等の機能や適用条件に関する設計照会と回答が記載されている。安全機能の代替条件、配置、作動説明は転載していない。原回答の妥当性、対象機種、現行性は未確認であり、設計・据付・運転・安全判断の根拠には使用しない。

## 寸法・運転動作に関する原文記載

- CWLの説明には、ピット床面からCWT下端まで1.8mを確保するとの記載がある。
- 別注記には、開発部門の技術資料でCWT下枠下面からピットまで1800mm以上を全現場共通で設計しているとの記載がある。測定起点の表現が異なるため、同一条件とは断定していない。
- 保守合理化S/W搭載時のCWL停止後の動作として、運転釦再押下でULまでブザー鳴動下に4m/min運転可能との記載がある。これは原文の説明であり、運転許可や復旧手順ではない。

## TSD/SETSの機能説明

原文は、USR/DSR/1USD/1DSDが動作するたびに残距離をプリセットし、停止までの現在位置カウンタ変化量を加算してTSD残距離を演算すると説明している。また、SETSではUP2/DN2・UP1/DN1の基準位置センサーと調速機エンコーダーでかごを連続検出し、CPUが位置に応じたOS検出パターンを演算して加速度検出レベルを下げ、昇降路上下部のスペース縮小を実現すると記載されている。用語定義・機種適用・設計条件は未確認。

## 適用上の制約

- 記載した寸法、速度、スイッチ機能は原文の未検証情報であり、現行設計仕様、据付寸法、運転・復旧手順、合否基準として使用しない。
- CWT寸法の起点、速度/レイアウトによるスイッチ共用、個別機種の構成は、対象設備の承認済み図面と所管者に確認する。
- 参照PDF3件と埋め込み画像2点は未確認。資料の改訂、図版の内容、適用範囲を確認できていない。
- [[ELV_KM-LB最上階DN時Eストップと階床表示_ID62事例]]は、DZU検知等を含む別の個別事例。ここにある位置・終点スイッチ一般の説明は、同事例の原因・機種適用を裏付けない。

出典: `技術メモ【ELV】２/ELV-FAQ/各種位置スイッチ.md`（OneNote ID `52e6ca63-ff89-4aa2-96d6-ad5a49ff4e91:1`）。本文確認日: 2026-10-09。

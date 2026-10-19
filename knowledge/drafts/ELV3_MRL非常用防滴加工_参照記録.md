---
schema_version: 1
record_id: "catalog-elv3-mrl-emergency-waterproofing-reference"
record_version: 2
title: "MRL非常用エレベーター防滴の機種別記載と安全条件"
category: "技術メモ【ELV】３"
record_type: "technical_reference"
product: "エレベーター"
model_type: ["MRL", "KM-LD"]
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["非常用エレベーター", "防滴", "浸水"]
source_path: "技術メモ【ELV】３/防滴加工(MRL非常用エレ).md"
source_filename: "防滴加工(MRL非常用エレ).md"
onenote_id: "b79c5525-bb8d-4a68-bf43-26d279bd9f8c:1"
related_ids: []
attachment_paths: ["添付画像/防滴加工(MRL非常用エレ) image.emf"]
reference_links: []
document_references:
  - document_number: "YE401A207"
    title: "防滴カバー据付図"
    locator: "原資料記載。対応EMF添付は実在確認、内容未確認"
    source_path: "添付画像/防滴加工(MRL非常用エレ) image.emf"
  - document_number: "JEAS/A505B"
    title: "JEAS/A505B"
    locator: "原資料内の見出し参照。本文・版未確認"
    source_path: ""
  - document_number: ""
    title: "機械室なし非常用エレベーター防水保護等級証明書"
    locator: "原資料内リンク。未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv3-emergency-waterproofing-001"
    source_type: "vault_original"
    title: "防滴加工(MRL非常用エレ)"
    source_path: "技術メモ【ELV】３/防滴加工(MRL非常用エレ).md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["KM-LD/その他MRの防滴方式、IPX2/IPX7、非常運転時の回路条件とピット内異物注意が原文にあること"]
structured_data:
  specifications:
    - name: "新AXIEZ拡張容量(KM-LD)の防滴方式"
      value: "非常用エレベーター適用は想定されていなかったと記載。IPX2以上の防水措置では、盤自体の防滴設計より防滴カバーが総合的に妥当と判断され、原文時点で採用中と説明"
      unit: ""
      condition: "原文の判断・当時状況。現行採用・設計妥当性・適用条件は未確認"
    - name: "KM-LDで防滴カバーを使う盤"
      value: "トランス盤、リアクトル盤、増設盤(2C-2BC)"
      unit: ""
      condition: "原文記載。対象型式・現行構成・据付図未確認"
    - name: "KM-LDで盤側の防滴仕様が可能とする対象"
      value: "監視盤JB、その他JB"
      unit: ""
      condition: "原文記載。具体仕様・機種適用・現行性未確認"
    - name: "LINKsとの異機種群管理時"
      value: "原文は最新制御方式のVFGLF用マイサート盤(ΣAI-2200C相当)を適用し、群番によって盤側防滴仕様が可能と記載"
      unit: ""
      condition: "「最新」の基準時点、群番条件、現行仕様は未確認"
    - name: "群管理盤(ΣAI-22C～2200C)の防滴制約"
      value: "原文は防滴カバー・盤側防滴仕様とも不可とし、非常用号機以外の昇降路へ設置するよう記載"
      unit: ""
      condition: "原文記載。機種/構成条件・設計承認・現行性未確認"
    - name: "その他MR機種"
      value: "監視盤JB、その他JBは盤側防滴仕様が可能と記載"
      unit: ""
      condition: "原文記載。個別機種の仕様は未確認"
    - name: "KM-LD非常用の乗場機器取付"
      value: "乗場電源BOX・乗場STを全階で嵩上げして取り付ける必要があると記載"
      unit: ""
      condition: "原文記載。必要高さ・構造・現行設計条件未確認"
    - name: "防水保護等級に関するJEAS/A505B見出し下の記載"
      value: "駆動装置・制御盤にIPX2以上の有効な防水措置。IPX7装置の場合は水没防止の設置対策不要と記載"
      unit: ""
      condition: "原文記載の主張。規格本文・試験条件・現行解釈は未確認"
  safety_warnings:
    - "原文は浸水短絡がエレベーターへ影響しないようにすること、ファイナルリミットスイッチを水没しないよう最下階より高い位置に設置することと記載。現行法令・設計要件・具体高さは未確認。"
    - "原文はコンペンスイッチ、火災感知器、冠水感知器、かご下秤装置を非常運転時に制御回路から切り離し、濡れていても非常運転に支障がないことと記載。回路構成・切離し方法・非常運転の操作手順として転載/使用しない。"
    - "原文はピット内にオイル缶・布切れ等の異物を置かないよう記載。これは原文注意の記録であり、現行の点検・清掃手順を示さない。"
    - "IPX等級、設置位置、盤ごとの防滴可否、非常運転条件はJEAS/A505B本文・認証資料・現行設計図で照合していない。防滴設計、機器移設、電気回路変更、非常運転判断に本記録を使用しない。"
  source_notes:
    - "document_numberは空欄。YE401A207は防滴カバー据付図、JEAS/A505Bは原文の参照見出しとしてdocument_referencesに分離。"
    - "原文埋め込み画像PNGはVault検索で確認できず、EMF添付1点は実在のみ確認。図面内容は未確認。証明書リンクも未閲覧。"
    - "原文の『現状』『最新』等は記録作成時点不明の記述で、現在の採用状況・最新仕様を意味しない。"
---

# MRL非常用エレベーター防滴の機種別記載と安全条件

## 機種別の防滴方式に関する原文記載

- 新AXIEZ拡張容量(KM-LD)は非常用エレベーター適用を想定していなかったと原文は説明する。IPX2以上の措置では、盤自体の防滴設計よりカバー適用が総合的に妥当と判断され、原文作成時点で防滴カバーを採用中としている。
- KM-LDのカバー対象としてトランス盤、リアクトル盤、増設盤(2C-2BC)、盤側の防滴仕様が可能な対象として監視盤JB・その他JBを挙げる。
- LINKsとの異機種群管理では、VFGLF用マイサート盤(ΣAI-2200C相当)を適用し、群番によって盤側の防滴仕様が可能との記載がある。一方、ΣAI-22C～2200C群管理盤はカバー・盤側防滴とも不可で、非常用号機以外の昇降路へ設置するよう記載する。
- その他MR機種は監視盤JB・その他JBで盤側防滴仕様が可能とする。KM-LD非常用では、乗場電源BOX・乗場STを全階で嵩上げして取り付ける必要があると記載する。

これらは原文の機種別記載であり、現行仕様、盤構成、設置条件を確認したものではない。

## JEAS/A505B見出し下の原文記載

原文は、機械室レス非常用エレベーターで駆動装置・制御盤にIPX2以上の有効な防水措置を行うこと、IPX7装置なら水没しない位置へ設置する対策は不要とすることを記載する。また、浸水短絡の影響防止、ファイナルリミットスイッチの最下階より高い設置、非常運転時の各スイッチ/センサー/秤装置の制御回路切離し、ピット内異物を置かない注意を挙げている。

回路切離しの具体方法、設置高さ、機器適用、非常運転操作の手順は記載していない。

## 添付・参照先と適用上の制約

- 防滴カバー据付図YE401A207のEMF実ファイルは確認したが内容未確認。PNG埋め込み画像はVault内で確認できなかった。
- JEAS/A505B本文と機械室なし非常用エレベーター防水保護等級証明書は未閲覧。
- IPX等級、盤ごとの防滴可否、浸水条件、非常運転時の安全要件は現行法令・規格・承認済み設計図と照合するまで、設計・施工・回路変更・非常運転判断に使用しない。

出典: `技術メモ【ELV】３/防滴加工(MRL非常用エレ).md`（OneNote ID `b79c5525-bb8d-4a68-bf43-26d279bd9f8c:1`）。本文確認日: 2026-10-09。

---
schema_version: 1
record_id: "catalog-elv3-pit-in-recovery-reference"
record_version: 3
title: "PitIn機能の目的・表示・製品適用に関する参照"
category: "技術メモ【ELV】３"
record_type: "technical_reference"
product: "エレベーター"
model_type: ["CM-LB", "KM-LD"]
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["PitIn", "ピット侵入検知", "復帰"]
source_path: "技術メモ【ELV】３/モード/ピットインモード復帰手順.md"
source_filename: "ピットインモード復帰手順.md"
onenote_id: "5f0b234c-23e2-4b01-822d-b2d7d43454f3:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "ピットインモードの復帰手順について"
    locator: "SharePoint技術情報リストID 265。リンク先未閲覧"
    source_path: ""
  - document_number: ""
    title: "機械室有りエレベーター重篤災害再発防止対策に向けた製品切替に係わる件"
    locator: "原資料内SharePoint参照。未閲覧"
    source_path: ""
  - document_number: ""
    title: "社外秘（協力会社開示可）添付①：ピット侵入検出機能 詳細.pdf"
    locator: "原資料内認証付きリンク。未閲覧"
    source_path: ""
  - document_number: "YE320B397_0"
    title: "据付/保守切替コネクタ関連電気図面"
    locator: "原資料内リンク。未閲覧"
    source_path: ""
  - document_number: "YE312C376_C"
    title: "ピット侵入検知回路概要図"
    locator: "原資料内リンク。未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv3-pitin-recovery-001"
    source_type: "vault_original"
    title: "ピットインモード復帰手順"
    source_path: "技術メモ【ELV】３/モード/ピットインモード復帰手順.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["PitInモードの目的・表示・状態保持、保守ソフト対応条件、24年10月生産からの適用記載が原文にあること"]
  - source_id: "evidence-list-elv3-pitin-recovery-265"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: ピットインモードの復帰手順について（ID265）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "PitIn関連の復帰手順と運転/保守上の注意が原リストに記載されること"
structured_data:
  specifications:
    - name: "PitInモードの目的"
      value: "保守時に乗場運転阻止コネクタを取り外す手間を省き、作業者の安全を確保するモードと説明"
      unit: ""
      condition: "原文の説明。安全機能の現行仕様・適用機種は未確認"
    - name: "PitInモードの状態表示"
      value: "電源投入直後の7セグにPin、R1カードLEDにフリッカー表示と記載"
      unit: ""
      condition: "保守ソフト対応かつ据付完了フラグ成立時に移行すると原文に記載。表示仕様の現行性未確認"
    - name: "PitInモードの状態保持"
      value: "#29落ち相当の状態を作り、リセット後も解除条件を満たすまでPitInモードを保持すると記載"
      unit: ""
      condition: "原文の機能説明。解除条件・個別機種差は転載せず、適用未確認"
    - name: "製品切替時の適用記載"
      value: "『24年10月生産より』機械室有りエレベーターにもピット侵入検知機能を適用。新設工事ではCM-LB（VFGLB-K）が対象と記載"
      unit: ""
      condition: "原文の時期・対象記載。年の解釈、現行適用・生産範囲は未確認"
    - name: "保守ソフト接続時の機能有効化"
      value: "工場出荷時（据付中を含む）は機能無効、メンテコン接続により自動的に有効となると記載"
      unit: ""
      condition: "原文記載。機種/ソフト条件・現行動作・承認済み手順は未確認"
  safety_warnings:
    - "原文は解除方法、電源/CPU/MCBリセット、スイッチ短絡、乗場ボタン保持、ピットスイッチ復帰、モード切替、回路コネクタ付替え、運転制限中の速度/方向条件を含む。危険な操作手順・解除条件は本記録に転載していない。"
    - "保守コンソール接続がピット侵入検知機能の自動有効化につながると原文に記載。現場での接続判断・作業開始・復帰操作は、対象機種の承認済み現行手順と責任者確認なしに行わない。"
    - "SharePointの技術情報・機密添付・回路図は未閲覧。現行性、対象機種、制御仕様、開示条件は未確認。"
  source_notes:
    - "解除方法①/②、検出条件の論理式、回路短絡、乗場/ピット操作、メンテコン解除メニュー、具体的な速度/方向動作は、危険な作業手順となるため転載していない。"
    - "関連するSharePointリンク・機密添付・電気図面は閲覧していない。認証付きURLは保存/再掲していない。"
    - "原文の『KM-LDではできなかった』との個別記述にある原因推測は未確認のため採用していない。"
    - "協力会社展開用Excel ID265にも解除/復帰方法と運転/保守上の注意が記載される。解除条件、リセット、短絡、乗場/ピット操作、運転操作、遠隔監視関連の詳細は転載せず、現行性/機種適用は未確認。"
---

# PitIn機能の目的・表示・製品適用に関する参照

## 機能の目的と表示

原文はPitInモードを、保守時の乗場運転阻止コネクタ取り外しの手間を省き、作業者の安全を確保するモードとして説明する。条件成立時は電源投入直後の7セグに「Pin」、R1カードLEDにフリッカーを表示すると記載している。

PitIn中は#29落ち相当の状態となり、リセット後も解除条件を満たすまでモードが保持されると原文に記載されている。解除条件・解除操作はここでは記録していない。

## 製品適用に関する原文記載

- 「24年10月生産より」機械室有りエレベーターにもピット侵入検知機能を適用し、新設工事ではCM-LB（VFGLB-K）が対象と原文にある。年の解釈、生産範囲、現行適用は未確認。
- 工場出荷時（据付中を含む）は機能無効だが、メンテコン接続により自動的に有効となると原文は注意している。現行の機種/ソフト条件は未確認。

## Excel ID265の追加出典

協力会社展開用Excel ID265にもPitIn関連の復帰手順と運転/保守上の注意が記載される。解除条件、リセット、短絡、乗場/ピット操作、運転操作、遠隔監視関連の詳細は転載していない。原リストの説明と既存原文との整合、現行性、機種適用は未確認。

## 適用上の制約

原文にはピット侵入検知条件、運転制限状態、解除手順、リセット、回路短絡、制御盤コネクタ付替え、乗場/ピット操作が含まれるが、これらは転載していない。承認済みの現行機種別要領と責任者確認なしに、作業開始・保守コン接続・解除・運転判断へ本記録を使用しない。SharePointの詳細資料と回路図も未閲覧。

出典: `技術メモ【ELV】３/モード/ピットインモード復帰手順.md`（OneNote ID `5f0b234c-23e2-4b01-822d-b2d7d43454f3:1`）。本文確認日: 2026-10-09。

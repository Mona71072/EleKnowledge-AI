---
schema_version: 1
record_id: "catalog-elv-smoke-control-door-reference"
record_version: 5
title: "遮煙ドア認定・安全仕様資料の参照記録"
category: "技術メモ【ELV】２"
record_type: "catalog"
product: "エレベーター"
model_type: []
document_number: "TI-1407"
revision: "原資料に更新資料記載。現行性未確認"
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["遮煙ドア", "大臣認定", "煙感知器"]
source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/遮煙ドア.md"
source_filename: "遮煙ドア.md"
onenote_id: "019a54aa-c81c-4677-8aba-fee2f991c38d:1"
related_ids:
  - "list-id290-emergency-elevator-fire-control-condition"
  - "list-id154-mrl-smoke-shaft-detector-installation-report"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "TI-1407"
    title: "遮煙大臣認定番号更新"
    locator: "原資料内SharePoint PDFリンク。未閲覧"
    source_path: ""
  - document_number: "S-31-50.1"
    title: "遮煙乗場ドア"
    locator: "首都工・不具合情報共有リストID346に記載された参照資料。本文・版・現行性は未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-smoke-door-001"
    source_type: "vault_original"
    title: "遮煙ドア"
    source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/遮煙ドア.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["認定/煙感知器/停電時動作等の過去情報と資料参照があること"]
  - source_id: "evidence-list-smoke-door-certification-labels-346"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 遮煙ドア認定シールの区分に関する説明"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["認定番号、戸閉方式、戸・枠仕様、シール表示、耐火性能と法令に関する説明がリストに記載されていること"]
  - source_id: "evidence-list-emergency-elevator-fire-control-condition-290"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 非常用エレベーターで火災管制運転が必須となる条件（ID290）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "個別現場条件により遮煙ドアと火災管制運転の適用が求められたとの原リスト説明"
  - source_id: "evidence-list-smoke-door-fire-alarm-requirement-id227"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 遮煙認定と火災管制連動の確認漏れ報告（ID227）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "建物仕様変更後の火災管制連動と認定仕様の適合懸念、原リスト記載の対応案"
  - source_id: "evidence-list-mrl-smoke-shaft-detector-id154"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: 遮煙適用現場の昇降路内煙感知器に関する報告（ID154）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "MRL機種の遮煙適用現場における煙感知器設置状況についての出典上の報告"
      - "対応欄は完了表示だが、法令/認定適合・対象現場への適用・是正結果は未確認"
structured_data:
  source_notes:
    - "原文は法令/認定、安全スイッチ短絡関連、煙感知器条件、バックアップ動作を含む。操作/法令/設定条件は転載していない。"
    - "リストID346の認定表示・法令説明は未検証の出典主張として本文に分離。認定書、S-31-50.1、法令/告示の原文は未確認で、設計/施工/検査/適合判定に使用しない。"
    - "リストID290は個別現場条件と火災管制運転の適用に関する説明を含むが、現場配置、法令解釈、必要仕様、承認図書は未確認。一般的な法令/設計要件として扱わない。"
    - "協力会社展開用Excel ID227は建物仕様変更後の火災管制連動と認定仕様の適合懸念を報告し、申請書類/認定表示に関する対応案を記載する。法令要件、認定適合、提案の承認/実施/結果は未確認。"
    - "一次リストID154はMRL機種の遮煙適用現場における昇降路内煙感知器の設置状況を報告し、数値/基準に関する記述を含む。法令/認定根拠、適用条件、現行性、対応結果は未確認。数値・設置基準・現場情報は転記せず、法令/設計適合判断に使用しない。"
---

# 遮煙ドア認定・安全仕様資料の参照記録

原資料は遮煙認定、煙感知器、停電時バックアップ動作、関連する過去情報/資料への参照を含む。法令・認定条件や安全スイッチの操作、機能設定は転記していない。

現行の大臣認定仕様、機種別承認図、現行法令と安全手順を設計/防災担当が確認するまで、設計・試験・運転判断に使用しない。

## リストID346の未照合記載

首都工・不具合情報共有リストID346は、認定番号が戸閉方式（CO、2S、2CO等）や三方枠/乗場戸の仕様条件で異なると説明する。また、金色/銀色のシールを特定防火設備/防火設備の区分に対応付け、窓の有無やCAS-1046の括弧内数字も区分の手掛かりになるとしている。

同じ項目は、防火設備と特定防火設備の耐火時間をそれぞれ20分/1時間とする説明、両面に関する要件、2000年6月以降の要件、建築基準法第109条/第112条、平成12年告示第1360号/第1369号、および非常用エレベーターの戸仕様に関する説明も含む。これらはリスト上の主張であり、法令・告示・認定書の要件として照合していない。

シール表示、窓の有無、括弧内数字だけで認定区分を推定しない。参照先S-31-50.1、当該設備の大臣認定書、法令・告示の現行本文を所管部門が確認するまで、設計・施工・検査・適合性判断に使用しない。

## 非常用エレベーターの火災管制運転に関する個別報告（リストID290）

協力会社展開用Excel ID290は、特定現場の建築/戸配置条件により遮煙ドアの適用と火災管制運転が求められたと説明する。また、現場固有の設計背景を所管設計に確認するよう案内している。現場配置、法令解釈、適用要件、火災管制運転の仕様および承認図書は確認できていない。

この報告を一般的な法令/設計要件として扱わず、個別設備の適用可否や運転仕様の根拠にしない。認定書、現行法令、承認済み建築/昇降機図書と所管者確認が必要である。現場名、階/扉の配置、具体的運転仕様および監視盤構成は記録しない。

## 建物仕様変更後の火災管制連動懸念（リストID227）

協力会社展開用Excel ID227は、建物側仕様変更後に火災管制連動が成立しない状態となり、遮煙認定仕様との適合性に懸念が生じたと報告する。原リストは申請書類や認定表示に関する対応案を記載するが、法令/認定要件、個別設備の適合性、対応案の承認/実施/結果は独立確認していない。対応案を実施指示として扱わず、認定書・現行法令・承認済み設計図書を所管設計/防災部門が確認するまで、適合・運転判断に使用しない。現場/顧客/配置、火災信号/電源構成、認定表示の具体処置は記録しない。

## MRL機種の遮煙適用現場における煙感知器設置状況（リストID154）

一次リストID154は、MRL機種の遮煙適用現場について、昇降路内の煙感知器設置状況に関する報告を記載する。対応欄は完了表示だが、法令/認定根拠、対象現場の条件、設置要否、対応実施後の状態、現行設計への適用性は確認できていない。数値・基準・設置条件は転記しておらず、この報告を設置要否や法令適合の一般判断に使用しない。認定書、現行法令、承認済み建築/昇降機図書を所管設計/防災部門が確認する必要がある。

出典: `技術メモ【ELV】２/ELV-付加仕様（その他）/遮煙ドア.md`（OneNote ID `019a54aa-c81c-4677-8aba-fee2f991c38d:1`）。確認日: 2026-10-08。

---
schema_version: 1
record_id: "elv-insulation-resistance-test-review-hold"
record_version: 3
title: "絶縁抵抗試験メモの確認記録（安全レビュー保留）"
category: "不具合対応(ELV)"
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
keywords: ["絶縁抵抗試験", "高圧測定", "残留電荷", "安全レビュー"]
source_path: "不具合対応【ELV】/現象（不具合対応）/絶縁抵抗試験（不具合対応）/絶縁抵抗試験（注意点）.md"
source_filename: "絶縁抵抗試験（注意点）.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:147"
related_ids:
  - "case-elv-insulation-test-fire-alarm-panel-board-damage-id162"
  - "elv-axiez-links-boon-grounding-misconnection-id69"
  - "list-id307-power-line-insulation-resistance-report"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-7-A30-J"
    title: "絶縁抵抗試験（高圧メガー測定）に関する基準"
    locator: "原文内参照。本文・改訂未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-insulation-test-review-hold"
    source_type: "vault_original"
    title: "絶縁抵抗試験（注意点）"
    source_path: "不具合対応【ELV】/現象（不具合対応）/絶縁抵抗試験（不具合対応）/絶縁抵抗試験（注意点）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["高圧試験後の残留電荷に関する説明と、具体的な測定器接続/放電手順の記載があること"]
  - source_id: "evidence-list-elv-power-line-insulation-307"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 動力線の絶縁抵抗不良（ID307）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports: ["動力回路の絶縁抵抗に関する異常報告と、原因未確定の調査経過"]
  - source_id: "evidence-list-elv-insulation-test-fire-alarm-board-id162"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: 絶縁抵抗試験時の火報盤内基板焼損（ID162）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports: ["絶縁抵抗試験に伴う火報盤内基板焼損の報告。試験条件・原因機構・復旧結果は未確認。"]
structured_data:
  source_notes:
    - "原文は残留電荷・放電の説明に続き、測定器の接続、待ち時間、接地を含む実施手順を記載している。本記録では手順、電圧値、時間、機器指定を複写・再構成していない。"
    - "原文が参照するC-7-A30-Jの本文・版、対象回路/機器、測定器要件、資格要件、正しい試験後処置は未確認。原文記載を正式手順として扱わない。"
    - "電気安全責任者/有資格担当者による現行基準との照合とレビューが完了するまで、試験・放電・接地・機器切離しの実施根拠に使用しない。"
  related_incidents:
    - "ID307は動力回路の絶縁抵抗に関する別報告。測定値・現場/設備識別・端子/配線・修理/試験手順は転載せず、原因と解消結果は未確認として扱う。ID69/83の制御回路誤結線事例とは別事象。"
    - "ID162は絶縁抵抗試験に伴う火報盤内基板焼損の別報告。試験電圧/測定値、対象回路、端子/配線、切離し/復旧手順を転載せず、原因機構・是正・復旧・火報機能確認は未確認。個別記録[[ELV_絶縁抵抗試験時火報盤基板焼損_ID162事例]]を参照。"
---

# 絶縁抵抗試験メモの確認記録

## 確認範囲

原文に高圧絶縁抵抗試験後の残留電荷に関する説明と、測定器接続・待ち時間・接地を含む具体的な手順があることを確認した。内容の安全性・適用性を独立検証できていないため、手順や数値は本記録に転載していない。

## 未確認事項

- C-7-A30-Jの本文、版、適用範囲
- 対象回路/機器、測定器の適合要件、電気安全上の資格/役割要件
- 試験後の残留電圧確認、放電、接地、切離しに関する承認済み現行手順
- 技術・電気安全レビューおよび情報管理区分

## 関連事例: ID307

協力会社展開用リストID307は、動力回路の絶縁抵抗に関する異常報告と複数の調査/是正試行を記載するが、原因と解消結果は確定していない。ID69/83の制御回路誤結線報告とは異なる事象として扱う。測定値、現場/設備識別、端子/配線、測定・切離し・修理手順は転載しない。

## 関連事例: ID162

一次リストID162は、絶縁抵抗試験に伴う火報盤内基板焼損を報告する。試験条件、原因機構、是正内容、復旧、火報機能の独立確認は未確認。個別記録[[ELV_絶縁抵抗試験時火報盤基板焼損_ID162事例]]を参照する。試験値・電圧・対象回路・切離し/復旧手順を本記録へ追加しない。

## 利用制限

この記録は安全レビュー保留の案内であり、試験方法ではない。レビューと現行資料照合が完了するまで、原文の手順を試験・放電・接地・機器切離しの根拠に使用しない。

## 出典

- 原文: [[不具合対応【ELV】/現象（不具合対応）/絶縁抵抗試験（不具合対応）/絶縁抵抗試験（注意点）]]
- OneNote ID: `a8c15103-95f4-4d08-897a-403d412bffb5:147`
- [[ELV_AXIEZ-LINKS_BOON線誤結線_絶縁不良_ID69事例]]は絶縁不良の別事例記録であり、この資料の測定・試験後処置を裏付けるものではない。
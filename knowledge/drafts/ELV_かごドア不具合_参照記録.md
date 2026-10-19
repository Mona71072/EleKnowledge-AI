---
schema_version: 1
record_id: "catalog-elv-car-door-failures-reference"
record_version: 5
title: "かごドア不具合リンク資料の参照記録"
category: "技術メモ【ELV】２"
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
keywords: ["かごドア", "不具合", "異音"]
source_path: "技術メモ【ELV】２/ELV-一般/かご/かごドア.md"
source_filename: "かごドア.md"
onenote_id: "48423b33-c60c-4add-b7e8-73c7287c93ba:1"
related_ids: ["elv-lv5k-lv6k-clt-dimension-acceleration-case"]
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-car-door-failures-001"
    source_type: "vault_original"
    title: "かごドア"
    source_path: "技術メモ【ELV】２/ELV-一般/かご/かごドア.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["不具合共有リストの題名4件、開閉異音の見出し、埋め込み画像参照が原文にあること"]
  - source_id: "evidence-list-elv-movable-vane-cam-misalignment-359"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 可動ベーン動作カム位置ずれによる戸全閉不良（ID359）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "かご戸全閉不良と異音、可動ベーン動作カム位置ずれの確認、是正後に動作良好との報告"
      - "冠水後の扉操作を位置ずれの原因とした原リストの推測"
  - source_id: "evidence-list-elv-door-closing-rattle-200"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 戸閉時のがたつき報告（ID200）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "戸閉時のがたつき、扉構成との原因説明、ソフトウェア変更後に解消したとの原リスト記載"
structured_data:
  items:
    - item_id: "link-title-1"
      title: "可動ベーン動作カムの位置がずれることで戸が全閉しない"
      locator: "不具合共有リストのリンク題名。リンク先未閲覧"
      content_status: "title_only_unverified; separate_excel_extract_recorded"
    - item_id: "link-title-2"
      title: "CLT・OLT寸法をドア駆動基盤上で確認できる件"
      locator: "不具合共有リストのリンク題名。リンク先未閲覧"
      content_status: "title_only_unverified"
    - item_id: "link-title-3"
      title: "LV5K／LV6Kドア適用現場におけるCLT寸法の設定基準について"
      locator: "不具合共有リストのリンク題名。リンク先未閲覧"
      content_status: "title_only_unverified"
    - item_id: "link-title-4"
      title: "ドア開閉時異音発生"
      locator: "不具合共有リストのリンク題名。リンク先未閲覧"
      content_status: "title_only_unverified"
  source_notes:
    - "上記4件は原文に見える不具合共有リストの題名のみで、リンク先の案件内容・原因・対策・適用性を確認した事実ではない。認証付きURLは転載していない。"
    - "首都工・不具合情報共有リストID359の別出典を追記。可動ベーン動作カム位置ずれの確認、是正後の動作報告と、冠水後の無理な扉操作を原因とする推測を区別。カムの手動復帰/固定等の操作、現場情報は転載していない。原因・是正・機種適用は独立確認していない。"
    - "協力会社展開用Excel ID200をID359とは異なる戸閉時のがたつき事例として追記。扉構成との原因説明とソフトウェア変更後の解消報告は出典上の記載であり、独立確認していない。速度/設定値/清掃/機構調整/改造手順、現場情報は転載しない。"
    - "首都工・不具合情報共有リストID 432には題名が類似するCLT事例の提供内容があるが、原文の共有リストリンク先と同一資料・同一案件であることは確認できない。Excel出力から得た内容は [[整備済み資料/技術資料/ELV_LV5K_LV6K_CLT寸法_事例記録]] に別出典として記録した。"
    - "原文には別途「カゴドア開閉時の異音について」の見出しと埋め込み画像1点がある。画像はVault内検索で実ファイルを確認できず、内容未確認。"
---

# かごドア不具合リンク資料の参照記録

## 原文にある共有リストの題名

原文には次の4件が不具合共有リストのリンク題名として記載されている。題名を検索用に保持したもので、リンク先の記述・事実関係を確認したものではない。

- 可動ベーン動作カムの位置ずれと戸の全閉不良
- CLT・OLT寸法をドア駆動基盤上で確認できる件
- LV5K／LV6K適用現場におけるCLT寸法の設定基準
- ドア開閉時異音

原文本文には別途「カゴドア開閉時の異音について」という見出しがある。画像1点と共有リンク先は未確認であり、原因、設定基準、対策をこの記録から確定してはならない。

現象に該当する場合は現行の承認済み不具合情報と機種別保守資料を確認する。未確認のリンク情報を故障処置に使用しない。

## 共有リストID359の別出典

協力会社展開用Excel ID359は、MRLでスロー運転時に戸が全閉せず異音が続いた事例を報告する。原リストは可動ベーン動作カムの位置ずれを確認し、是正後に動作が良好になったとしている。冠水後に保守員が扉を無理に開けたことがずれの原因との説明は、原リスト上の推測であり、因果関係・復旧の継続性・機種適用は独立確認していない。

カムの手動復帰、扉の固定、運転や調査の手順は記載しない。原文リンク先と本件が同一案件かも未確認である。

## 戸閉時のがたつき報告（共有リストID200）

協力会社展開用Excel ID200は、戸閉時のがたつきと扉構成との関係を原因として挙げ、ソフトウェア変更後に解消したと報告する。これは出典上の説明であり、原因、変更の適否、解消の継続性、機種適用、アクセシビリティ要件との整合は独立確認していない。ID359の戸全閉不良とは別事例として扱う。

速度/設定値、清掃/機構調整/改造手順、現場情報は記録しない。本記録を扉の調整、ソフト変更、受入判定の根拠に使用しない。

出典: `技術メモ【ELV】２/ELV-一般/かご/かごドア.md`（OneNote ID `48423b33-c60c-4add-b7e8-73c7287c93ba:1`）。確認日: 2026-10-08。

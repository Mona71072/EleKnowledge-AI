---
schema_version: 1
record_id: "catalog-elv-maintenance-console-links-review-hold"
record_version: 3
title: "メンテコン関連情報の確認記録（情報管理保留）"
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
keywords: ["メンテコン", "情報管理", "社内限定", "アクセス制限"]
source_path: "不具合対応【ELV】/メンテコン.md"
source_filename: "メンテコン.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:99"
related_ids:
  - "list-id300-alarm-history-analysis"
  - "list-id297-scu-maintenance-tool-location"
  - "list-id248-maintenance-console-wifi-certificate"
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-maintenance-console-links-hold"
    source_type: "vault_original"
    title: "メンテコン（情報共有リスト）"
    source_path: "不具合対応【ELV】/メンテコン.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["関連情報への外部リンク、参考資料一覧、共有範囲を制限する注意があること"]
  - source_id: "evidence-list-elv-alarm-history-analysis-300"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: アラーム履歴採取について（ID300）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports: ["アラーム履歴を用いた原因解析の可能性と、データ取扱いに関する原リスト記載"]
  - source_id: "evidence-list-elv-scu-maintenance-tool-location-297"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: SCU保守ツール保存場所について（ID297）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports: ["SCU保守ツールの社内保存場所案内があるとの原リスト記載"]
  - source_id: "evidence-list-elv-maintenance-console-wifi-certificate-248"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: メンテコンのWi-Fi接続/コンピュータ証明書取得（ID248）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports: ["社内無線LAN接続とコンピュータ証明書取得に関する原リスト記載、配布端末の事前登録に関する説明"]
structured_data:
  source_notes:
    - "原文にアクセス制限付き外部リンクと、他支社協力会社へ伝えないよう求める記述がある。リンクURL、トークン、限定手順は本記録へ複写していない。"
    - "リンク先の権限、内容、現行性、共有範囲、認証情報の有効性は未確認。許可された閲覧経路と情報管理者の判断が確認できるまでリンク先を開かず、要約・展開・外部共有しない。"
    - "この記録は所在と保留状態の管理用であり、メンテコン操作手順や保守情報の代替ではない。"
    - "Excel ID300はログ取得/保存/社外解析と付随情報に関する手順を含むが、内部アドレス・保存先・ファイル形式・送付情報・操作は転載していない。提供権限/情報管理/現行性は未確認。"
    - "Excel ID297はSCU保守ツールの社内保存場所案内を含むが、ポータル経路、内部リンク、保存場所、ダウンロード手順は転載していない。ツールの利用権限/共有可否/現行性は未確認。"
    - "Excel ID248は社内無線LAN接続/コンピュータ証明書取得の説明を含む。URL、申請/証明書取得、管理者権限での操作、端末識別情報、事前登録の手順は非転載。内容/現行性/対象端末/情報管理者の承認は未確認。"
---

# メンテコン関連情報の確認記録

## 確認範囲

原文が複数の関連情報リンクと参考資料を列挙し、一部情報の共有先を制限する注意を含むことを確認した。リンク先は閲覧していない。

## 関連情報: ID300

協力会社展開用リストID300は、アラーム履歴を用いた原因解析の可能性を記載し、履歴データと発生状況に関する情報の取扱いにも触れている。具体的なログ取得/保存/送付方法、内部アドレス/パス、ファイル形式、送付情報、提供権限、データ管理要件および現行性は未確認のため転記していない。

協力会社展開用リストID297は、SCU保守ツールの社内保存場所を案内している。内部ポータル経路、リンク、保存場所、ダウンロード方法、ツールの利用権限および共有可否は未確認のため転記していない。

協力会社展開用リストID248は、メンテコン端末の社内無線LAN接続とコンピュータ証明書取得について説明し、配布端末の事前登録に言及している。接続申請、証明書取得、管理者権限での操作、端末識別情報、社内URL、登録方法は記録しない。内容・現行性・対象端末・情報管理者の承認は未確認であり、本記録を接続/証明書取得手順として使用しない。

## 利用制限・未確認事項

- リンクURL、共有トークン、社内限定手順は転載しない。
- リンク先のアクセス権、内容、改訂、現行性、社外・他支社への共有可否は未確認。
- 情報管理者が共有範囲を確認するまで、リンク先を開かず、手順化・要約・クラウド連携に使用しない。

## 出典

- 原文: [[不具合対応【ELV】/メンテコン]]
- OneNote ID: `a8c15103-95f4-4d08-897a-403d412bffb5:99`
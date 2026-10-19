---
schema_version: 1
record_id: "elv-load-test-mcb-rating-question-id391"
record_version: 1
title: "負荷試験時のMCB定格超過に関する照会（ID391）"
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
keywords:
  - "負荷試験"
  - "MCB"
  - "定格電流"
  - "時間特性"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "MCB動作特性曲線（原リスト添付）"
    locator: "添付本文未確認"
    source_path: ""
  - document_number: ""
    title: "原リスト記載のメーカー製品資料PDF"
    locator: "URL記載あり。リンク先本文・版・対象器種未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-load-test-mcb-rating-391"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 負荷試験時のMCB定格超過に関する照会（ID391）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "負荷試験時の電流がMCB定格を超えることへの質問と、遮断器の時間特性に関する出典説明"
structured_data:
  question: "負荷試験時に電流がMCB定格を超える場合があるのに、直ちにトリップしない理由についての照会。"
  source_explanation: "原リストは、過電流に対する時間遅延特性により定格超過が直ちに遮断されない場合があると説明する。説明中の数値例や一般化された時間は再掲しない。"
  independent_verification: "添付動作特性曲線および原リスト記載のメーカー資料PDFは未閲覧。対象MCBの型式・定格・設定、負荷試験条件と適用規程は未確認で、出典説明の技術的妥当性を独立確認していない。"
  limitations:
    - "本記録は照会と原リストの説明の記録であり、定格超過運転の安全性・許容可否を示すものではない。"
    - "ブレーカー選定、保護協調、負荷試験の実施・継続、合否判断に使用しない。"
    - "具体的な電流値・継続時間、遮断器型式、特性曲線、試験・設定手順は転載しない。"
---

# 負荷試験時のMCB定格超過に関する照会（ID391）

首都工・不具合情報共有リストID391は、負荷試験時の電流がMCBの定格電流を上回る場合があることについて、直ちに遮断されない理由を照会している。

原リストは、遮断器に過電流の時間特性があり、定格を一時的に超えても直ちに動作しない場合があると説明する。これは出典上の説明であり、対象ブレーカーの特性・定格・設定・劣化状態や負荷条件を確認した評価ではない。添付特性曲線および参照先メーカーPDFも未閲覧で、説明内容の独立検証は行っていない。

したがって、この記録を定格超過運転が安全または許容される根拠として扱わない。対象機器に適用する現行の承認済み資料、電気設計および所管技術者の判断で確認する。選定・保護協調・試験の具体条件や操作は含めない。
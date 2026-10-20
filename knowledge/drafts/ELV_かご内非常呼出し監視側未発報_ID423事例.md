---
schema_version: 1
record_id: "elv-emergency-intercom-call-not-reported-id423"
record_version: 1
title: "かご内非常呼出しの監視側未発報事例（ID423）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
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
  - "かご内非常呼出し"
  - "インターホン通報"
  - "遠隔監視"
  - "調査未完了"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-emergency-intercom-monitoring-423"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: かご内非常呼出しの監視側未発報（ID423）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "かご内非常釦操作時に監視側のインターホン通報が発報しなかった事象と、調査の一部が未完了との記載"
structured_data:
  equipment: "エレベーター（詳細機種・監視システム名は記録しない）"
  symptom: "原リスト記載の運転状態において、かご内非常釦を操作しても、遠隔監視側設備でインターホン通報が発報しなかったとの報告。"
  investigation:
    - "遠隔監視側でエレベーター運転状態を確認できたため、制御盤から監視システムまでの結線は良好と推定したとの記載。独立確認はない。"
    - "制御盤内の電気的確認は出典上「良好」とされるが、測定端子・電圧値は記録しない。"
    - "インターホン分岐基板周辺の信号調査は調査中と記載されている。"
  cause_assessment: "原因は未特定。通報信号のどの区間で不達となったか、監視側表示と通報先の受信状況も未確認。"
  outcome: "是正対応、通報再試験、復旧結果の記載なし。調査未完了。"
  limitations:
    - "非常通報回路の端子/コネクタ識別、電圧値、結線情報、診断・試験手順は記録しない。"
    - "現場、建物、顧客、監視システムの固有名、担当者、号機情報は記録しない。"
    - "本記録は未完了事例の参照用であり、非常呼出しの機能確認・受入判定・復旧手順ではない。"
---

# かご内非常呼出しの監視側未発報事例（ID423）

## 症状と調査状況

首都工・不具合情報共有リストID423は、原リスト記載の運転状態でかご内非常釦を操作した際、遠隔監視側設備でインターホン通報が発報しなかったと報告する。

遠隔監視側でエレベーターの運転状態を確認できたため、制御盤から監視システムまでの結線は良好と推定したとの記載がある。この推定は独立確認されていない。制御盤内の電気的確認は出典上「良好」とされるが、端子や電圧値は記録しない。インターホン分岐基板周辺の信号調査は調査中とされている。

## 原因・結果

原因、通報信号の不達箇所、通報先での受信状況は特定されていない。是正対応、通報再試験、復旧結果も記載がなく、本件は調査未完了である。

非常通報回路の端子/コネクタ、電圧、結線、診断・試験手順は本記録に含めない。非常呼出し機能の確認・受入判定・復旧には、承認済みの現行資料と所管担当による確認が必要である。
---
schema_version: 1
record_id: "elv-cm-ma-no-load-run-m1-card-damage-terminal-label-case"
record_version: 1
title: "CM-MAの空回し不能と端子表示誤貼付の事例"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "CM-MA"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "空回し不能"
  - "M1カード"
  - "端子表示誤貼付"
  - "盤表示消灯"
related_ids: []
source_path: ""
source_filename: ""
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: "ATHO07104"
    title: "不発資料（リスト記載。本文未確認）"
    locator: "参考資料欄"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-cm-ma-no-load-run-m1-card-terminal-label-053"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 空回し時にM1カード焼損の事例（ID53）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "空回し時の表示消灯とM1カード損傷所見、カード交換で改善しなかった調査経過、端子台ラベル誤貼付との原因報告、是正後の空回し良好報告"
      - "供給元による他機器損傷リスク評価があったとのリスト記載"
structured_data:
  equipment: "CM-MA"
  symptom: "空回しを試みた際に制御盤表示が点灯せず、M1カード上に浮き・脱落しかけた部品と焼損痕が見つかったとの報告。"
  error_codes: []
  cause: "リストは端子台ラベルの貼付誤りにより結線が誤っていたことを原因としている。具体的な端子・配線対応と因果関係は独立確認していない。"
  verified_actions: []
  outcome: "初期にはカード固定不良が疑われ、交換用カードを使用しても状況は改善しなかった。その後の比較調査でラベル誤貼付が見つかり、ラベル/結線の是正と一時的なカード交換後に空回し動作良好との報告がある。供給元はM1カード以外の機器損傷リスクは低いと判断したとの記載だが、損傷範囲・原因・復旧結果は独立確認していない。具体的な測定・端子・結線・交換・通電手順は記録しない。"
---

# CM-MAの空回し不能と端子表示誤貼付の事例

首都工・不具合情報共有リストID53は、CM-MAで空回しを試みた際に制御盤表示が点灯せず、M1カード上に浮き・脱落しかけた部品と焼損痕が見つかったと報告する。

## 調査経過

原文では当初、M1カード上の部品固定不良が疑われ、交換用カードを手配・使用したものの状況は改善しなかった。その後の再調査と正常設備との比較で、端子台ラベルの貼付誤りが見つかったと記録されている。具体的な端子表示、測定・結線確認の方法は転載しない。

## 原因報告と対応結果

リストは端子台ラベルの誤貼付により結線が誤っていたことを原因としている。ラベルと結線の是正、および一時的なカード交換後に空回し動作が良好となったとの報告がある。原因・因果関係・機器損傷範囲は独立確認していない。供給元はM1カード以外の機器損傷リスクが低いと判断したとの記載だが、これは原文上の評価である。

参考資料欄の不発資料番号は追跡用に残したが、資料本文・添付実体は未確認である。端子・配線の識別、絶縁抵抗/電圧測定、結線修正、カード交換、通電・空回しの手順は記録しない。本記録は事例検索用で、電気作業や安全判断の根拠ではない。
---
schema_version: 1
record_id: "elv-axiez-links-boon-grounding-misconnection-id69"
record_version: 2
title: "AXIEZ-LINKSのBOON線誤結線による制御回路絶縁不良報告（ID69）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "AXIEZ-LINKS"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "絶縁抵抗不良"
  - "誤結線"
  - "アース"
  - "接地"
  - "BOON"
  - "MELD"
related_ids:
  - "elv-insulation-resistance-test-review-hold"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-axiez-links-boon-misconnection-069"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: アース線を異なるターミナル（128番）に結線してしまい、制御回路のメガー不良（ID69）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "AXIEZ-LINKSの制御回路絶縁不良、MELDバッテリー負極側の線をアース線と誤認したとの原因報告、是正後に良好となったとの記録、および同様事象の複数回報告"
  - source_id: "evidence-list-axiez-links-boon-misconnection-083"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: アース線を異なるターミナルに結線し、制御回路の絶縁不良となった件（ID83）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "制御回路の絶縁不良報告、線の外観による用途誤認との原因説明、是正後に絶縁良好となったとの報告、および複数地域での類似事象との備考"
structured_data:
  equipment: "AXIEZ-LINKS"
  symptom: "調整時に制御回路の絶縁抵抗不良があったとの報告。ID83は測定値を約0.2 MΩと記載するが、当該事例の報告値であり判定基準ではない。ID69・83とも、MELDバッテリー負極側の線（原文表記BOON）を接地線と取り違えたとの原因説明がある。"
  error_codes: []
  cause: "原文は、MELDバッテリー負極側のBOON線が接地線に似た外観であったため、接地線と誤認して別のターミナルへ接続したことを原因とする。ID69・83は別日付の報告であり、各原因説明は独立確認していない。個別端子番号・線識別は記載しない。"
  verified_actions: []
  outcome: "ID69・83の各原リストは、誤接続の是正後に絶縁が良好となったと報告する。ID83は神奈川・関越・東京地区でも類似事象があったとするが、各案件の条件・件数・時期は未記載。ID69は誤接続状態でもMELD動作は良好だったと記載する。各報告の原因・対応・結果は独立確認していない。"
---

# AXIEZ-LINKSのBOON線誤結線による制御回路絶縁不良報告（ID69）

首都工・不具合情報共有リストID69は、共有日欄を2021-12-10（Excel値44540の換算）とするAXIEZ-LINKSの報告で、調整時に制御回路の絶縁抵抗不良があったと記録する。

原因欄は、MELDバッテリー負極側の線（原文表記BOON）が接地線に似た外観だったため、据付作業者がターミナル番号を確認せず接地線と誤認して誤結線したと説明する。線色・外観のみでは導体の用途を判断できないという事例上の注意であり、個別設備の配線確認手順を示すものではない。

## 調査・対応結果

原リストは、調査の過程で誤結線を発見して是正した結果、絶縁抵抗が良好になったと報告する。また、複数現場で同様事象に対応したとの共有があるが、各案件の条件・件数・時期は未記載。誤結線状態でもMELD動作は良好だったとの記載もある。原因・対応・結果は原文上の報告で、独立確認していない。

### ID83: 別報告

首都工・不具合情報共有リストID83は、共有日欄を2021-12-23とする別報告である。調整時に制御回路の絶縁不良があり、原リストは測定値を約0.2 MΩと記載する。この値は当該報告の記録値で、合否基準・推奨値ではない。

ID83の調査記録は、特定の回路枝を調べる中で異常箇所を絞り、MELDバッテリー負極側のBOON線が接地線に似た外観だったため、作業者が接地線と誤認していたと説明する。原リストは誤接続是正後に制御回路の絶縁が良好となったと報告する。備考は神奈川・関越・東京地区でも類似事象があったとするが、発生件数・各現場の条件・時期は示していない。これらはID83の原リスト上の説明で、ID69と同一設備・同一発生事象とは確認できず、原因・是正・結果も独立確認していない。個別の測定、端子識別、回路切離し、結線是正の手順は転載しない。

## 注意事項と関連資料

原文の制御ラインコネクタや接地線を切り離す調査手順、ターミナル番号、写真は転載しない。絶縁抵抗試験の測定・判定・回路切離し手順を示す資料ではなく、個別設備への実施根拠に使用しない。[[ELV_絶縁抵抗試験_安全レビュー保留]]は試験安全に関する別の参照記録であり、本事例の裏付けや作業指示ではない。
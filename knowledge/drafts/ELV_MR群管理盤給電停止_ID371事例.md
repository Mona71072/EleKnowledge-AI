---
schema_version: 1
record_id: "case-elv-mr-group-panel-power-disconnected-id371"
record_version: 1
title: "MR機種・群管理盤への給電停止による乗場呼び不作動事例"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type: ["MR機種"]
document_number: ""
revision: "首都工・不具合情報共有リスト記載。原資料・版は未確認"
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["群管理", "群管理盤", "給電停止", "乗場呼び", "仮設電源"]
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids:
  - "elv-group-operation-issues"
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-mr-group-panel-power-disconnected-id371"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト（Excel出力、ID371）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    locator: "リストID371（Excel出力のID欄、ワークシート行14）"
    supports:
      - "仮設電源から本設電源への切替後に乗場呼びが不作動となった症状と現地所見"
      - "群管理盤への給電停止、原因仮説、給電復旧後に復帰したとの記載"
structured_data:
  equipment: "MR機種のエレベーター群管理設備"
  symptom: "電源切替後に乗場呼びが作動しなくなったとの報告。現地ではかご内呼びと自動運転は動作し、乗場呼びのみ不作動だったと記録されている。"
  error_codes: []
  cause: "リストは、群管理盤への供給線が抜かれて給電されていなかったと記録する。作業時に線が邪魔となり他業者が外した後、戻し忘れたとの説明は推測として記載されており、独立確認されていない。"
  verified_actions: []
  outcome: "リストは群管理盤への給電復帰後に復帰を確認したと記録する。復帰確認の方法・対象範囲・継続確認は未記載で、報告結果は独立確認されていない。"
  case_conditions:
    - "リストの機種欄はMR機種。"
    - "仮設電源から本設電源へ切替後の事例として記録されている。"
    - "初報と現地確認で、乗場呼びと、かご内呼びによる運転の状態が区別されている。"
  source_notes:
    - "リストは群管理盤への供給線が外れていた状態と、線が作業の妨げとなり外されたままになったとの原因仮説を記載する。原因の独立確認はない。"
    - "給電復帰後の復帰確認はリスト上の報告。現行の電源構成・対象群管理盤・継続状態は未確認。"
    - "ブレーカー遮断、配線識別・接続・復旧などの具体的な電気作業手順は転載していない。"
    - "現場名、号機、作業者・共有者名は転記していない。添付図の実体と内容は未確認。"
---

# MR機種・群管理盤への給電停止による乗場呼び不作動事例

## 事例の要点

首都工・不具合情報共有リストID371は、仮設電源から本設電源への切替後、乗場呼びが作動しなくなったと報告している。初報では全自動運転もできないとの連絡だったが、現地確認では、かご内呼びとそれによる自動運転は可能で、乗場呼びのみ不作動と区別されている。

## 原文上の調査・原因説明

リストは、群管理盤に電源が供給されておらず、群管理盤への供給線が外れていたと記録する。線が他の電源線に挟まれて作業の妨げとなり、電源切替時に外した後戻し忘れたとの説明は、リスト上の原因推定であり独立確認されていない。

## 対応と結果

進捗欄には、群管理盤への給電を復帰させた後に運転が復帰したとの報告がある。復帰確認の方法・対象範囲・継続確認は記載されていない。

## 注意事項

本記録は事例検索用であり、電源遮断、配線、ブレーカー、結線確認や復旧の作業手順ではない。現場名・号機・作業者名は記録していない。現行の給電構成、添付図、技術レビューは未確認。

## 関連資料

- [[ELV_群管理不具合一覧]]: 群管理関連の共有事例一覧。ID371の題名記録から本事例へ接続する。

## 出典・確認状態

- 出典: 首都工・不具合情報共有リストのExcel出力、リストID371。
- 原文上の原因推定と復帰報告は独立確認されていない。現行性・対象設備への適用は未確認。
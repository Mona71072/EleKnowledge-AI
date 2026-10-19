---
schema_version: 1
record_id: "case-elv-cm-ma-group-operation-2c-2bc-id384"
record_version: 1
title: "3carで群管理運転せず、2C-2BC運転となる"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type: ["CM-MA"]
document_number: ""
revision: "Excel出力記載。元リストの改訂・現行性未確認"
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["CM-MA", "群管理", "工事使用", "2C-2BC", "乗場押しボタン"]
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: ["elv-group-operation-issues"]
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-cooperation-share-list-id384"
    source_type: "user_provided_extract"
    title: "技術情報リスト（協力会社展開用）.xlsx: 3carで群管理運転せず、2C-2BC運転となる"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "リストID384のCM-MA工事使用中における群管理運転の症状"
      - "原因/対応欄の記載が途中で終わり、進捗欄が空欄であること"
structured_data:
  equipment: "CM-MA、3台群管理（工事使用中との記載）"
  symptom: "工事使用中、3台群管理運転から2C-2BC運転となったとの報告。2か所の乗場押しボタンについて連動して点灯しないとの連絡があり、確認時は一方の押しボタンで2台、もう一方で1台のみが応答したと記載されている。"
  error_codes: []
  cause: "確定原因は記載されていない。現象欄の分類語は『接触不良』だが、原因/対応欄は『GH1基盤とGP１基盤間で』という途中の記載で終わっており、故障箇所や因果関係は判断できない。"
  verified_actions: []
  outcome: "進捗状況欄は空欄。原因/対応欄にも具体的な調査結果、実施対応、対応後の動作確認結果は記載されていない。"
---

# 3carで群管理運転せず、2C-2BC運転となる

## 事例の概要

技術情報リスト（協力会社展開用）には、CM-MAの工事使用中に3台群管理運転ができず、2C-2BC運転となった事例が記載されている。乗場に設置された2か所の押しボタンが連動して点灯しないとの連絡があり、確認時は一方で2台、もう一方で1台のみが応答したと報告されている。重要度欄は「中」、エラー表示欄は「未確認」。

## 原因・対応の記載状態

現象欄の分類語に「接触不良」とあるが、確定原因とは確認できない。「不具合原因+対応内容」欄は「GH1基盤とGP１基盤間で」で記載が途切れており、その後の原因説明や対応内容は読み取れない。進捗状況欄も空欄であるため、調査・対応の実施状況や復旧結果は不明。

## 出典・未確認事項

- 出典: `技術情報リスト（協力会社展開用）.xlsx`、リストID384。共有日はExcel日付値45686（2025-01-29）。
- 現場名・共有者名は検索に不要な識別情報のため、本記録へ転記していない。
- 元リストの完全性・改訂、原因記載の続き、進捗、対応後結果、技術的な因果関係、他物件への適用性は未確認。
- 本記録は事例の検索・確認用であり、群管理設定、基板・接点の診断、配線、運転・復旧手順を示さない。

---
schema_version: 1
record_id: "elv-vfglb-car-top-station-order-mismatch-id104"
record_version: 1
title: "VFGLBかご上ステーションの誤搬入とオーダー照合に関する報告（ID104）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGLB"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "かご上ステーション"
  - "誤搬入"
  - "オーダー照合"
  - "VFGLB"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-18-D50.1-J"
    title: "VFGLBドア基板資料"
    locator: "原リスト記載: P5、2.1.2.(2)。本文未閲覧、適用範囲未確認。"
    source_path: ""
  - document_number: ""
    title: "label.xlsx"
    locator: "原リストが添付として参照。実ファイル未確認。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-case-id104"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID104"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト未照合"
    accessed_at: "2026-10-09"
    supports:
      - "VFGLBかご上ステーションの誤搬入報告、原文が挙げるオーダー情報と基板ラベル位置の照合先、および仕様に含まれるはずと原文が述べる装備が欠けていたとの記載"
structured_data:
  equipment: "VFGLB かご上ステーション"
  symptom: "他現場向けのかご上ステーションが誤って搬入された事例があったと原リストは報告する。また、仕様に含まれているはずと原文が述べるインターフォン基板とITV中継フィルタがなかったとの記載がある。"
  cause: "誤搬入の原因は原リストに記載なし。装備の欠落が仕様上の不備に該当するかは、正式仕様を確認しておらず未確認。"
  verified_actions: []
  outcome: "対応後の結果記載なし。"
---

# VFGLBかご上ステーションの誤搬入とオーダー照合に関する報告（ID104）

## 概要

首都工・不具合情報共有リストID104は、他現場向けのかご上ステーションが誤って搬入された事例を記録する。共有日は2022-05-26。原リストの現象欄は「豆知識」、エラー表示欄は「未確認」で、不具合内容・進捗状況欄に記載はない。

## 原リストの記載

原リストは、オーダー情報と基板に貼付されたラベルの位置を確認する資料を挙げている。ただし、詳細は参考資料と添付に委ねられており、具体的な確認方法やラベル内容はこの抜粋から確認できないため再構成していない。

備考には、仕様に含まれるはずと原文が述べるインターフォン基板とITV中継フィルタがなかったとの記載がある。この期待仕様が当該機の正式仕様と一致するか、欠落が確認済みの事実かは独立確認していない。

## 対応・結果

原リストはオーダー確認を行ったと記載するが、具体的な照合内容、誤搬入後の処置、再発防止策および対応後の結果は記載していない。実施内容や結果を補っていない。

## 関連資料

- 参考資料としてC-18-D50.1-JのP5、2.1.2.(2)項が記載されている。本文、改訂、適用範囲は未確認。
- `label.xlsx` が添付として記載されているが、ワークスペース内で実ファイルを確認できていない。添付内容は未確認で、`attachment_paths`には登録していない。

## 出典・確認状態

- 出典: Excel出力のID104行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- 参考資料本文、添付、当該機の正式オーダー/仕様、誤搬入の原因と処置、現行適用、技術レビューは未確認。
- 本記録はレビュー中・未公開であり、機器照合や搬入判定の手順・基準を示すものではない。

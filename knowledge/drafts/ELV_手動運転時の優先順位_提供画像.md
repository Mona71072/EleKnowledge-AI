---
schema_version: 1
record_id: "elv-manual-operation-priority-user-image"
record_version: 3
title: "手動運転時の優先順位（VFGLF/VFGLB・提供画像）"
category: "技術メモ【ELV】２"
record_type: "knowhow"
product: "エレベーター"
model_type:
  - "VFGLF"
  - "VFGLB"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "手動運転"
  - "HAND"
  - "運転優先順位"
  - "VFGLF"
  - "VFGLB"
source_path: "技術メモ【ELV】２/ELV-一般/手動運転優先順位.md"
source_filename: "手動運転優先順位.md"
onenote_id: "d6d3fbd5-7e56-4b5c-be71-b28c4b3303f2:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-7-C3900-J"
    title: "VFGLF電気システム据付調整資料"
    locator: "P7"
    source_path: ""
  - document_number: "C-7-C3300.1-J"
    title: "VFGLB電気システム据付調整資料"
    locator: "P7"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-manual-priority-user-image-20261009"
    source_type: "user_provided_extract"
    title: "ユーザー提供画像: VFGLF/VFGLB手動運転優先順位"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "画像に記載されたHAND時の優先順位と、かご上HAND中に他位置から運転できない旨の注意"
  - source_id: "evidence-elv-manual-priority-vault-page-20261009"
    source_type: "vault_original"
    title: "手動運転優先順位（OneNote由来ページ）"
    source_path: "技術メモ【ELV】２/ELV-一般/手動運転優先順位.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "VFGLF/VFGLB各資料へのリンク表記、資料番号およびP7の参照位置"
structured_data:
  knowledge_items:
    - model: "VFGLF"
    - topic: "VFGLFのHANDモード時の運転優先順位"
      statement: "優先順位は、かご上 > ピット > かご内 > 乗場と画像に記載されている。"
      conditions:
        - "VFGLF制御"
        - "HANDモード"
      exceptions: []
      rationale: "かご上でHAND中は、ピット・かご内・乗場では運転できないため注意する旨が画像に記載されている。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-elv-manual-priority-user-image-20261009"
    - model: "VFGLB"
    - topic: "VFGLBのHANDモード時の運転優先順位"
      statement: "優先順位は、かご上 > かご内 = 乗場（ピット内）と画像に記載されている。"
      conditions:
        - "VFGLB制御"
        - "HANDモード"
      exceptions: []
      rationale: "かご上でHAND中は、かご内および乗場（ピット内）では運転できないため注意する旨が画像に記載されている。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-elv-manual-priority-user-image-20261009"
  source_notes:
    - "優先順位・注意文はユーザー提供画像に記載された情報。原ページの対応する埋め込み画像ファイル実体との照合は未実施。"
    - "原ページのリンク表記から資料番号とP7を記録。リンク先PDFの本文、版、適用範囲、現行性は未確認。"
    - "画像の記載を現行の操作許可、実施手順、安全判断、他機種へ一般化した仕様として扱わない。"
---

# 手動運転時の優先順位（VFGLF/VFGLB・提供画像）

  ## 要点

  手動運転（HAND）時の運転優先順位は、提供画像上ではVFGLFとVFGLBで異なる。VFGLFは「かご上 > ピット > かご内 > 乗場」、VFGLBは「かご上 > かご内 = 乗場（ピット内）」と示される。どちらも、かご上でHAND中は他の記載位置から運転できない旨の注意が添えられている。

  ## 機種別の記載

| 制御方式 | HAND時の優先順位表示 | 画像記載の注意 |
| --- | --- | --- |
| VFGLF | かご上 > ピット > かご内 > 乗場 | かご上でHAND中は、ピット・かご内・乗場では運転できない旨。 |
| VFGLB | かご上 > かご内 = 乗場（ピット内） | かご上でHAND中は、かご内および乗場（ピット内）では運転できない旨。 |

画像上の参照表記は、VFGLFが「C-7-C3900-J.pdf（VFGLF調整資料P7）」、VFGLBが「C-7-C3300.1-J.pdf（VFGLB調整資料P7）」。原ページ[[技術メモ【ELV】２/ELV-一般/手動運転優先順位]]にも同じ資料番号とP7のリンク表記がある。

## 読み取り範囲と注意

これは提供画像に記載された機種別の違いを回答するための記録であり、運転操作の許可や手順を示すものではない。原ページの画像ファイル実体と提供画像の照合、参照PDFの本文・改訂・適用範囲・現行性は未確認である。実機操作や安全判断には、適用確認済みの承認資料を用いる。

## 出典

- 優先順位・注意文: ユーザー提供画像（2026-10-09受領）。原ページ内の同一添付画像との実体照合は未実施。
- 資料番号・P7リンク表記: [[技術メモ【ELV】２/ELV-一般/手動運転優先順位]]。
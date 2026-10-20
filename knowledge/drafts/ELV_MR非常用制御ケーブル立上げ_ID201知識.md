---
schema_version: 1
record_id: "knowhow-elv-mr-emergency-control-cable-riser-id201"
record_version: 1
title: "MR非常用エレベーターの制御ケーブル立上げ条件（ID201）"
category: "技術メモ【ELV】２"
record_type: "knowhow"
product: "エレベーター"
model_type:
  - "MR機種"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "制御ケーブル"
  - "立上げ位置"
  - "ケーブルプロテクター"
  - "ケーブルクリップ"
  - "PAD"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "catalog-elv-cable-hanger-reference"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "IN-EL-08-111"
    title: "制御ケーブル立上げ位置の参照施工要領（原題未確認）"
    locator: "立上げ位置に関する指示としてID201に記載。本文・版未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-mr-emergency-control-cable-riser-201"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: かご側制御ケーブル立上げとプロテクター干渉（ID201）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "ケーブルプロテクターとクリップを同時取付できなかった事象とID201の条件"
      - "IN-EL-08-111からの基本指示と条件付きのPAD側立上げ指示"
      - "PADプレートと制御ケーブルの35mm以上との設計記載"
structured_data:
  knowledge_items:
    - topic: "非常用MR機種での制御ケーブル立上げ位置と取付干渉"
      statement: "ID201は、IN-EL-08-111由来として記載する基本の立上げ指示と異なり、特定条件ではPAD取付側へ立ち上げる指示があると報告する。該当事例ではケーブルプロテクターとケーブルクリップを同時に取り付けられなかった。"
      conditions:
        - "非常用で、かご上JBを適用する条件。"
        - "TR 100m以上で、ケーブルプロテクターを適用する条件。"
        - "ID201は、該当設計でPADプレートと制御ケーブルが35mm以上離れると記載する。"
      exceptions: []
      rationale: "ID201は上記条件下でPAD取付側へ立ち上げる指示があると説明している。基本指示との関係および取付干渉の解消方法は原資料に記載された範囲を超えて推定しない。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-elv-mr-emergency-control-cable-riser-201"
  specifications:
    - name: "PADプレートと制御ケーブルの離隔（設計記載）"
      value: "35以上"
      unit: "mm"
      condition: "ID201が述べる特定条件下の設計。現行設計値・許容値としては未確認。"
    - name: "TR"
      value: "100以上"
      unit: "m"
      condition: "非常用・かご上JB適用時にケーブルプロテクターを適用するとするID201の条件。現行適用未確認。"
  source_notes:
    - "IN-EL-08-111の本文・版、ID201が引用する基本指示の正確な内容、MR機種への適用範囲は未確認。"
    - "同じIN-EL-08-111をVFGH施工要領書として扱う別の参照記録がある。文書同一性・MR条件への適用性・記載差は未確認であり、VFGHの条件を本件に流用しない。"
    - "本記録は出典記載の整理であり、現行の据付図・承認済み施工指示を代替しない。"
---

# MR非常用エレベーターの制御ケーブル立上げ条件（ID201）

## 事象

首都工・不具合情報共有リストID201は、かご側制御ケーブルの立上げ時、ケーブルプロテクターとケーブルクリップを同時に取り付けられなかった事象を報告する。現場名・号機などの識別情報は記録しない。

## 条件付きの立上げ位置に関する記載

ID201は、IN-EL-08-111由来としてPAD取付位置と反対側へ立ち上げる基本指示を引用する一方、次の条件ではPAD取付側へ立ち上げる指示があると説明する。

- 非常用で、かご上JBを適用
- TR 100m以上で、ケーブルプロテクターを適用

同資料は該当設計でPADプレートと制御ケーブルが35mm以上離れると記載する。これらはID201に記載された条件・値であり、現行設計値、離隔基準、全MR機種への適用として確認されたものではない。

## 参照資料と適用上の注意

参照番号はIN-EL-08-111。正式な資料名、本文、版および基本指示との関係は未確認。同番号は既存の別記録でVFGH施工要領書として扱われているが、MR機種への適用や同一文書性は確認できていない。現行の機種別据付図・承認済み施工資料で条件を照合するまで、配置、離隔、部材取付の判断に使用しない。

出典: 首都工・不具合情報共有リスト.xlsx、ID201。補助ブック行198は作業上の照合位置。
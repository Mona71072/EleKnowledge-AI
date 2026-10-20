---
schema_version: 1
record_id: "knowhow-elv-acoe-remote-stop-fan-runon"
record_version: 1
title: "ACO-E遠方発停で圧縮機停止後も送風機が継続する記録"
category: "技術メモ【ELV】１"
record_type: "knowhow"
product: "エレベーター"
model_type: []
document_number: ""
revision: "首都工・不具合情報共有リスト記載。取扱説明書原本・適用版未確認"
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["ACO-E", "遠方発停", "圧縮機", "送風機", "停止遅延"]
source_path: ""
source_filename: "技術情報リスト.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links:
  - "https://www.mitsubishi-elevator.net/GIS/eisetujp/mebs/torisetsu/torisetsu_etc.html"
document_references:
  - document_number: "D-C-845.1"
    title: "C資料（正式題名要確認）"
    locator: "Excel参考資料欄 P.5。原本未閲覧"
    source_path: ""
  - document_number: "C-30-G5.3"
    title: "D資料（正式題名要確認）"
    locator: "Excel参考資料欄 P.13。原本未閲覧"
    source_path: ""
  - document_number: "YX201B879"
    title: "資料種別要確認"
    locator: "Excel参考資料欄に記載。内容未確認"
    source_path: ""
  - document_number: ""
    title: "エアコン取扱説明書"
    locator: "リスト記載のP.12。原本未受領・未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-acoe-remote-stop-id377"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: クーラー付き運転（ACO-E）の遠方発停の動作について"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    locator: "リストID 377（Excel出力のID欄）。資料番号ではない"
    supports: ["遠方発停時の圧縮機/送風機の停止タイミング、記載資料間の差、現地観察の記録"]
structured_data:
  knowledge_items:
    - topic: "ACO-E遠方発停では圧縮機と送風機の停止時点が異なるとの記録"
      statement: "リスト記載では、停止条件を満たしACOEライン（遠方発信信号）がブレイクされると、圧縮機は即時停止し、送風機は25分継続後に停止する。停止条件を満たしてから25分後に同じ動作を現地で確認したと報告されている。"
      conditions: ["首都工・不具合情報共有リスト記載の一事例。内容照合にはリストからのExcel出力を使用。", "取扱説明書の記載および現地観察として報告された内容", "対象機種欄は『全エレ機種』だが、適用機種・エアコン型式は独立確認していない"]
      exceptions: ["25分はリスト記載値であり、全機種/全エアコンに適用される現行設定時間とは確認されていない。", "送風機が回転しない場合にDC48V信号未入力の可能性があるとの注記は、可能性の記録であり診断手順ではない。"]
      rationale: "圧縮機停止後に送風機だけが継続する状態を、直ちに停止不良と判断せず、承認済み仕様と照合するため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-acoe-remote-stop-id377"]
    - topic: "C/D資料と取扱説明書の記載差を区別する"
      statement: "Excelは、参照されたC資料/D資料には25分後に運転停止する記載が見当たらず、記載明確化を提案した後、2025-02-12にメーカー取扱説明書ページへエアコン取扱説明書が追加されたと記録している。追加された資料の内容・版・現在の掲載状態は未確認。"
      conditions: ["いずれもExcelの記録内容", "D-C-845.1 P.5、C-30-G5.3 P.13、YX201B879、取扱説明書P.12の本文未閲覧"]
      exceptions: ["資料番号・ページ・追加日の記載は独立確認していない。", "外部リンクはExcel備考に記載された案内先で、取扱説明書本体への直接リンクとは確認していない。"]
      rationale: "資料間の記載差と、メーカー取扱説明書への追加履歴を分けて残し、未確認の資料内容を確定仕様として扱わないため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-acoe-remote-stop-id377"]
  source_notes:
    - "現象・25分・DC48V・資料差・2025-02-12の追記日はリスト記載。参照元Excelは当該リストからの出力。取扱説明書原本、C/D資料、掲載URLは独立閲覧していない。"
    - "本記録は停止挙動の照合メモであり、電源/信号測定、停止試験、設定変更の手順ではない。現行仕様は対象機器の承認済み資料で確認する。"
    - "リストID 377は出典追跡用識別子であり、資料番号ではない。現場名・号機・共有者等は転記していない。"
---

# ACO-E遠方発停で圧縮機停止後も送風機が継続する記録

## 動作記録

技術情報リストには、停止条件を満たして遠方発信信号がブレイクされた後、圧縮機は即時停止し、送風機は25分継続してから停止するとの取扱説明書記載がある。停止条件成立後、25分経過して同じ動作を現地で確認したとも記録されている。これらはExcelに記録された一事例であり、対象機器への現在の適用を保証するものではない。

同表には、送風機が回転しない場合に遠方発信信号（DC48V）が入力されていない可能性があるとの注記がある。可能性の提示に留まり、測定・診断・操作方法は示さない。

## 資料間の記載差

Excelは、D-C-845.1 P.5およびC-30-G5.3 P.13には25分後に停止する記載がないと報告している。記載の明確化を提案し、2025-02-12にメーカー取扱説明書ページへエアコン取扱説明書が追加されたと記録されている。参照資料本文、改訂、追加履歴、現在の掲載状態は未確認である。

本記録は現行の運転仕様や試験手順ではない。圧縮機/送風機の停止時間、信号条件、機種適用は、実設備に対応する承認済み資料で照合する。

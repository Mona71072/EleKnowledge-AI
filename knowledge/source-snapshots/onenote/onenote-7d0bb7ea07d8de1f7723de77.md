---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "d0aa7329-f26d-4ee4-ab5e-a993c0987919:1"
knowledge_domain: "unknown"
organizational_scope: "unknown"
classification: "unknown"
review_status: "unreviewed"
publication_status: "not_published"
cloud_approval: "not_reviewed"
source_links_resolved: false
attachments_included: false
---

> Source snapshot for EleKnowledge-side organization. Not curated, not verified, and not RAG-eligible.

## OneNote content
スローFMS（手動階高書込み）

Slow FMS (Manual Floor Height Writing)

(1)作業内容

Work Procedure

①カゴを終端階走行（最下階→最上階）へ走行させ、自動運転を行えるようにする。

Run the car on a terminal floor run (bottom floor to top floor) to enable automatic operation.

(2)目的

Purpose

①制御盤内P1基板上のRAMに最下階～最上階までの距離及び各階間の距離を書込む。

Write the distance from the bottom floor to the top floor and the distance between each floor to the RAM on the P1 board in the control panel.

②最下階と最上階の位置は終点スイッチと着床プレート、各階の距離は着床プレートを基準に巻上機回転センサーにて検出する。

The positions of the bottom and top floors are detected by terminal limit switches and landing plates, and the distance of each floor is detected by the hoist machine rotation sensor based on the landing plates.

③スローFMSが完了していない状態で自動運転にすると、終端階走行を繰り返すので注意。

Be careful: if automatic operation is initiated before slow FMS is complete, the car will repeatedly perform terminal floor runs.

（セレクタずれ検出時と同じ状態となる。カゴ位置が検出できないのため。）

(This is the same state as when a selector misalignment is detected, as the car position cannot be detected.)

④FMSが完了しない理由としては、基本的に着床プレート、終点スイッチが原因であることが多い。

FMS failure is often caused by the landing plates or terminal limit switches.\n
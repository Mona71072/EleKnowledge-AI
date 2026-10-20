---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "8b4e3532-1808-42d6-b17a-34098987f000:1"
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
秤設定（BL+カゴ上作業者一人）

Weighing Setting (BL + One Worker on Car Top)

(1)作業内容

Work Procedure

①カゴ内に最大積載の50％のオモリを積み込み、傾斜センサーの角度設定を行う。

Load weights equivalent to 50% of the maximum capacity into the car and set the tilt sensor angle.

(2)目的

Purpose

①傾斜センサーはカゴ内負荷BL（50％）で垂直（目盛の０）になるように設定を行い、カゴ内負荷を正確に検出できるようにする。（変化量の基準点を設定する）

Set the tilt sensor to be vertical (scale reading 0) at 50% car load (BL) to accurately detect the car's internal load. (Set the reference point for change.)

②作業の際は、カゴ上に作業員が一名搭乗しているため、メモリを＋3または＋4に設定する。カゴ積載及びロープ本数によって目盛値の設定が異なる。

During this work, one worker is on the car top, so set the scale reading to +3 or +4. The scale reading setting varies depending on the car load and the number of ropes.

33.2026/6/9

2026/6/9

34.NL・BL値書込み・確認

NL・BL Value Writing and Confirmation

(1)作業内容

Work Procedure

①カゴ内NL、また、カゴ内に50%分のオモリを積み込み、終端階走行を行い各値をP１基板へ書込む。書込み後、50%L秤（BLWT）とNL秤（NLWT）の秤値を確認する。

With the car at NL and with 50% load, perform terminal floor runs and write each value to the P1 board. After writing, confirm the weighing values for 50% load (BLWT) and no load (NLWT).

(2)目的

Purpose

①実際にNLとBLオモリを積み込んだ状態で秤値を書込みカゴ内の積載量を正確に検出できるようにする。

Write the weighing values with actual NL and BL weights loaded to accurately detect the car's internal load.

②カゴ内積載量を正確に検出可能となるため、可変速運転はこの作業実施後に有効化される。

Since the car's internal load can be accurately detected, variable speed operation is enabled after this procedure.

可変速運転…乗車率に応じて運行速度が変化する仕様。

Variable speed operation: A specification where the operating speed changes according to the occupancy rate.

(3)NL/BLの秤値を書込むことで自動的にFL/OLの秤値を算出する。

Writing the NL/BL weighing values automatically calculates the FL/OL weighing values.

(4)秤値は、往路と復路（最上階と最下階）の値を足して２で割った値をフラッシュメモリに書き込む。

The weighing value is written to flash memory as the average of the values from the outbound and return runs (top floor and bottom floor).

(5)秤値 カゴ内負荷

Weighing Value Car Load\n
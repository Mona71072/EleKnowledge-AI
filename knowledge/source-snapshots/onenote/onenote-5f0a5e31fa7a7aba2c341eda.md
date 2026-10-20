---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "fe060413-3902-44b9-9834-55874202e951:69"
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
目的：**着床位置、ロープアンバランスの書き込み**

【技術情報リスト】

[カムの据付不良によりFMS完了しない件]([URL omitted pending approved OneNote link resolution])

**・階高書込み**

カゴを終端階から反対の終端階まで運転する。モータのエンコーダーパルス数を累積し、カゴの移動量を求め、各階の着床プレートの位置を着床位置としてRAMに書き込む（位置スイッチも）。エンコーダーの原理についてはエンコーダー磁極合わせの項目で述べる。これにより高速運転が可能となる。また、シンクロ位置、アドバンス位置の検出を行う。

シンクロ位置はBOT階を基準とし実際にいる階をシンクロ階と呼ぶ。階床表示信号に用いられる。アドバンス位置はシンクロ位置より一定距離先行させ残距離演算の開始点を求めたもの。その位置にある階床をアドバンス階と呼び、停止検出する為の信号として用いられる。

| [OneNote attachment reference omitted; attachment not copied] |  |
| --- | --- |

**・ケーブル・ロープアンバランス書込み**

カウンターバランスによりカゴとカウンタの釣合いを取るがカゴとカウンタの位置関係によって昇降行程や制御ケーブル芯数の影響を受け、ケーブルやロープの重さによりアンバランスが生じる。コンペンチェーンやウィスパーフレックス等のコンペン装置により補正をかけるが、アンバランスは生じてしまう。これによりエレベーター起動時にブレーキを開く事により起動ショックが生じる。ケーブル・ロープアンバランスが生じる状況を図2に示す。

起動ショックを防ぐために秤値、エンコーダーより階高値とケーブル・ロープアンバランス重量をRAMに書込む。秤装置の原理は秤装置の調整の項目で述べる。

[OneNote attachment reference omitted; attachment not copied]\n
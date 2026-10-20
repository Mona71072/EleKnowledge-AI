---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:159"
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
【事象】

調整屋が負荷試験実施の際、NL時にて可変速の設計速度値(品目表記載)にならない不具合が発生。

DN運転時は設計速度値が測定されたのに対し、UP運転時は基準値より大きい値が測定された。

【原因】

前提条件：LINKsはバランスウェイト積込時やUP運転時に秤値がズレる可能性があるため、NL・BL時の秤書込は下降時に書込む仕様となっている

仮説：高速のUP・DNにおいて秤値に差が生じるのではないか？

DN運転にて測定したNL書込時と、最下階からのUP運転にて測定した秤値に差が生じており(ロープアンバランスの書込み、秤装置の勝手、傾斜センサーのばらつき等？)、秤が負荷を誤認識したことで正常に可変速機能が動作しなかったと推測される。　（FMS実施目的・機能一覧：OneNote reference (unresolved in snapshot): FMS）

【対策】

スローFMS(UP方向で実施)に付随している秤のオフセット機能によって、最下階からのUP運転（NL）で負荷検出されている秤値をNLとしての適正な秤値へと再設定可能になる。（最上階からのDN運転時に負荷がマイナスになるのではないかとの疑問もある。。。。）

→スローFMS後はUP/DNで無負荷時で設計速度値となり動作良好

[OneNote attachment reference omitted; attachment not copied]

【備考】

以下の「手動優先モード」使用にてかご中間位置にて速度を計測可能

[OneNote attachment reference omitted; attachment not copied]\n
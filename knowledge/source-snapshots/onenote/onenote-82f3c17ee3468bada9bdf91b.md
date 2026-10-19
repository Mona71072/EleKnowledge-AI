---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "cff9f835-784e-47d5-99c8-57e32e5506f5:122"
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
資料

| OneNote reference (unresolved in snapshot): C-8-S140.1-J-A.pdf | OneNote reference (unresolved in snapshot): C-60-631-VF26.1-J-H (1).pdf |
| --- | --- |
| エレ | エス |

〇概要

LAN監視システムでは、エレベーター・エスカレーターの運転状態（エスカの場合はUP,DN別であり）や故障などを監視しており、異常状態であれば警報が鳴り駅員がすぐに把握できるようなモニター監視装置である。

従来（LonWorks）では端末とパラレル接続されていたため、全ての項目の確認が必要であったが

LAN監視システムではシリアル通信のため基本的な運転状態の確認と代表として2つの安全装置動作を確認する。

〇確認内容

・エレベーター

[OneNote attachment reference omitted; attachment not copied]

・エスカレーター

[OneNote attachment reference omitted; attachment not copied]

〇LAN監視システム詳細図

| [OneNote attachment reference omitted; attachment not copied] | [OneNote attachment reference omitted; attachment not copied] |
| --- | --- |
| 状態監視 | 警報一覧 |

| [OneNote attachment reference omitted; attachment not copied] | [OneNote attachment reference omitted; attachment not copied] |
| --- | --- |
| 分割ライブ映像（エスカレーター） | 分割ライブ映像（エレベーター） |

〇注意点

・LANケーブルはJECT盤差し込むこと。

※エレベーターの場合、JECT盤と一緒に取り付けてあるI/O基板にLANケーブルの差込口があるため注意。

・各号機とJECT盤はIPアドレスで紐づいているため、LAN監視システムで号機のテレコがあったときはJECT盤右下に

記載あるIPアドレスを確認し正しいかJREM（メカトロ）へ確認すること。

・安全装置遮断時の状態表示は下記の通り。

エレベーター：重故障

エスカレーター：軽故障

・S/W側でLAN監視システムの信号有効/無効があり、接続状態は良いが通信異常発生する場合はS/W不良の可能性ありた

め、稲電へ確認すること。

・LAN監視システムと接続された状態で作業する際は、事前にLAN監視システムで検修状態（警報が鳴らない）にしても

らうようJREM（メカトロ）へ連絡すること。\n
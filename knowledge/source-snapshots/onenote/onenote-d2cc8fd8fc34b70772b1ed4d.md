---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "839f5e88-68d9-4fc8-a200-72a5c73c3ac6:1"
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
〇混雑階待機動作（CFS）​

⇒乗車する乗客により一時 的に混雑する場合にかごを集中し，混雑緩和を図る。 ​

※前半と後半で動作がある。​

【条件】

前半サービス（CFS-Z）：降車混雑階で降車負荷(降りた人)が20%以上を検出した際に、出発時のかご負荷が70%以上検出した階へ優先的​に配車し待機する。​

後半サービス（CFS-K）：乗車混雑階で乗車負荷（乗った人）が20%以上を検出した際に、乗車混雑階へ配車し待機する。​

※降車混雑階と乗車混雑階を群管理モニターで設定可能。

**〇混雑階待機動作（****CFS****）前半****​**

【確認方法】​

手順①：MITEMAS上で手動またはケジュールを設定する。​

※MITEMAS無の場合は、群管理モニタでスケジュール設定を行う。

※手動の場合は、条件を満たすと動作に移行する。

[OneNote attachment reference omitted; attachment not copied]

手順②：群管理盤モニタに接続し、混雑階待機動作を強制選択且つ降車混雑階を設定する。​

※自動の場合はスケジュール設定しておかないと強制選択しても動作に移行しないので注意！

[OneNote attachment reference omitted; attachment not copied]

手順③：群管理モニターにて、降車混雑階とは別の階に全自動で移動させ、到着したら仮想負荷を70%以上に設定する。​

手順④：群管理モニターの状態表示にてカゴを操作し、設定した降車混雑階に到着後に仮想負荷を0%に設定する。​

[OneNote attachment reference omitted; attachment not copied]

手順⑤：群管理モニターの状態表示内にある、運転パターンのCFSZが点灯していることを確認する。​併せて、設定した混雑階に待機することも確認する。

[OneNote attachment reference omitted; attachment not copied]

**〇混雑階待機動作（****CFS****）後半****​**

【確認方法​】

手順①：MITEMAS上で手動またはスケジュールを設定する。​

[OneNote attachment reference omitted; attachment not copied]

※MITEMAS無の場合は、群管理モニタでスケジュール設定を行う。

※手動の場合は、条件を満たすと動作に移行する。

手順②：群管理盤モニタに接続し、混雑階待機動作を強制選択且つ乗車混雑階を設定する。​

[OneNote attachment reference omitted; attachment not copied]

※自動の場合はスケジュール設定しておかないと強制選択しても動作に移行しないので注意！

手順③：群管理モニターにて、乗車混雑階に全自動で移動させ、到着したら仮想負荷を20%以上に設定する。​

[OneNote attachment reference omitted; attachment not copied]

手順④：群管理モニターの状態表示内にある、運転パターンのCFSKが点灯していることを確認する。​併せて、設定した混雑階に待機することも確認する。

[OneNote attachment reference omitted; attachment not copied]\n
---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:117"
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
・Links

[AXIEZ-LINKs安全回路について 1.pptx]([URL omitted pending approved OneNote link resolution])

→29回路がどのように構成されているのかわからない時

[R1_Z11コネクタ一覧表.xlsx]([URL omitted pending approved OneNote link resolution])

→コネクタがどの機器に繋がっているのか確認時

[制御盤短絡表（VFGLB-JB、VFGLF、VFGH）.xlsx]([URL omitted pending approved OneNote link resolution])

→不具合箇所特定のため短絡するとき

[VFGLF技術資料.pdf]([URL omitted pending approved OneNote link resolution]) ([3201.pdf]([URL omitted pending approved OneNote link resolution]))

→安全回路の構成の参考に

・VFGH

29が遮断された場合は、自動もスローも動くことはない。かご呼びも作れず戸閉ボタンを押しても閉まってこない。また、遮煙ありの場合は安全回路遮断することで、自動ではゆっくり戸閉してくる。

※安全回路から41DGの電圧が回ってくるため、29が切れている場合は41DGが点灯しない。

**・安全回路遮断**

安全回路遮断時に、遮煙適用と適用無しで動作が異なる。

〇遮煙あり⇒安全回路遮断することで、戸閉し動作不能となる。

〇遮煙なし⇒安全回路遮断することで、戸開き待機のまま動作不能となる。

※ドラフト対策で遮煙が適用されていた場合は、遮煙なしの動作となる。監視盤側の動作に関しては、差異はない。

【異常灯】

安全回路を落とすことで、出発不能を検出して点灯する。

⇨かご内がスローだと異常灯が点灯しないので注意してください。

[OneNote attachment reference omitted; attachment not copied]\n
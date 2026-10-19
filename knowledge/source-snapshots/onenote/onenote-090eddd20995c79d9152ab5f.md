---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "25a2acc3-4a3e-4512-89ed-15d8a0a4a3f3:1"
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
参考不発： [URL omitted pending approved OneNote link resolution]

①Ville-feuille側から指令を出しても、タイムアウトとなりエレロボ連動しない

⇒原因：エレベーター側パラメータ設定ミス（）

⇒処置：群管理、制御盤のパラメータ改造し動作確認

【群管理】

|  |  | データ名 | データ内容 |  |  | 備考 |
| --- | --- | --- | --- | --- | --- | --- |
| アドレス | データ長 | （ＬＡＢＥＬ） | 変更後 ← 変更前 |  |  |  |
| D170 | バイト | UM_DOAS_GATE_CAR | 01 | ← | 11 | DRC01 /*H*/ |
| DD58 | ワード | UM_ELSCA_CRTBL | 26AD | ← | FFFF | STB7F /*A*/ |

【制御盤】

| アドレス設定 |  | データー名 | データ変更内容 |  |  | 備考 | (設計メモ) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| セグメント | アドレス |  | 変更後 | ← | 変更前 |  | 変数名 /*コード*/ |
| 1009 | 4598 | UM_ELSCA_CRTBL | 26 | ← | FF |  | ASTB7F /*A*/ |
| 1009 | 4599 | UM_ELSCA_CRTBL | AD | ← | FF |  | ASTB7F /*A*/ |
| 1009 | 4256 | KM_ELSCA_ROBOT_NO | 7F | ← | 00 |  | CSCRBN /*A*/ |

②エレロボ連携し始めるが、ロボット乗車後の目的階かご呼びが登録されない。

⇒原因：かご内CRスイッチが無効（平常）側になっていた

⇒注意事項として取説に記載するよう営設に申し入れ

③ロボットがエレベーターを呼び出し

→ロボットが乗場呼びを登録するが、エレベーターからロボット専用号機が配車されない。

⇒原因：ロボットが乗場呼びを要求した際の呼び属性が間違っていた

（本来は呼び属性"04"（ロボット）だが、呼び属性"00"(一般)で要求されていた）\n
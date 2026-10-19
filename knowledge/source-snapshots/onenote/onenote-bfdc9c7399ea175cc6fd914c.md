---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "057444fa-309a-4170-bbef-998c0015e5f7:128"
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
| 時計(制御盤・群管理盤)が設定されている事 |
| --- |
| ﾐﾆｺﾝﾀｸﾀに防塵ｼｰﾙ(目張り)が貼り付けられている事。（JRE駅物件のみ） |
| UCMP制動距離・秤データを制御盤ラベルに記載している事。 |
| ﾜﾝﾀｯﾁｸﾘｯﾌﾟの挿入穴に電線が2本以上挿入されていない事。（電線の剥き代が10～12mmで、軽く引っ張っても抜けない事） |

【LINKs限定】

| 制御盤養生シートの剥ぎ忘れ、IPU組立ファン動作に問題が無いこと ※特に制御盤背面の養生に注意すること |
| --- |
| 制御盤側UVW、トランス、ﾜﾝﾀｯﾁｸﾘｯﾌﾟの結線が良好なこと （ひげが出ておらず、引っ張っても抜けないこと） |
| 制御盤の蓋で電線が傷ついていないこと |
| 巻上機-制御盤間の分離配線が良好なこと |
| 【制御盤後ろ配置の時】制御盤取付腕に固定するケーブルが圧迫された状態で固定されていないこと。 |

**・時計(制御盤・群管理盤)が設定されている事**

[OneNote attachment reference omitted; attachment not copied]

**・****制御盤養生シートの剥ぎ忘れ、IPU組立ファン動作に問題が無いこと　※特に制御盤背面の養生に注意すること**

[OneNote attachment reference omitted; attachment not copied]

|  |  |
| --- | --- |
|  |  |

**・制御盤側UVW、トランス、****ﾜﾝﾀｯﾁｸﾘｯﾌﾟ****の結線が良好なこと（ひげが出ておらず、引っ張っても抜けないこと）**

| [OneNote attachment reference omitted; attachment not copied] | [OneNote attachment reference omitted; attachment not copied] | [OneNote attachment reference omitted; attachment not copied] |
| --- | --- | --- |
| 引抜試験を実施し適切に結線されていることを確認すること。 | ワンタッチクリップの結線が良好なこと ワンタッチクリップがしっかりはまっていることを確認する。1つのクリップで2線以上結線しないこと。 備考：BGMの仕様がなかったとしてもワンタッチクリップは手配される。 | ひげが出ておらず、引っ張っても抜けないこと すべての線がはまっているかを軽く引っ張って確認する。 ひげが出ている場合は一度線を抜いて刺しなおす (芯線がはみ出していないか、銅線部分。) |

**・制御盤の蓋で電線が傷ついていないこと**

**・巻上機-制御盤間の分離配線が良好なこと**

| [OneNote attachment reference omitted; attachment not copied] | [OneNote attachment reference omitted; attachment not copied] | [OneNote attachment reference omitted; attachment not copied] |
| --- | --- | --- |
| 制御盤基板の蓋を閉める際は、線を元の位置に戻し、挟み込みがないか確認してから蓋を閉めてください。 | 制御盤本体のふたを閉める際は、飛び出ている線がないか確認してください。 | 制御盤から巻上機へ向かう線は大電流が流れるため、他の線にノイズが乗らないよう、他の線から離して単独で配線してください。 |

**・****WGHO****設定値の確認****(SET1****＝****4****→****SW1****▽****)**

**※制御盤裏に記載された調整データと一致していること。**

【参考資料】

[TI-1449 エレベーターの管理秤（WGHO）の戻し忘れ不具合に係る件.pdf]([URL omitted pending approved OneNote link resolution])

WGHOの説明

WGHO（29W：乗り過ぎ検出動作点）の設定値を変更することで、カゴの満員ブザーの鳴動有無や、カゴの運転可否を決定できます。

**【その他】**

| [OneNote attachment reference omitted; attachment not copied] |
| --- |
| 電源遮断後も、主回路の電解コンデンサにはしばらくの間高電圧が残留し、放電されません。 そのため、DCV表示が消灯していてもインバーター回路に触れる前に、必ずテスターで直流電圧を測定し、十分に放電されていることを確認してから作業を行ってください。 緑色でマーキングされているビスは工場でトルク管理されているため基本的に触らない。 ※群管理有(ACB有)の場合MCBを遮断しても共通回路が生きているので不用意に触らないこと。 |\n
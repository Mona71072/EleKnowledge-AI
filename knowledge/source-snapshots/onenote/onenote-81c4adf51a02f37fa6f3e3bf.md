---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "c3cbdf09-d13b-4aa5-9561-35eec9fc56a6:153"
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
[OneNote attachment reference omitted; attachment not copied]

<u>ETS</u><u>とは</u>

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

資料資料の保存先

[超高速エレの調整について.pptx]([URL omitted pending approved OneNote link resolution])/%25E8%25AA%25B2%25E5%2586%2585%25E5%258B%2589%25E5%25BC%25B7%25E4%25BC%259A/20%25E5%25B9%25B4%25E5%25BA%25A6/10%25E6%259C%2588%25E5%25BA%25A6_%25E8%25B6%2585%25E9%25AB%2598%25E9%2580%259F%25E3%2582%25A8%25E3%2583%25AC%25E8%25AA%25BF%25E6%2595%25B4/%25E8%25B6%2585%25E9%25AB%2598%25E9%2580%259F%25E3%2582%25A8%25E3%2583%25AC%25E3%2581%25AE%25E8%25AA%25BF%25E6%2595%25B4%25E3%2581%25AB%25E3%2581%25A4%25E3%2581%2584%25E3%2581%25A6.pptx?d=w4b9df369f84b4707a70114ced2c04c87&csf=1&web=1&e=WLHQ5q)

| [OneNote attachment reference omitted; attachment not copied] |  |  |
| --- | --- | --- |

<u>動作点確認方法</u>（調整作業員によるETS調整が終わってから確認）

※基準内に設定されていないと、バッファ許容速度を超えてしまったり、速度が下がらずにE-STOPしてしまう恐れがあります。

OneNote reference (unresolved in snapshot): ETS動作点確認用_.xlsx

[OneNote attachment reference omitted; attachment not copied]

**手順①：カゴ内に****BL****のテストウェイトを積む**。

※BLのみ実施する（。NLやOLでカゴが引っ張られるのを最小限に抑えるためです。）

**手順②：対象の号機にメンテコンを繋げ、昇降機メニューの「メモリ表示」を立ち上げる。**

**手順③：以下アドレスを入力し、自動で停止した際の最下階と最上階での位置（表示する値は現在の最下階からの距離を示す）それぞれを下記****excel****に記入する。**

※メンテコンは以下アドレス表示で接続したままとする。

[OneNote attachment reference omitted; attachment not copied]

※メンテコンで表示される値は16進数のため、右記excelに記入することで10進数に自動で変換される。

※最上階/下階の位置は16進数で8ケタで表現される。上記の各アドレスで2ケタずつ保存されている。

質問：シンクロ位置はなんですか？

⇒メンテコンの画像つけて別途記載します。

[OneNote attachment reference omitted; attachment not copied]

※4つのアドレスから調べた8ケタの数値（最上階/下階の位置）を上記オレンジ枠に記載する。

※HEX：16進数、DEC：10進数であり、excelでは数式で自動変換している。

**手順④：****ETS****スイッチカム取付図と品目表を確認し、各段（最大で****3****段）の動作点基準値を右記****excel****に記入する。**

[OneNote attachment reference omitted; attachment not copied]

※各動作点は最下階/最上階からの距離を表している。

[OneNote attachment reference omitted; attachment not copied]

※品目表に記載してある値を黒枠に1/2/3段目とそれぞれ記載してください。

**手順⑤：****ETS****を動作させるために、上部または下部の****ETS****動作点から離れた位置（接点が外れる方向）に移動してください。**

**位置は、メンテコンで確認しながら「手順③で確認した****DEC****値（****10****進数）」ー「手順④で確認した基準値」の値を****HEX****値（****16****進数）に変換した値**

**を過ぎた箇所で停止させる。**

※離れすぎると、測定時はスロー速4m/minで確認することで時間が掛かるため注意のこと

※離れすぎると、測定時はスロー速4m/minで確認するため時間が掛かるため注意のこと

**手順⑥：移動したら、****P1****基板の****MON1/0****⇒****9/C****で値を****5****⇒****1****に変更し、スロー速を****20****⇒****4m/min****に変更してください。**

**また、****ETS****基板（****KCA-1011****）のロータリーを下記のように設定し、****ETS-1****～３の各段を測定してくださ****い。****各段測定前には必ず****CONT****遮断し****ETS****基板の電源を落とすこと****。**

※ETS基板は基板制御盤下部にある縦に取り付けられている基板です。

※CPUリセットではETS基板がリセットされないため、必ず各台制御盤内の

サーキットプロテクタ「CONT」遮断によりETS基板をリセットする。

※スロー速4m/minに変更する理由として、各段測定時の停止する際E-STOPのため制動距離を少なくしたい。※電源リセットすると昇降機メニューが落ちてしまうため、再度メモリ表示を立ち上げ手順③のアドレスを入力すること。

[OneNote attachment reference omitted; attachment not copied]

例：一段目を確認の際は、ESPDを0、EGOVを0に設定。

※上記のグラフは、ETS基板内にあるロータリーESPDとEGOVの設定表です。

**手順⑦：スロー速****4m/min****でスロー運転し（上部側の確認なら****UP****、下部側の確認なら****DN****）、停止したら、メンテコンの値（現在の位置）を****excel****に入力する。**

[OneNote attachment reference omitted; attachment not copied]

※メンテコンで表示される値は16進数のため、右記excelに記入することで10進数に自動で変換される。

[OneNote attachment reference omitted; attachment not copied]

※E-STOPした後の現在のかご位置の値（メンテコン上のHEX値の8ケタ）を青枠に1/2/3段目とそれぞれ記載してください。

**手順⑧：自動計算された値が基準値との差±****100mm****以内に収まっているか確認する。**

※数式によって、最上階からの各段のETP動作点と最上階/下階からのかご位置の差が計算される。

[OneNote attachment reference omitted; attachment not copied]

**手順⑨：未確認箇所へ移動し、手順①または⑤から繰り返す。**

※スロー速20m/min且つETS基板のロータリーを戻さないと（工場設定値）自動走行できないため、必ず復帰のこと。

**手順⑩：確認終了後、調整必要な箇所があれば調整作業員に伝え、手直ししてもらう。**

※手直し後に再度測定し、基準内に収まっていることを確認する。

**<u>総点確認</u>**

**・****ETS****スイッチローラ芯～レール芯を****ETS****カム取付図に記載ある基準内であるか測定すること。※図****1****参照**

[OneNote attachment reference omitted; attachment not copied]

図１

**・中間階へ移動し、****ETS****スイッチ****BOX****内でスイッチ内部カムと動作ボタンが接触していないこと。※図****2****参照**

[OneNote attachment reference omitted; attachment not copied]

図２

**・****ETS****スイッチローラーとカム取付腕の隙間が****12****＋****10mm****となっていることを確認すること。※図****3****参照**

[OneNote attachment reference omitted; attachment not copied]

図３

**・****ETS****スイッチローラー取付ボルトとケーブル等の隙間が****10mm****以上あること。※図****4****参照**

[OneNote attachment reference omitted; attachment not copied]

図4

ローラー取付ボルト

昇

降

路

カ

ゴ

部のローラー取付ボルトと干渉物（ケーブルなど）がないこと、干渉物があっても10mm以上隙間があること

[OneNote attachment reference omitted; attachment not copied]\n
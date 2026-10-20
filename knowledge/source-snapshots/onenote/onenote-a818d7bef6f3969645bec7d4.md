---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "6ff3e3ec-2cc8-48be-9c76-165a90c390ba:1"
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

【不具合事例】

[NSHR時にタッチレス機能で解除できない件]([URL omitted pending approved OneNote link resolution])

[NS一時解除時のボタン点滅設定について]([URL omitted pending approved OneNote link resolution])

[乗場CR/３９３９認証セキュリティの制御処理不具合]([URL omitted pending approved OneNote link resolution])

[乗場テンキーを入力しても、NSの一時解除ができない件]([URL omitted pending approved OneNote link resolution])

[E-CAN通信不良によるNS動作しない件（+α＜群管理盤エラー見かた＞）]([URL omitted pending approved OneNote link resolution])

### ExcelリストID315の照合メモ

協力会社展開用リストでは、AXIEZ-LINKSの2022年2月生産以降、NS一時解除時のボタン点滅動作が変更されたとの説明がある。顧客要望時に条件付きで変更可能との記載もあるが、適用条件・承認根拠・現行仕様は未確認。参照資料の内容も未確認のため、具体的な設定方法や条件は記載しない。本メモを設定・セキュリティ機能の変更手順として使用しない。

【注意事項】

＜全階床乗場サービス切離し時＞

全階床に乗場NSが効いた場合は、カゴは追い出し状態となり主階床に移動する。

基本仕様では下記パラメーターが有効となっており、主階床の乗場押釦で戸開できるようになっている。

※あくまでも戸開できる仕様なので、全階床乗場NSで主階床にカゴが到着していない場合は、主階床の乗場押釦は機能しない。

[OneNote attachment reference omitted; attachment not copied]

＜ワンショット＞

接点がオフになってから5秒保持する。

ワンショット1秒（CR特記仕様書）＋保持5秒

→接点が出てから6秒後にオフになる。（6秒間一時解除になる。）

※0.1秒以上じゃないとエレが認識しない。パルスが入ったタイミングから一時解除が行われてパルスが切れてから5秒間保持するのが標準仕様。

※連続信号とワンショットの違いは保持するかしないか。

→ワンショットで受け取る場合、電圧がOFF→ONになったタイミングから保持時間分だけ解除される？

どこかで確認したいです。

＜一次解除＞

基本的に複数回解除するカード

＜ロータリー設定＞

・乗場インジのRSWのFW=1⇨その階床のみに影響を及ぼす使用時に選択（NSなど）、FW=0⇨全階床に影響を及ぼす使用時に設定（HOSなど）

・NSありの場合乗場インジをFL1=8にしないと休止動作になったりする場合がある。

※電気品目599にロータリーSW設定図が指定されているため確認する事。

＜サービス階切離し機能-自動選択（NS-T）＞

・NS-Tは時間設定しないとセキュリティーがかからない。

※タイマー設定は下記の資料を参考にP1のRWSで確認してください。

[NS-T RSW設定方法（改訂版）.pptx]([URL omitted pending approved OneNote link resolution])

[OneNote attachment reference omitted; attachment not copied]

※各階強制停止運転（EFS-T）もRSWで変更可能

※MFP, VIP, SCS. FFS, NS, RCS. ACO-T, MES, GOS, EFS. HOS. BSO.SPARE1, SPARE2. SPもRSWで変更可能

※予約パラメータのみRSWで変更できる。仕様変更のパラメータはRSWで変更できないため、メンテコンでの変更が必要です。

例.EFS-TのRSWでの設定について。下表のパラメータ名称:KL_EFS,アドレス:1009 02E8の場合、

アドレス値02E8をMON1/0＝C/Eで入力後、設定値をMON1/0＝C/Fで01hから02hに変更しようとすると数字右下のﾄﾞｯﾄ表示が出ず、変更できない。

ﾀｲﾏｰ予約設定は各アドレス値をMON1/0＝C/Eで入力後、MON1/0＝C/Fで変更できる。

[OneNote attachment reference omitted; attachment not copied]

**＜**任意階サービス切り離し（NS-CB ）＞

【切り離しスイッチ無効/運転設定】

手動運転で、サービス切り離しスイッチを設定に投入してボタンを選択する。点灯した階が切り離される。

（NSを動作させると、乗場表示は消灯し、乗場報知も動作を止める。また、休止灯があれば点灯する。）

※マルチカーの場合、サービス階切り離し階の設定と無効SWはバンク毎に有効となる。

※NS-CBにて休止階が不停止階になっているとRCS動作に移行しない。

※基本は乗場カゴ共にNSだが、パラーメーター設定でどちらかのみ不可にすることができる。

※M系は基本仕様

[カードリーダー勉強会_200529.pptx]([URL omitted pending approved OneNote link resolution])

OneNote reference (unresolved in snapshot): カードリーダー勉強会_200529.pptx.pdf

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]\n
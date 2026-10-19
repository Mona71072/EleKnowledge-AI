---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "fd06b4cf-59cf-44a2-a824-70f2855121cc:1"
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
パワポリンク：

[03.現場まとめ会資料]([URL omitted pending approved OneNote link resolution])

①Bバンクゲート表示器画面が異なっている

・ゲート１，２：矢印表示

⇒原因：#11号機RVMケーブル（制御盤～乗場増設電源BOX）電線短絡

⇒処置：RVMケーブル再手配・配線、配線後表示良好（黒画面バックライト表示）

・ゲート３：未点灯

⇒原因：ゲートブレーカーが落ちていて１００V給電されていなかった

⇒処置：ゲート屋にブレーカー上げてもらい表示良好

②Dバンクゲート２と３で配線がテレコ（昇降路乗場増設電源BOX～ゲート表示器）

⇒処置：電気設計に連絡し、ソフト改造を実施した。動作良好。

③全バンクカード認証しても号機が割り当てられるない

1.エレナビ通信異常が出力し続ける

⇒入退側のELSGW通信異常は、NW業者側でマルチキャストorブロードキャストの通信設定を是正して通信異常は復旧した。

※マルチキャストアドレスはIP：239.0.0.1~3のため、NW業者はマルチキャスト(ASM)で設定。

2.エレナビ通信異常は解消し、通信はしている（pingのやり取り良好）が、

カード認証しても群管理盤への指令が飛んでこない。

⇒原因：IGMP IP Snooping設定がON？

⇒処置：KDDI側統合ネットワーク設定にて、IGMP IP SnoopingをOFF設定に変更

↓IoTGWの資料

[OneNote attachment reference omitted; attachment not copied]

(2)IOTGWのLAN側ネットワーク内で使用するHUBの設定にマルチキャストIPの通信制御(通常いGMPSnoopingと呼ばれる)機能がある場合には制御を無効にする必要があります。特に、お客様のネットワークを使用する場合にはIOTGWのLANにつながるELSGWなどとのネットワーク経路にある、すべてのHUBで同様に制御を無効にしていただく必要があります。

3.カード認証した際、最初の一度or6分ほど間隔を置いてからしか群管理盤へ指令が飛んでこない

⇒原因：IGMP Snooping設定はOFFだがネットワークの階層を跨いでいたことが原因？

⇒処置：KDDI側でネットワーク設定を変更

④ゲート表示がテレコ、または表示されないゲートがある。

A ゲート1→2,2→1,3→なし

B ゲート1→2,2→1,3→3

C ゲート1→2,2→1,3→3

D ゲート1→1,2→2,3→3

⇒テレコ原因：乗場増設電源ボックスのロータリー設定とJBのゲート結線がマッチしていなかった

⇒処置：RSWを再設定

⇒ゲート表示なし原因：乗場増設電源BOX取り込みパラメータが間違っていた

⇒処置：GCパラメータ書き換え

⑥入退側のELSGW通信異常は、NW業者側でマルチキャストorブロードキャストの通信設定を是正して通信異常は復旧した。

※マルチキャストアドレスはIP：239.0.0.1~3のため、NW業者はマルチキャスト(ASM)で設定。

⇒BM側設計打合せ不足

⑦エレナビ特記仕様書のIDC番号に重複があったため、重複しないよう是正した。

※本件ではゲート用IDCが６台、エレカット用IDCが１１台の計１７台であったが、

001~017のユニークな番号が当初割り当てられていなかった。

⇒エレナビ特記仕様書の確認不足

⑧ELSGW～統合NW間のLAN成端をBM側で実施した。

※本来はBM側の施工区分ではありません。

⇒昇降機側図面では電気工事区分、電気工事側の認識では各社で施工となっていた。

LANケーブル成端作業は昇降機側で施工する場合施工業者が限られ高額な施工費もかかる。（簡単なものだったら工技で施工可能だがパッチ工事もやる場合施工不可）

⇒現地施工区分についての設計時打ち合わせ不足

⑨ELSGW側の通信要件をELV側でNW業者に指示を出していなかった。

※BM側の設計が接続ポートの払出し、通信要件の提示まで実施しています。

本来はELV側設計の所掌であると認識しています。

⇒現地環境についての確認・打ち合わせ不足

以下は今回役立ったツールです。

・Wireshark：PCでパケットキャプチャを取得するツール。パケットが正しく発信、受信されているか確認が可能。

・リピータHUB：複数のポートに同じパケットが流れるHUB。２台あると良い。

・パケットキャプチャ取得のタイミング：エレナビ対象のCRでカード認証する前から認証後３０分程度。

※IGMP IP Snooping設定が有効の場合、２４０秒程度後にパケットが発信される可能性があるため。

※下記（１）と（２）が同時で取得できるとなおよい。

・パケットキャプチャを取得するH/Wの位置

（１）ゲート用IDC　ー　リピータHUB　ー　統合NW

｜

PC(Wireshark)

（２）ELSGW　ー　リピータHUB　ー　統合NW

｜

PC(Wireshark)\n
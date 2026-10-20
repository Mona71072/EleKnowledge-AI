---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "898cd3ba-ffc1-4d64-baa0-b4a3399133ba:1"
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
参考までに、Puttyにてエラーログ採取した際にC資料（C-7-C3421.1-J）から読み取れる範囲のエラーログの見方を記載します。簡単なエラーだったら現地解決できます。

稲電やBMと状況確認する際に材料となります。

①トラブルシュートマニュアルに則てログ採取した際に<u>ERRLOG</u><u>に情報が記載されている。</u>

[OneNote attachment reference omitted; attachment not copied]

②ERRLOGに情報記載されている場合、モジュールID・エラーログコードが③の表(表5-2)に記載あるか確認。

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

③エラーログコード一覧に該当する場合、S-8-K4.1-J 添付資 料 1 の該当箇所とセキュリティ連動 DOAS\[エレ・ナビ\]特記仕様書を参照し、

該当パケットにて正しい値が設 定されているか確認する。

[OneNote attachment reference omitted; attachment not copied]

④下記の場合、モジュールID：06、エラーログコード：13⇒端末番号不正となる。

[OneNote attachment reference omitted; attachment not copied]

⑤通信データはS-8-K4.1-J 添付資料1より、

[OneNote attachment reference omitted; attachment not copied]

1730　⇒　識別子（固定）

0014　⇒　14バイトのデータ

01　⇒　宛先機器がELSGW（ACS⇒ELSGWの通信）

02　⇒　02バンクへの通信

22　⇒　送信元の機器種別番号（エレナビ特記仕様書で確認）

7f　⇒　16進数で127（送信元機器番号）

00 00 00 00　⇒　00×4で固定

01　⇒　エレベーター制御情報（単階床）

12　⇒　データ長12バイト

26ad　⇒　端末番号9901（16進数）

01　⇒　乗場照合

01　⇒　乗場呼び

00　⇒　乗場釦列指定なし

00　⇒　予備

0006　⇒　ビル階6階で乗車

※残りはCOMLOGで確認

[OneNote attachment reference omitted; attachment not copied]

（エレナビロボット連携特記仕様書）

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]\n
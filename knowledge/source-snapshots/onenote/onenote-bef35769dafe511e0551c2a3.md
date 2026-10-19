---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "c6652278-5012-4ec1-b580-4c9055a4472a:1"
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
①電気屋所持図面と稲電所持図面で割り当て表示器の配線が異なる

→営業設計がそれぞれに図面送付する際、別の図面を送付していた。

機械室にて配線を振替え対応。図面も現地に合わせて改定

[OneNote attachment reference omitted; attachment not copied]

②客先接点でカゴ内NSをかけた際、HOP（乗場操作盤）で切り離し階も呼び登録できる。

（監視盤SWでエレナビ無効時のみ）

→エレナビ無効設定時にはこの動作になるとの電気設計回答。（標準動作）

この状況はまずいので群管理SW書換にて対応

③カードを照合した際にHOPの表示が変化しない。

→本現場には各バンクHOPが二つ付いている。

この二つの接続先号機がテレコであり、基板設定とアンマッチであったため

動作していなかった。

配線を修正し解決。

※不具合じゃないけど気になった系

①エレナビ無効時、表示は「カードを使用して登録するかご利用階を入力してください」

しかし、エレナビ無効状態ではカードを利用しての行先階登録はできない。

→稲電回答はこれが正規動作との回答

以下稲電電気設計回答

________________________________________________________________________________

エレナビ無効時は乗場釦を操作する運用であり乗場操作盤は使用しません。

乗場操作盤はエレナビOFF時に機能をOFFする動作を実現できないためエレナビ有効時と

同様に使用できる状態で設置されますが、運用上操作しないものと認識しております。

上記理由につき乗場操作盤としてはON、OFFで動作の切り替えを行わないため

表示としては標準動作となります。

_________________________________________________________________________________

上記動作を営業設計に共有しこのままでよいか確認、基本的にエレナビ無効にしない

運用のためこのまま

②HOP★ボタンについて

★ボタンを押すと４階（エントランス階が登録される）しかし、本現場HOPの設置は４階のみ

意味のないボタンになっている。

保守や現地で客先要望により登録階床を変更できるのか？

→変更不可とのこと

（今回操作盤が標準使用のため、意味のない★（主階床）と－（マイナス※地下階用）がついている。）

[OneNote attachment reference omitted; attachment not copied]\n
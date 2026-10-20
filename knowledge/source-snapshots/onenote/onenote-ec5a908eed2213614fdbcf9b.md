---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "b137030d-994c-4d06-972b-6d44a8793623:1"
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
【設計資料】

・MELD(停電時自動着床装置）適用上の制約条件について（[S-1-B37.101-J.pdf]([URL omitted pending approved OneNote link resolution])）

【技術情報リスト】

[遮煙の大臣認定がある場合は火災管制運転とMELD（または戸閉保証用バッテリー盤）が必須！！]([URL omitted pending approved OneNote link resolution])

[AXIEZ-LINKsのBPSスイッチ適用について]([URL omitted pending approved OneNote link resolution])

[バッテリー電圧が低く、MELD動作に移行せず閉じ込めになってしまう。]([URL omitted pending approved OneNote link resolution])

[MELD の繋ぎ込み時、CP遮断をせずコンダクタが焼損した件]([URL omitted pending approved OneNote link resolution])

[コネクタの差し忘れにて、客先ブレーカー遮断時にMELDが実動作しない件]([URL omitted pending approved OneNote link resolution])

[MELDなしの場合の受電盤にあるバックアップバッテリーは何に使う？]([URL omitted pending approved OneNote link resolution])

[MELDバッテリーの誤結線により、IPU基盤内M1カードが焼けた]([URL omitted pending approved OneNote link resolution])

概要

停電により停止したエレベーターを、バッテリー電源を使用し、かごを最寄階まで走行させて乗客を救出する。

※救出を優先とする運転のため、サービスカット階でも最寄階停止することがある｡

機能

・三段設定の地震感知器付の場合【標準】

→手動運転以外で、「高」地震感知器が動作しておらず、停電状態が約6 秒間継続すると選択する。

※かご負荷が50％以上であればDOWN方向、50％未満であればUP 方向とする。なお、バックアップとしてかごが所定時間経過しても走行しない場合は起動方向を反転させる（この動作は一回のみ行なう）。

解除

・三段設定の地震感知器付の場合【標準】

以下のいずれかが成立すると解除する。

①MELD 運転状態にて約3 分間ドアゾーン外停止を継続すると解除する。

②MELD 運転状態にて約70 秒間ドアゾーン内停止を継続すると解除する。\n
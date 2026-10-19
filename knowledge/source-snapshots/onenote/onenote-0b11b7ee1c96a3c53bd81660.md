---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "52e6ca63-ff89-4aa2-96d6-ad5a49ff4e91:1"
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
**【参考資料】**

﷟HYPERLINK "[URL omitted pending approved OneNote link resolution]

﷟HYPERLINK "[URL omitted pending approved OneNote link resolution]

﷟HYPERLINK "[URL omitted pending approved OneNote link resolution])3．ソフトウェア構成】

**【各種位置スイッチ】**

**・****UOT****/****DOT**

終点スイッチ

※行き過ぎ制限スイッチUL/DLを超えて走行させないための最終スイッチ

**・****UL/DL**

行き過ぎ制限スイッチ

※最上階や最下階レベルを超えて走行させないためのスイッチ

**・****UHS/****DHS****（****LINKs:US****L****/PSL（****USE:****S/W）****）**

※かご頂部やピットの作業者を守るためのスイッチ

カゴ上安全距離用スイッチ：UHS

底部安全距離確保スイッチ：DHS

頂部空間リミットスイッチ：USL

ピット空間リミットスイッチ：PSL

**・****CWL****（****LINKs****のみ）**

下降制限スイッチ：CWL

**ピット床面～****CWT****下端の隙間を****1.8****m****確保**

速度と昇降路レイアウトによりUSL.USRとスイッチが共用となる場合がある。

※保守合理化S/W搭載時はCWLで一旦停止し、運転釦再押下でULまでブザー鳴動しながら4m/minで運転可能

※開発部門が出している技術資料にて、全現場共通で「**CWT下枠下面**」からピットまでが1800mm以上確保するように設計されている。

**・終点スイッチ：****USR****/DSR****、****1USD/1DSD**

TSDパターン発生用に終点スイッチが動作する毎に、その動作点に残距離をプリセットしながら停止するまで現在位置カウンタの変化量を加算することで残距離を演算する。

※TSDパターン：起動から着床までのTSDパターンを発生し、終端階においてはTSD残距離に従ったパターンを発生する。

[OneNote attachment reference omitted; attachment not copied]

**・基準位置センサー：****UP2/DN2****、****UP1****/DN1**

電子化終端階強制減速装置（SETS装置）に使用される。（高速機種のETSの考え方を低速機種に拡張適用）

SETSは調速機のエンコーダー及び基準位置センサにてかごを連続的に検出、CPUにてかご位置に応じた加速度（OS）検出パターンを演算し加速度検出レベルを下げることにより、昇降路上下部のスペース縮小を実現している。

※終点スイッチ（1USD/1DSD）とSETS基準位置スイッチの共有化をしている。

[OneNote attachment reference omitted; attachment not copied]\n
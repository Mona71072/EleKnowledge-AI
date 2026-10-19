# テーマカード本文テンプレ（AI探索用）

frontmatter は [CONTRACT.md](../CONTRACT.md)。本文は次の順・見出しを **固定** する（Wave1/2 以降同じ）。

1. **使う場面・対象条件** — **machine_room（MRL/MR）**・**guide_systems**・**door_families / door_types**・**制御**・**機種略称**（[APPLICABILITY-TAXONOMY.md](../registry/APPLICABILITY-TAXONOMY.md)）・Lists `Model` 欄との違い・いつ開くか
2. **症状・現象** — 箇条書き（検索ヒット用）
3. **ソース要約** — Lists / OneNote を分けて事実のみ（伏せ字は「保留」と明記）。OneNote が長文なら **「OneNote 詳細」** 小見出しで構造化。索引ページのみの場合は **同页の別タイトル一覧** を載せ、リンク先未取得と明記
4. **統合した回答・ノウハウ** — 上記を統合した短文〜段落（Markdown 単独で答えられる範囲）
5. **調査・確認手順** — 番号付き。Lists の progress があればその順
6. **関連事例と条件の違い** — 表
7. **KB確認に基づく追記** — `content_reviewed` 後のみ中身を書く
8. **正式資料・元情報** — Lists / OneNote / KB / 法令 RAG（該当時）の表
9. **未確認事項**

`symptoms` には §2 の語を frontmatter にも重ねる。

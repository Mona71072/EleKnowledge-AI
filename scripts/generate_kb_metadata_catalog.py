#!/usr/bin/env python3
"""KB メタデータカタログ (docs/kb-metadata-catalog-2026-08-26.md) を S3 実測から再生成する。

使い方:
    1. データソースバケットからメタデータを全件ダウンロード:
       aws s3 cp s3://ragknowledgebasestackinst-datasourcebucket9fa93e04-ybbhm1efhyzb/docs/documents <local-dir> \
           --recursive --exclude "*" --include "*.metadata.json" --profile datautl-bple-mebs
    2. python scripts/generate_kb_metadata_catalog.py <local-dir>

出力は S3 の `.metadata.json` と一対一（TSV 由来の description 列は実メタデータに存在しないため出力しない）。
索引欠落ファイル (UNINDEXED) は 2026-08-26 実測 (docs/verification-2026-08-26-kb-vqv-metadata.md §6,
issue #53) に基づく。所有側対応・再 Sync 後に確認のうえ更新すること。
"""
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "kb-metadata-catalog-2026-08-26.md"

# 2026-08-26 実測: KB 索引 (VQV81CNYU4 / KHPV3CNKOU) に取り込まれていない = 検索不能
UNINDEXED = {
    "documents/Qシート/Q-3663.pdf", "documents/Qシート/Q-3665.pdf",
    "documents/Qシート/Q-3667.pdf", "documents/Qシート/Q-3670.pdf",
    "documents/Qシート/Q-3671.pdf", "documents/Qシート/Q-3672.pdf",
    "documents/Qシート/Q-3675.pdf", "documents/Qシート/Q-3678.pdf",
    "documents/Qシート/Q-3683.pdf", "documents/Qシート/Q-3687.pdf",
    "documents/Qシート/Q-3689B.pdf", "documents/Qシート/Q-3699.pdf",
    "documents/W資料/WIG-27--D.pdf",
    "documents/据付ノート/IN-EL-08-94/追加分/IN-EL-08-94-01-2.pdf",
    "documents/据付ノート/IN-EL-12-104/IN-EL-12-104-01-1.pdf",
    "documents/据付ノート/IN-EL-12-104/IN-EL-12-104-01-2.pdf",
    "documents/据付ノート/IN-EL-12-104/IN-EL-12-104-01-3.pdf",
    "documents/据付ノート/IN-EL-12-105/IN-EL-12-105-01.pdf",
    "documents/現場代理人業務マニュアル/GM-01-03-A.pdf",
    "documents/現場代理人業務マニュアル/GM-01-29-A.pdf",
}
COMMON = {"", "*", "general"}


def elements(raw):
    els = []
    for e in (raw if isinstance(raw, list) else [raw]):
        els += [s.strip() for s in str(e).split(",") if s.strip()]
    return els


def main(src_dir):
    docs = []
    for p in sorted(Path(src_dir).rglob("*.metadata.json")):
        a = json.loads(p.read_text(encoding="utf-8"))["metadataAttributes"]
        docs.append(a)
    if not docs:
        sys.exit(f"no metadata files under {src_dir}")

    cats = Counter(a["category"] for a in docs)
    mt_list = sum(1 for a in docs if isinstance(a.get("model_type"), list))
    mt_str = len(docs) - mt_list
    comma = [a for a in docs if isinstance(a.get("model_type"), str) and "," in a["model_type"]]
    mt_vals = Counter(e for a in docs for e in elements(a.get("model_type")))
    common_n = sum(1 for a in docs
                   if (els := elements(a.get("model_type"))) is not None
                   and (not els or all(e in COMMON for e in els)))
    unindexed_found = sum(1 for a in docs if a["file_path"] in UNINDEXED)

    L = []
    w = L.append
    w("# KB 資料メタデータ一覧")
    w("")
    w("> **状態:** S3 実測ベース（正本）")
    w("> **ソース:** `s3://ragknowledgebasestackinst-datasourcebucket9fa93e04-ybbhm1efhyzb/docs/documents/` の全 `.metadata.json`")
    w(f"> **取得日:** 2026-08-26 ／ **生成日:** {date.today().isoformat()} ／ **件数:** {len(docs):,} 件")
    w("> **再生成:** `python scripts/generate_kb_metadata_catalog.py <metadata-dir>`（手動編集しない）")
    w(">")
    w("> 旧版（〜2026-08-26）はユーザー提供 TSV ベース（3,492 件）だったが、実バケットと 253 件乖離していたため")
    w("> 実測へ置換した。TSV 由来の `description` 列は実メタデータに存在しないため本版にはない")
    w("> （旧 TSV は `docs/kb-metadata-catalog.tsv` に残置）。実測の経緯・検証詳細は")
    w("> [verification-2026-08-26-kb-vqv-metadata.md](./verification-2026-08-26-kb-vqv-metadata.md) を参照。")
    w("")
    w("---")
    w("")
    w("## 1. スキーマ（S3 実メタデータ）")
    w("")
    w("| キー | 説明 |")
    w("|---|---|")
    w("| `file_path` | `documents/<カテゴリ>[/<サブフォルダ>...]/<ファイル名>` |")
    w("| `filename` | ファイル名 |")
    w("| `category` | カテゴリ（フォルダ名由来） |")
    w("| `model_type` | 対象機種。**list 型と string 型が混在**。`*`/`general`＝全機種共通。空欄・キー欠落は 0 件 |")
    w("| `tags` / `tags_string` | サブフォルダ名（据付場用図・災害事例集・据付ノートのみ） |")
    w("| `upload_date` / `folder_depth` | 取り込み日時・階層深さ |")
    w("")
    w("記号: **⚠未索引** = KB 索引に未取り込みで検索不能（issue #53 で所有側へ修正依頼中）／")
    w("**†** = `model_type` がカンマ連結 string（`listContains` 完全一致で拾えない形式。issue #53 依頼 3）")
    w("")
    w("## 2. サマリ")
    w("")
    w("### カテゴリ別件数")
    w("")
    w("| category | 件数 | 未索引 |")
    w("|---|---:|---:|")
    ui = Counter(k.split("/")[1] for k in UNINDEXED)
    for c, n in cats.most_common():
        w(f"| {c} | {n:,} | {ui.get(c, 0) or ''} |")
    w(f"| **計** | **{len(docs):,}** | **{unindexed_found}** |")
    w("")
    w(f"### model_type 統計")
    w("")
    w(f"- 型: list {mt_list:,} 件 / string {mt_str:,} 件（うちカンマ連結 {len(comma)} 件）。空欄・キー欠落 0 件")
    w(f"- 全機種共通（`*` / `general` のみ）: {common_n} 件")
    w(f"- 異なり値: {len(mt_vals)} 種（値の業務的正しさ・表記ゆれ統合は未検証）")
    w("")
    w("### model_type 要素別件数（上位 30）")
    w("")
    for v, n in mt_vals.most_common(30):
        w(f"- `{v}`: {n} 件")
    w("")
    w("---")
    w("")
    w("## 3. 全件一覧（category 別・file_path 順）")
    w("")
    by_cat = defaultdict(list)
    for a in docs:
        by_cat[a["category"]].append(a)
    for c, n in cats.most_common():
        rows = sorted(by_cat[c], key=lambda a: a["file_path"])
        w(f"### {c}（{n:,} 件）")
        w("")
        w("| filename | model_type | サブフォルダ | 備考 |")
        w("|---|---|---|---|")
        for a in rows:
            mt = a.get("model_type")
            els = elements(mt)
            disp = " / ".join(els) if els else "(なし)"
            sub = "/".join(a["file_path"].split("/")[2:-1]) or "—"
            notes = []
            if a["file_path"] in UNINDEXED:
                notes.append("⚠未索引")
            if isinstance(mt, str) and "," in mt:
                notes.append("†")
            w(f"| `{a['filename']}` | {disp} | {sub} | {' '.join(notes)} |")
        w("")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(docs)} docs, {OUT.stat().st_size/1024:.0f} KB)")
    if unindexed_found != len(UNINDEXED):
        print(f"WARNING: UNINDEXED {len(UNINDEXED)} 件中 {unindexed_found} 件しか S3 に見つからない")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])

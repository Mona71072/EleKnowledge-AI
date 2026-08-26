#!/usr/bin/env python3
"""KB メタデータカタログ (docs/kb-metadata-catalog-<取得日>.md) を S3 実測から生成する。

使い方:
    1. データソースバケットからメタデータを全件ダウンロード:
       aws s3 cp s3://ragknowledgebasestackinst-datasourcebucket9fa93e04-ybbhm1efhyzb/docs/documents <local-dir> \
           --recursive --exclude "*" --include "*.metadata.json" --profile datautl-bple-mebs
    2. python scripts/generate_kb_metadata_catalog.py <local-dir> \
           --as-of <S3取得日 YYYY-MM-DD> [--unindexed docs/kb-unindexed-<取得日>.txt] [--overwrite]

出力は S3 の `.metadata.json` と一対一（TSV 由来の description 列は実メタデータに存在しないため出力しない）。

スナップショット方針:
- 出力ファイル名と本文の「取得日」は --as-of（S3 から実際にダウンロードした日）に従う。
  生成物は取得日時点の履歴スナップショットであり、後日の S3 再取得で過去日付のファイルを
  上書きしない（新しい取得日で別ファイルを生成する）。既存ファイルの上書きは --overwrite 指定時のみ。
- KB 索引への未取り込み (未索引) は S3 のメタデータからは判定できない。--unindexed で取得日時点の
  観測リスト（1 行 1 file_path。空行・`#` 始まりはコメント）を渡す。2026-08-26 観測分は
  docs/kb-unindexed-2026-08-26.txt（出典: docs/verification-2026-08-26-kb-vqv-metadata.md §6, issue #53）。
  再 Sync・issue #53 対応後は状態が変わり得るため、再生成時は索引状態を再確認してリストを
  更新すること。--unindexed 省略時は未索引判定なし（未確認）として生成する。
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
COMMON = {"", "*", "general"}


def elements(raw):
    els = []
    for e in (raw if isinstance(raw, list) else [raw]):
        els += [s.strip() for s in str(e).split(",") if s.strip()]
    return els


def load_unindexed(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return {s for s in (l.strip() for l in lines) if s and not s.startswith("#")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("metadata_dir", help=".metadata.json をダウンロードしたローカルディレクトリ")
    ap.add_argument("--as-of", required=True, metavar="YYYY-MM-DD",
                    help="S3 取得日。出力ファイル名 docs/kb-metadata-catalog-<取得日>.md と本文の取得日に使う")
    ap.add_argument("--unindexed", metavar="FILE",
                    help="取得日時点で KB 索引に未取り込みの file_path リスト（1 行 1 パス）。省略時は未索引判定なし")
    ap.add_argument("--overwrite", action="store_true",
                    help="出力先が既に存在する場合に上書きを許可（過去スナップショットの保護）")
    args = ap.parse_args()

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.as_of):
        sys.exit(f"--as-of は YYYY-MM-DD 形式で指定してください: {args.as_of}")
    as_of = args.as_of
    out = DOCS_DIR / f"kb-metadata-catalog-{as_of}.md"
    if out.exists() and not args.overwrite:
        sys.exit(f"{out} は既に存在します。過去スナップショットの上書き防止のため中断します。"
                 f"意図的な再生成なら --overwrite を付けてください。")

    unindexed = load_unindexed(args.unindexed) if args.unindexed else set()
    unindexed_display = Path(args.unindexed).as_posix() if args.unindexed else None

    docs = []
    for p in sorted(Path(args.metadata_dir).rglob("*.metadata.json")):
        a = json.loads(p.read_text(encoding="utf-8"))["metadataAttributes"]
        docs.append(a)
    if not docs:
        sys.exit(f"no metadata files under {args.metadata_dir}")

    cats = Counter(a["category"] for a in docs)
    mt_list = sum(1 for a in docs if isinstance(a.get("model_type"), list))
    mt_str = len(docs) - mt_list
    comma = [a for a in docs if isinstance(a.get("model_type"), str) and "," in a["model_type"]]
    mt_vals = Counter(e for a in docs for e in elements(a.get("model_type")))
    common_n = sum(1 for a in docs
                   if (els := elements(a.get("model_type"))) is not None
                   and (not els or all(e in COMMON for e in els)))
    unindexed_found = sum(1 for a in docs if a["file_path"] in unindexed)

    L = []
    w = L.append
    w("# KB 資料メタデータ一覧")
    w("")
    w(f"> **状態:** {as_of} 時点の S3 実測スナップショット（同時点の正本。以降の S3/KB 状態を保証しない）")
    w("> **ソース:** `s3://ragknowledgebasestackinst-datasourcebucket9fa93e04-ybbhm1efhyzb/docs/documents/` の全 `.metadata.json`")
    w(f"> **取得日:** {as_of} ／ **生成日:** {date.today().isoformat()} ／ **件数:** {len(docs):,} 件")
    w("> **再生成:** `python scripts/generate_kb_metadata_catalog.py <metadata-dir> --as-of <取得日> --unindexed <未索引リスト>`（手動編集しない）")
    w("> **注意:** 本ファイルは取得日時点の履歴スナップショット。後日の S3 再取得で上書きせず、新しい取得日で別ファイルを生成すること。")
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
    if unindexed_display:
        w(f"記号: **⚠未索引** = KB 索引に未取り込みで検索不能（`{unindexed_display}` に基づく取得日時点の観測値。")
        w("再 Sync・issue #53 対応後は変わり得るため、再生成時は索引状態を再確認しリストを更新すること）／")
    else:
        w("記号: （本生成では未索引リスト未指定のため ⚠未索引 の判定なし。KB 索引状態は S3 からは判定できず未確認）／")
    w("**†** = `model_type` がカンマ連結 string（VQV81CNYU4 実機確認 2026-08-26 では `listContains` 完全一致で拾えない。AWS の恒久仕様ではなく実測。issue #53 依頼 3）")
    w("")
    w("## 2. サマリ")
    w("")
    w("### カテゴリ別件数")
    w("")
    if unindexed:
        w("| category | 件数 | 未索引 |")
        w("|---|---:|---:|")
        ui = Counter(k.split("/")[1] for k in unindexed)
        for c, n in cats.most_common():
            w(f"| {c} | {n:,} | {ui.get(c, 0) or ''} |")
        w(f"| **計** | **{len(docs):,}** | **{unindexed_found}** |")
    else:
        w("| category | 件数 |")
        w("|---|---:|")
        for c, n in cats.most_common():
            w(f"| {c} | {n:,} |")
        w(f"| **計** | **{len(docs):,}** |")
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
            if a["file_path"] in unindexed:
                notes.append("⚠未索引")
            if isinstance(mt, str) and "," in mt:
                notes.append("†")
            w(f"| `{a['filename']}` | {disp} | {sub} | {' '.join(notes)} |")
        w("")
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(docs)} docs, {out.stat().st_size/1024:.0f} KB)")
    if unindexed and unindexed_found != len(unindexed):
        print(f"WARNING: 未索引リスト {len(unindexed)} 件中 {unindexed_found} 件しか S3 に見つからない"
              f"（リストが取得日時点の S3 と不整合の可能性）")


if __name__ == "__main__":
    main()

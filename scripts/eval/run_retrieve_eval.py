#!/usr/bin/env python3
"""
ゴールデン質問セットに対する retrieve 到達率の機械採点（第1層評価）。

lambda/rag/rag-function/app.py を import して本番と同じ経路
（正規化 → 聞き返しゲート → 本命優先 retrieve → 略語展開 → 弱い検索ゲート）
で dev KB を検索し、期待資料への Top-k 到達率を採点する。

第2層（Bedrock Evaluations の LLM-as-a-judge）向けに
BYOI（Bring Your Own Inference / retrieve-only）形式の JSONL も出力する。

使い方:
    AWS_PROFILE=<dev用プロファイル> python scripts/eval/run_retrieve_eval.py
    python scripts/eval/run_retrieve_eval.py --kb-id DF9XUCSPDM --search-type SEMANTIC
    python scripts/eval/run_retrieve_eval.py --compare eval-results/retrieve-eval-XXXX.json

設計・運用: docs/eval-2026-07-29-retrieve-golden-set.md
ゴールデンセット: tests/eval/golden_set.jsonl
"""
import argparse
import importlib.util
import json
import os
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RAG_APP_PATH = REPO_ROOT / "lambda" / "rag" / "rag-function" / "app.py"
DEFAULT_GOLDEN = REPO_ROOT / "tests" / "eval" / "golden_set.jsonl"
DEFAULT_OUT_DIR = REPO_ROOT / "eval-results"
HIT_KS = (1, 3, 5, 10)


def parse_args():
    p = argparse.ArgumentParser(description="Golden set retrieve evaluation (layer 1)")
    p.add_argument("--golden", default=str(DEFAULT_GOLDEN), help="golden set JSONL のパス")
    p.add_argument("--env", default="dev", help="対象環境 (SSM から KB ID を引くときに使用)")
    p.add_argument("--kb-id", default=None, help="Knowledge Base ID (省略時: env KNOWLEDGE_BASE_ID → SSM)")
    p.add_argument("--region", default=os.environ.get("AWS_REGION", "ap-northeast-1"))
    p.add_argument("--search-type", default=None, choices=["HYBRID", "SEMANTIC"],
                   help="RAG_SEARCH_TYPE の上書き (A/B 比較用)")
    p.add_argument("--limit", type=int, default=None, help="先頭 N 問だけ実行 (スモーク用)")
    p.add_argument("--only", default=None, help="カンマ区切りの id 指定で絞り込み")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--no-byoi", action="store_true", help="BYOI JSONL を出力しない")
    p.add_argument("--compare", default=None, help="過去の結果 JSON と集計を比較する")
    return p.parse_args()


def resolve_kb_id(args) -> str:
    if args.kb_id:
        return args.kb_id
    if os.environ.get("KNOWLEDGE_BASE_ID"):
        return os.environ["KNOWLEDGE_BASE_ID"]
    import boto3
    ssm = boto3.client("ssm", region_name=args.region)
    name = f"/eleknowledge/{args.env}/knowledge-base-id"
    resp = ssm.get_parameter(Name=name)
    return resp["Parameter"]["Value"]


def load_rag_module(kb_id: str, region: str, search_type: str = None):
    """本番 Lambda のモジュールを同一ロジックのまま import する（tests/unit と同じ流儀）。"""
    os.environ["KNOWLEDGE_BASE_ID"] = kb_id
    os.environ.setdefault("AWS_REGION", region)
    # モジュールが import 時に要求する env（評価では DynamoDB へ書かない）
    os.environ.setdefault("CHATLOGS_TABLE", "eval-local-dummy")
    if search_type:
        os.environ["RAG_SEARCH_TYPE"] = search_type
    spec = importlib.util.spec_from_file_location("rag_eval_app", str(RAG_APP_PATH))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rag_eval_app"] = mod
    spec.loader.exec_module(mod)
    return mod


def load_golden(path: str, only=None, limit=None) -> list:
    items = []
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            if item.get("skip"):
                continue
            if not item.get("id") or not item.get("query"):
                raise ValueError(f"{path}:{line_no}: id と query は必須です")
            items.append(item)
    if only:
        wanted = {x.strip() for x in only.split(",")}
        items = [i for i in items if i["id"] in wanted]
    if limit:
        items = items[:limit]
    return items


def norm_text(s: str) -> str:
    return unicodedata.normalize("NFKC", s or "").strip().lower()


def doc_matches(expected: str, doc_name: str) -> bool:
    """図書番号など部分文字列でのゆるい一致（例: 'C-591124' は 'C-591124_xxx.pdf' に一致）。"""
    e, d = norm_text(expected), norm_text(doc_name)
    return bool(e) and e in d


def result_doc_name(result: dict) -> str:
    meta = result.get("metadata") or {}
    uri = meta.get("x-amz-bedrock-kb-source-uri", "") or ""
    return uri.split("/")[-1] if uri else ""


def ranked_documents(results: list) -> list:
    """スコア順の結果からユニーク資料名リストを作る（表示対象外の .md は除く）。"""
    seen = []
    for r in results:
        name = result_doc_name(r)
        if not name or name.lower().endswith(".md"):
            continue
        if name not in seen:
            seen.append(name)
    return seen


def run_normal_retrieve(mod, query: str, filters: dict):
    """lambda_handler の normal モード retrieve ブロックと同じ手順。"""
    normalized = mod.normalize_query_text(query)
    expanded = mod.expand_query_abbreviations(normalized)
    q1 = normalized or query

    kb1 = mod.retrieve_for_normal_query(q1, filters, number_of_results=30)
    priority_expanded = bool(kb1.pop("_priorityExpanded", False))
    r1 = kb1.get("retrievalResults") or []
    s1 = mod.select_retrieval_results(r1, mode="normal")

    r2 = []
    used_abbrev_expansion = False
    if expanded and expanded != q1 and len(s1) == 0:
        kb2 = mod.retrieve_for_normal_query(expanded, filters, number_of_results=30)
        priority_expanded = priority_expanded or bool(kb2.pop("_priorityExpanded", False))
        r2 = kb2.get("retrievalResults") or []
        used_abbrev_expansion = True

    merged = mod.merge_retrieval_results(r1, r2)
    return merged, priority_expanded, used_abbrev_expansion


def score_item(mod, item: dict) -> dict:
    query = item["query"]
    filters = item.get("filters") or {}
    expected_docs = [e for e in (item.get("expected_documents") or []) if e]
    expected_pages = item.get("expected_pages") or []
    expected_gate = item.get("expected_gate")

    row = {
        "id": item["id"],
        "query": query,
        "filters": filters,
        "tags": item.get("tags") or [],
        "labeled": bool(expected_docs),
        "expected_documents": expected_docs,
        "expected_gate": expected_gate,
    }

    # --- 聞き返しゲート（本番同様、clarify なら検索しない） ---
    should_clarify, _ = mod.needs_clarify(query, filters, chat_history=[])
    if should_clarify:
        row.update({
            "predicted_gate": "clarify",
            "gate_ok": (expected_gate == "clarify") if expected_gate else None,
            "first_hit_rank": None,
            "hits": {f"hit@{k}": False for k in HIT_KS},
            "hit_in_candidates": False,
            "page_hit": None,
            "top_docs": [],
            "selected_results": [],
        })
        return row

    merged, priority_expanded, used_expansion = run_normal_retrieve(mod, query, filters)
    weak = mod.is_weak_retrieval(merged, mode="normal")
    predicted_gate = "not_found" if weak else "pages"

    selected = mod.select_retrieval_results(merged, mode="normal")
    ranked = ranked_documents(merged)
    candidate_docs = ranked_documents(selected)[:5]  # UI の pageCandidates 相当

    first_hit_rank = None
    for rank, name in enumerate(ranked, start=1):
        if any(doc_matches(e, name) for e in expected_docs):
            first_hit_rank = rank
            break

    page_hit = None
    if expected_docs and expected_pages:
        page_hit = False
        for r in merged:
            name = result_doc_name(r)
            if any(doc_matches(e, name) for e in expected_docs):
                page = mod.extract_page_number(r.get("metadata") or {})
                if page in expected_pages:
                    page_hit = True
                    break

    top_docs = []
    for r in selected[:5]:
        meta = r.get("metadata") or {}
        top_docs.append({
            "document": result_doc_name(r),
            "category": meta.get("category", "") or "",
            "model_type": meta.get("model_type", "") or "",
            "page": mod.extract_page_number(meta),
            "score": round(float(r.get("score", 0.0) or 0.0), 4),
        })

    row.update({
        "predicted_gate": predicted_gate,
        "gate_ok": (predicted_gate == expected_gate) if expected_gate else None,
        "priority_expanded": priority_expanded,
        "used_abbrev_expansion": used_expansion,
        "first_hit_rank": first_hit_rank,
        "hits": {f"hit@{k}": (first_hit_rank is not None and first_hit_rank <= k) for k in HIT_KS},
        "hit_in_candidates": any(
            any(doc_matches(e, name) for e in expected_docs) for name in candidate_docs
        ) if expected_docs else False,
        "page_hit": page_hit,
        "top_docs": top_docs,
        "selected_results": [
            {
                "name": result_doc_name(r),
                "text": (mod.chunk_text(r) or "").strip(),
                "metadata": r.get("metadata") or {},
                "score": float(r.get("score", 0.0) or 0.0),
            }
            for r in selected
        ],
    })
    return row


def aggregate(rows: list) -> dict:
    labeled = [r for r in rows if r["labeled"]]
    gated = [r for r in rows if r.get("expected_gate")]
    summary = {
        "total": len(rows),
        "labeled": len(labeled),
        "unlabeled": len(rows) - len(labeled),
    }
    for k in HIT_KS:
        key = f"hit@{k}"
        summary[key] = (
            round(sum(1 for r in labeled if r["hits"][key]) / len(labeled), 3) if labeled else None
        )
    if labeled:
        rr = [1.0 / r["first_hit_rank"] for r in labeled if r["first_hit_rank"]]
        summary["mrr"] = round(sum(rr) / len(labeled), 3)
        summary["hit_in_candidates"] = round(
            sum(1 for r in labeled if r["hit_in_candidates"]) / len(labeled), 3
        )
    else:
        summary["mrr"] = None
        summary["hit_in_candidates"] = None
    summary["gate_accuracy"] = (
        round(sum(1 for r in gated if r["gate_ok"]) / len(gated), 3) if gated else None
    )
    summary["gate_total"] = len(gated)
    return summary


def build_byoi_lines(rows: list, kb_identifier: str) -> list:
    """Bedrock Evaluations RAG 評価 (retrieve-only / BYOI) 用 JSONL。

    形式: docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-prompt-retrieve.html
    """
    lines = []
    for r in rows:
        if r.get("predicted_gate") == "clarify" or not r.get("selected_results"):
            continue
        retrieval_results = []
        for s in r["selected_results"]:
            meta = s.get("metadata") or {}
            retrieval_results.append({
                "name": s.get("name") or "unknown",
                "content": {"text": s.get("text") or "[IMAGE チャンク: 本文なし]"},
                "metadata": {
                    "category": str(meta.get("category", "") or ""),
                    "model_type": str(meta.get("model_type", "") or ""),
                    "score": str(round(s.get("score", 0.0), 4)),
                },
            })
        turn = {
            "prompt": {"content": [{"text": r["query"]}]},
            "output": {
                "knowledgeBaseIdentifier": kb_identifier,
                "retrievedResults": {"retrievalResults": retrieval_results},
            },
        }
        reference = None
        if r.get("reference_answer"):
            reference = r["reference_answer"]
        elif r.get("expected_documents"):
            reference = "該当資料: " + ", ".join(r["expected_documents"])
        if reference:
            turn["referenceResponses"] = [{"content": [{"text": reference}]}]
        lines.append(json.dumps({"conversationTurns": [turn]}, ensure_ascii=False))
    return lines


def print_report(rows: list, summary: dict):
    print()
    print("=" * 72)
    print("個別結果")
    print("=" * 72)
    for r in rows:
        gate = r.get("predicted_gate")
        mark_gate = ""
        if r.get("expected_gate"):
            mark_gate = " [gate OK]" if r["gate_ok"] else f" [gate NG: 期待 {r['expected_gate']}]"
        if r["labeled"]:
            rank = r["first_hit_rank"]
            hit = f"rank={rank}" if rank else "MISS"
            cand = " (候補頁に表示)" if r["hit_in_candidates"] else ""
            print(f"  {r['id']}: {hit}{cand} / gate={gate}{mark_gate}  {r['query'][:40]}")
        else:
            print(f"  {r['id']}: [未ラベル] gate={gate}{mark_gate}  {r['query'][:40]}")
            for d in r.get("top_docs", []):
                page = f" p.{d['page']}" if d["page"] is not None else ""
                print(f"      候補: {d['document']}{page} ({d['category']}, score={d['score']})")
    print()
    print("=" * 72)
    print("集計")
    print("=" * 72)
    for k, v in summary.items():
        print(f"  {k}: {v}")


def print_compare(summary: dict, compare_path: str):
    with open(compare_path, encoding="utf-8") as f:
        prev = json.load(f).get("summary", {})
    print()
    print("=" * 72)
    print(f"比較: {compare_path}")
    print("=" * 72)
    for key in ["hit@1", "hit@3", "hit@5", "hit@10", "mrr", "hit_in_candidates", "gate_accuracy"]:
        old, new = prev.get(key), summary.get(key)
        if old is None or new is None:
            continue
        delta = round(new - old, 3)
        arrow = "+" if delta > 0 else ""
        print(f"  {key}: {old} -> {new} ({arrow}{delta})")


def main():
    args = parse_args()
    try:
        kb_id = resolve_kb_id(args)
    except Exception as e:
        if type(e).__name__ in ("NoCredentialsError", "ProfileNotFound", "SSOTokenLoadError"):
            print("AWS 認証情報が見つかりません。実行前に次のいずれかを設定してください:")
            print("  - AWS_PROFILE=<dev用プロファイル> を付けて実行")
            print("  - aws configure / aws sso login で認証情報を用意")
            print("必要権限: bedrock:Retrieve（対象 KB）, ssm:GetParameter（--kb-id 指定時は不要）")
            return 1
        raise
    mod = load_rag_module(kb_id, args.region, args.search_type)
    items = load_golden(args.golden, only=args.only, limit=args.limit)
    if not items:
        print("採点対象がありません（skip 行のみ？）")
        return 1

    print(f"KB: {kb_id} / region: {args.region} / search: {mod.RAG_SEARCH_TYPE} / 質問数: {len(items)}")

    rows = []
    for item in items:
        try:
            row = score_item(mod, item)
            if item.get("reference_answer"):
                row["reference_answer"] = item["reference_answer"]
        except Exception as e:  # 1問の失敗で全体を止めない
            row = {
                "id": item["id"], "query": item["query"], "filters": item.get("filters") or {},
                "tags": item.get("tags") or [], "labeled": False,
                "expected_documents": [], "expected_gate": item.get("expected_gate"),
                "error": str(e), "predicted_gate": None, "gate_ok": None,
                "first_hit_rank": None, "hits": {f"hit@{k}": False for k in HIT_KS},
                "hit_in_candidates": False, "page_hit": None, "top_docs": [],
                "selected_results": [],
            }
            print(f"  {item['id']}: ERROR {e}")
        rows.append(row)

    summary = aggregate(rows)
    print_report(rows, summary)
    if args.compare:
        print_compare(summary, args.compare)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    result_path = out_dir / f"retrieve-eval-{stamp}.json"
    detail_rows = [{k: v for k, v in r.items() if k != "selected_results"} for r in rows]
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": stamp,
            "kb_id": kb_id,
            "search_type": mod.RAG_SEARCH_TYPE,
            "golden": str(args.golden),
            "summary": summary,
            "rows": detail_rows,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n結果: {result_path}")

    if not args.no_byoi:
        byoi_lines = build_byoi_lines(rows, kb_identifier=f"eleknowledge-{args.env}-app-path")
        if byoi_lines:
            byoi_path = out_dir / f"retrieve-eval-{stamp}-byoi.jsonl"
            with open(byoi_path, "w", encoding="utf-8") as f:
                f.write("\n".join(byoi_lines) + "\n")
            print(f"BYOI (Bedrock Evaluations 用): {byoi_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Pure answer-context construction for EleKnowledge RAG.

This module prepares references and Anthropic message payloads but performs no
Bedrock API calls.  Generation transport/model invocation remains a separate
responsibility.

注意（移行期間中）: app.py はまだ本モジュールを import しておらず、本番 Lambda は
app.py 側のコピーで動作している。app.py の該当ロジックを変更する場合は、必ず
本モジュールと tests/unit/test_rag_answer_policy.py のパリティテストも同時に
更新すること。
"""
from retrieval_policy import chunk_image_b64, chunk_text


MAX_IMAGE_BLOCKS = 3


def _merge_claude_content(previous, new):
    """Merge two Claude message content values (str or multimodal list)."""
    if isinstance(previous, str) and isinstance(new, str):
        return f"{previous}\n{new}"
    previous_blocks = (
        previous if isinstance(previous, list) else [{"type": "text", "text": previous}]
    )
    new_blocks = new if isinstance(new, list) else [{"type": "text", "text": new}]
    return previous_blocks + new_blocks


def append_claude_message(messages: list, role: str, content) -> None:
    """Append a message while keeping Anthropic user/assistant alternation valid."""
    if role not in ("user", "assistant"):
        role = "user"
    if content is None or content == "" or content == []:
        return
    if messages and messages[-1]["role"] == role:
        messages[-1]["content"] = _merge_claude_content(messages[-1]["content"], content)
    else:
        messages.append({"role": role, "content": content})


def build_question_text_for_claude(query: str, search_query: str = None) -> str:
    """Expose the composed retrieval query when it differs from the raw user turn."""
    raw_query = (query or "").strip()
    composed_query = (search_query or "").strip()
    if composed_query and composed_query != raw_query:
        return f"【検索クエリ】\n{composed_query}\n\n【ユーザー入力】\n{raw_query}"
    return composed_query or raw_query


def build_references_block(selected_results: list) -> str:
    """Create the existing structured text block supplied to Claude."""
    if not selected_results:
        return ""

    lines = []
    max_chars_per_chunk = 1200

    for index, result in enumerate(selected_results, start=1):
        score = result.get("score", 0.0) or 0.0
        metadata = result.get("metadata", {}) or {}
        doc_uri = metadata.get("x-amz-bedrock-kb-source-uri", "") or ""
        doc_name = doc_uri.split("/")[-1] if doc_uri else "Unknown"
        title = metadata.get("title") or ""
        category = metadata.get("category", "") or ""
        model_type = metadata.get("model_type", "") or ""

        text = chunk_text(result).strip()
        if len(text) > max_chars_per_chunk:
            text = text[:max_chars_per_chunk].rstrip() + "…"

        header_parts = [
            f"[{index}]",
            f"score={score:.3f}",
            f"file={doc_name}",
        ]
        if title:
            header_parts.append(f"title={title}")
        if category:
            header_parts.append(f"category={category}")
        if model_type:
            header_parts.append(f"model_type={model_type}")

        lines.append(" ".join(header_parts))
        lines.append(
            text
            if text
            else "[図表] この資料の該当箇所は画像です。添付画像を参照してください。"
        )
        lines.append("")

    return "\n".join(lines).strip()


def build_claude_messages(
    query: str,
    selected_results: list,
    chat_history: list = None,
    search_query: str = None,
) -> list:
    """Build the current Anthropic message sequence without invoking a model."""
    search_results = build_references_block(selected_results)
    if search_results.strip():
        references_block = f"<references>\n{search_results}\n</references>"
    else:
        references_block = (
            "<references>\n[検索結果] 検索結果が0件でした"
            "（検索漏れの可能性があります）。\n</references>"
        )

    reference_content = [{"type": "text", "text": references_block}]
    for result in selected_results or []:
        if len(reference_content) > MAX_IMAGE_BLOCKS:
            break
        image_b64 = chunk_image_b64(result)
        if image_b64:
            reference_content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_b64,
                    },
                }
            )

    messages = []
    if chat_history:
        for message in chat_history:
            role = message.get("role", "user")
            content = message.get("content", "")
            if not content:
                continue
            if role not in ("user", "assistant"):
                role = "user"
            append_claude_message(messages, role, content)

    if messages and messages[0]["role"] == "assistant":
        messages.pop(0)

    if messages and messages[-1]["role"] == "user":
        append_claude_message(
            messages,
            "assistant",
            "追記を受け取りました。参照資料に基づき短い整理をします。",
        )

    question_text = build_question_text_for_claude(query, search_query)
    final_content = list(reference_content) + [{"type": "text", "text": question_text}]
    append_claude_message(messages, "user", final_content)
    return messages

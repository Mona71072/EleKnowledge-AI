"""Bedrock request construction and invocation for the Senpai synthesis Lambda.

Capability handling mirrors rag-function/model_profile.py in minimal form so this
function stays deployable on its own (it must not import from rag-function).
"""
import json
import os
import re

from botocore.config import Config

DEFAULT_MAX_TOKENS = 2048
MIN_MAX_TOKENS = 256
MAX_MAX_TOKENS = 4096
LEGACY_TEMPERATURE = 0.3
DEFAULT_READ_TIMEOUT_SECONDS = 22
# API Gateway integration timeout is 29s; leave room for the DynamoDB write.
MAX_READ_TIMEOUT_SECONDS = 27

# (sampling, thinking_disable, effort, api). Longer keys win; keys ending in '-'
# match a model family prefix. Unknown models fall back to a minimal request.
_PROFILES = {
    "gpt-6-luna": (False, False, False, "converse"),
    "sonnet-5-5": (False, False, True, "invoke"),
    "opus-5-5": (False, False, True, "invoke"),
    "fable-5-1": (False, False, True, "invoke"),
    "sonnet-5": (False, True, True, "invoke"),
    "opus-5": (False, True, True, "invoke"),
    "opus-4-7": (False, True, True, "invoke"),
    "opus-4-8": (False, True, True, "invoke"),
    "haiku-4-5": (True, False, False, "invoke"),
    "haiku-3-": (True, False, False, "invoke"),
    "sonnet-3-": (True, False, False, "invoke"),
    "opus-3-": (True, False, False, "invoke"),
    "opus-4-": (True, False, False, "invoke"),
    "3-5-haiku": (True, False, False, "invoke"),
    "3-7-sonnet": (True, False, False, "invoke"),
    "3-5-sonnet": (True, False, False, "invoke"),
    "sonnet-4": (True, False, False, "invoke"),
}
_MINIMAL = (False, False, False, "invoke")
_REGION_PREFIXES = {"global", "jp", "us", "apac", "eu", "au", "ca", "in"}


def _normalize(model_id: str) -> str:
    parts = (model_id or "").strip().lower().split(".")
    if parts and parts[0] in _REGION_PREFIXES:
        parts = parts[1:]
    if parts and parts[0] in {"anthropic", "openai"}:
        parts = parts[1:]
    name = ".".join(parts)
    if name.startswith("claude-"):
        name = name[len("claude-"):]
    return re.sub(r"-\d{8}-v\d+:\d+$", "", name)


def _profile(model_id: str) -> tuple:
    name = _normalize(model_id)
    for key in sorted(_PROFILES, key=len, reverse=True):
        if name == key or (key.endswith("-") and name.startswith(key)):
            return _PROFILES[key]
    return _MINIMAL


def _bounded_int(name: str, default: int, low: int, high: int) -> int:
    try:
        value = int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default
    return min(max(value, low), high)


def max_tokens_from_env() -> int:
    return _bounded_int("SENPAI_SYNTHESIS_MAX_TOKENS", DEFAULT_MAX_TOKENS, MIN_MAX_TOKENS, MAX_MAX_TOKENS)


def client_config() -> Config:
    """Single attempt with a read timeout that fits inside the API Gateway limit."""
    read_timeout = _bounded_int(
        "BEDROCK_READ_TIMEOUT", DEFAULT_READ_TIMEOUT_SECONDS, 1, MAX_READ_TIMEOUT_SECONDS
    )
    return Config(
        read_timeout=read_timeout,
        connect_timeout=5,
        retries={"total_max_attempts": 1},
    )


def build_request_body(system_prompt: str, messages: list, model_id: str, max_tokens: int) -> dict:
    sampling, thinking_disable, effort, _api = _profile(model_id)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": messages,
        "system": system_prompt,
    }
    if sampling:
        body["temperature"] = LEGACY_TEMPERATURE
    elif thinking_disable:
        body["thinking"] = {"type": "disabled"}
    elif effort:
        body["output_config"] = {"effort": "low"}
    return body


def _extract_invoke_text(response_body: dict) -> str:
    for block in response_body.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text" and isinstance(block.get("text"), str):
            return block["text"]
    return ""


def _invoke_converse(client, model_id: str, system_prompt: str, messages: list, max_tokens: int) -> str:
    converse_messages = [
        {"role": message["role"], "content": [
            {"text": block["text"]} for block in message["content"] if block.get("type") == "text"
        ]}
        for message in messages
    ]
    response = client.converse(
        modelId=model_id,
        messages=converse_messages,
        system=[{"text": system_prompt}],
        inferenceConfig={"maxTokens": max_tokens},
    )
    content = ((response.get("output") or {}).get("message") or {}).get("content") or []
    return "".join(
        block["text"] for block in content
        if isinstance(block, dict) and isinstance(block.get("text"), str)
    )


def generate(client, model_id: str, system_prompt: str, messages: list, max_tokens: int) -> str:
    """Return the generated text using the API the configured model supports."""
    if _profile(model_id)[3] == "converse":
        return _invoke_converse(client, model_id, system_prompt, messages, max_tokens)
    body = build_request_body(system_prompt, messages, model_id, max_tokens)
    response = client.invoke_model(modelId=model_id, body=json.dumps(body, ensure_ascii=False))
    return _extract_invoke_text(json.loads(response["body"].read()))

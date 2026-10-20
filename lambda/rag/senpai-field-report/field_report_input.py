"""Strict validation of the user-confirmed field report body."""
import re
import uuid

from field_report_vocab import (
    CONDITION_MAX_CHARS,
    FINDING_MAX_CHARS,
    MAX_CARD_REACTIONS,
    MODEL_TYPES,
    REACTIONS,
)

REQUIRED_KEYS = frozenset({"senpaiConversationId", "senpaiTurnId", "finding", "cardReactions", "confirmed"})
OPTIONAL_KEYS = frozenset({"condition", "modelType"})
REACTION_KEYS = frozenset({"knowledgeId", "cardVersion", "reaction"})
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$")
# Keep \n and \t; drop every other control character (CR is normalized first).
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


class InputError(ValueError):
    """The request body does not satisfy the contract."""


def canonical_uuid(value) -> bool:
    try:
        return isinstance(value, str) and str(uuid.UUID(value)) == value
    except (ValueError, AttributeError):
        return False


def clean_text(value, limit: int, *, required: bool) -> str:
    if value is None and not required:
        return ""
    if not isinstance(value, str):
        raise InputError("text must be a string")
    text = CONTROL_CHARS.sub("", value.replace("\r\n", "\n").replace("\r", "\n")).strip()
    if required and not text:
        raise InputError("text is required")
    if len(text) > limit:
        raise InputError("text is too long")
    return text


def _reactions(value) -> list:
    if not isinstance(value, list) or len(value) > MAX_CARD_REACTIONS:
        raise InputError("cardReactions is invalid")
    seen = set()
    reactions = []
    for entry in value:
        if not isinstance(entry, dict) or set(entry) != REACTION_KEYS:
            raise InputError("card reaction fields are invalid")
        knowledge_id, version, reaction = entry["knowledgeId"], entry["cardVersion"], entry["reaction"]
        if not isinstance(knowledge_id, str) or not ID_PATTERN.match(knowledge_id):
            raise InputError("knowledgeId is invalid")
        if type(version) is not int or not 1 <= version <= 1_000_000:
            raise InputError("cardVersion is invalid")
        if reaction not in REACTIONS:
            raise InputError("reaction is invalid")
        if knowledge_id in seen:
            raise InputError("duplicate card reaction")
        seen.add(knowledge_id)
        reactions.append({"knowledgeId": knowledge_id, "cardVersion": version, "reaction": reaction})
    return reactions


def parse_body(body) -> dict:
    """Return the normalized report fields or raise InputError."""
    if not isinstance(body, dict):
        raise InputError("body must be an object")
    keys = set(body)
    if not REQUIRED_KEYS <= keys or keys - REQUIRED_KEYS - OPTIONAL_KEYS:
        raise InputError("unexpected fields")
    if body["confirmed"] is not True:
        raise InputError("the user must confirm the content")
    conversation_id, turn_id = body["senpaiConversationId"], body["senpaiTurnId"]
    if not (canonical_uuid(conversation_id) and canonical_uuid(turn_id)):
        raise InputError("identifiers are invalid")
    model_type = body.get("modelType")
    if model_type is not None and model_type not in MODEL_TYPES:
        raise InputError("modelType is invalid")
    return {
        "senpaiConversationId": conversation_id,
        "senpaiTurnId": turn_id,
        "finding": clean_text(body["finding"], FINDING_MAX_CHARS, required=True),
        "condition": clean_text(body.get("condition"), CONDITION_MAX_CHARS, required=False),
        "modelType": model_type,
        "cardReactions": _reactions(body["cardReactions"]),
    }

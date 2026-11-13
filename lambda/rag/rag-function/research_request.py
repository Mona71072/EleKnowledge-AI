"""Validation and normalization for the long-running research API."""

import uuid
from typing import Any


MAX_QUERY_LENGTH = 2000
ALLOWED_FILTER_KEYS = frozenset({"category", "modelType"})


def normalize_research_request(body: object) -> dict[str, Any]:
    """Validate a research request and return only its supported fields."""
    if not isinstance(body, dict):
        raise ValueError("Request body must be an object")

    query = body.get("query")
    if not isinstance(query, str):
        raise ValueError("Query must be a string")
    query = query.strip()
    if not 1 <= len(query) <= MAX_QUERY_LENGTH:
        raise ValueError("Query must contain 1 to 2000 characters")

    client_request_id = body.get("clientRequestId")
    if not isinstance(client_request_id, str):
        raise ValueError("clientRequestId must be a UUID")
    try:
        client_request_id = str(uuid.UUID(client_request_id))
    except ValueError as exc:
        raise ValueError("clientRequestId must be a UUID") from exc

    normalized: dict[str, Any] = {
        "query": query,
        "clientRequestId": client_request_id,
    }

    session_id = body.get("sessionId")
    if session_id is not None:
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("sessionId must be a non-empty string")
        normalized["sessionId"] = session_id.strip()

    filters = body.get("filters")
    if filters is not None:
        if not isinstance(filters, dict) or not set(filters).issubset(ALLOWED_FILTER_KEYS):
            raise ValueError("filters must contain only category and modelType")

        clean_filters: dict[str, Any] = {}
        category = filters.get("category")
        if category is not None:
            categories = category if isinstance(category, list) else [category]
            if not categories or any(not isinstance(item, str) or not item.strip() for item in categories):
                raise ValueError("filters.category must contain non-empty strings")
            clean_filters["category"] = (
                [item.strip() for item in categories]
                if isinstance(category, list)
                else category.strip()
            )

        model_type = filters.get("modelType")
        if model_type is not None:
            if not isinstance(model_type, str) or not model_type.strip():
                raise ValueError("filters.modelType must be a non-empty string")
            clean_filters["modelType"] = model_type.strip()

        normalized["filters"] = clean_filters

    return normalized
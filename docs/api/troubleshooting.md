---
status: development
phase: 3
last-verified: 2026-05-27
related-code: lambda/troubleshooting/orchestrator/, lambda/troubleshooting/history/, infrastructure/sam/phase3-template.yaml
---

# Troubleshooting API

Phase 3 のトラブルシューティング機能で使う API。`chat-api` とは別の API Gateway として作成する。

Frontend environment variable:

- `NEXT_PUBLIC_TROUBLESHOOTING_API_URL`

This variable must be the troubleshooting API base path:

```text
https://{api-id}.execute-api.{region}.amazonaws.com/{env}/troubleshooting
```

The frontend appends `/analyze` and `/history`.

## Authentication

All endpoints require a Cognito ID token.

Phase 3 SAM uses API Gateway Cognito Authorizer. Downstream Lambda functions read the user ID from:

- `requestContext.authorizer.claims.sub`

For local tests and older events, Lambda functions also accept:

- `requestContext.authorizer.userId`

Header:

```http
Authorization: Bearer <Cognito ID Token>
```

## Endpoints

| Method | Path | Lambda | Purpose |
| --- | --- | --- | --- |
| `POST` | `/analyze` | `orchestrator-dev` | Analyze a troubleshooting request and return recommendations |
| `GET` | `/history` | `history-dev` | List the current user's latest troubleshooting sessions |
| `GET` | `/history?sessionId={id}` | `history-dev` | Return one troubleshooting session if it belongs to the current user |

The deployed API Gateway paths are:

- `/troubleshooting/analyze`
- `/troubleshooting/history`

## POST /analyze

Runs the troubleshooting orchestration flow. The Lambda creates a session record, invokes the Bedrock Agent, merges citations, stores the result, and returns the response.

Session data is stored in `sessions-dev` for the `dev` environment. Production uses `sessions-prd`.

### Request

```json
{
  "constructionNumber": "EIK54801",
  "troubleDescription": "エレベーターが動かない。制御盤のランプが全て消えている。",
  "model": "KE-LG",
  "errorCode": "E34"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `constructionNumber` | string | Conditional | Construction number. Required when `model` is not provided. |
| `troubleDescription` | string | Yes | User-entered trouble description. |
| `model` | string | Conditional | Equipment model. Required when `constructionNumber` is not provided. |
| `errorCode` | string | No | Optional error code. |

### Response 200

```json
{
  "sessionId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "result": "Markdown troubleshooting response...",
  "sourceDocuments": [
    {
      "documentName": "case.md",
      "title": "Trouble case",
      "sourceUri": "https://...",
      "documentType": "Trouble-Cases",
      "model": "KE-LG",
      "relevance": 0.85,
      "source_action": "trouble_cases"
    }
  ]
}
```

### `sourceDocuments`

| Field | Type | Description |
| --- | --- | --- |
| `documentName` | string | Source file name or object key. |
| `title` | string or null | Knowledge Base metadata title. |
| `sourceUri` | string | Presigned URL when available, otherwise source URI. |
| `documentType` | string | Knowledge Base metadata document type. |
| `model` | string | Knowledge Base metadata model. |
| `relevance` | number | Retrieval score. |
| `source_action` | string | Retrieval source identifier. |

Allowed `source_action` values:

| Value | Meaning | Search Lambda |
| --- | --- | --- |
| `trouble_cases` | Trouble case search result | `kb-search-cases-dev` |
| `manual` | Troubleshooting manual search result | `kb-search-manuals-dev` |
| `c_material` | C-material search result | `kb-search-materials-dev` |

### Error Responses

| Status | Meaning |
| --- | --- |
| `400` | Invalid request body or missing required input. |
| `401` | Missing or invalid Cognito token. |
| `500` | Internal error, Bedrock Agent error, or downstream service failure. |

## GET /history

Returns the latest troubleshooting sessions for the authenticated user.

### Response 200

```json
{
  "sessions": [
    {
      "sessionId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "timestamp": "2026-05-26T10:30:00+00:00",
      "input": {
        "constructionNumber": "EIK54801",
        "model": "KE-LG",
        "troubleDescription": "エレベーターが動かない..."
      },
      "preview": "Markdown troubleshooting response..."
    }
  ]
}
```

## GET /history?sessionId={id}

Returns one complete session if it belongs to the authenticated user.

### Response 200

```json
{
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "userId": "cognito-sub-uuid",
  "timestamp": "2026-05-26T10:30:00+00:00",
  "input": {
    "constructionNumber": "EIK54801",
    "model": "KE-LG",
    "troubleDescription": "エレベーターが動かない..."
  },
  "result": "Markdown troubleshooting response...",
  "sourceDocuments": [
    {
      "documentName": "case.md",
      "source_action": "trouble_cases"
    }
  ]
}
```

### Response 404

Returned when the session does not exist or belongs to another user.

## DynamoDB Session Table

Environment-specific table names:

- `dev`: `sessions-dev`
- `prd`: `sessions-prd`

| Attribute | Type | Description |
| --- | --- | --- |
| `session_id` | String | Partition key. UUID generated by orchestrator. |
| `userId` | String | Cognito subject. GSI partition key. |
| `timestamp` | String | ISO 8601 timestamp. GSI sort key. |
| `ttl` | Number | DynamoDB TTL epoch seconds. |
| `input` | Map | Original request input. |
| `citations` | List | Citation records written by KB search Lambda functions. |
| `result` | String | Final generated answer. |
| `sourceDocuments` | List | API response source document list with `source_action`. |

GSI:

- `userId-timestamp-index`

## CORS

| Header | Value |
| --- | --- |
| `Access-Control-Allow-Origin` | `*` |
| `Access-Control-Allow-Methods` | `GET, POST, OPTIONS` |
| `Access-Control-Allow-Headers` | `Content-Type, Authorization` |

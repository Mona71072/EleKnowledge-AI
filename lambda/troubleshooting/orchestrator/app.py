"""
トラブルシューティング エージェント Orchestrator Lambda
入力検証、Bedrock Agent 呼び出し、セッション保存、結果統合を担当
"""
import json
import logging
import os
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AGENT_ID = os.environ.get("AGENT_ID", "")
AGENT_ALIAS_ID = os.environ.get("AGENT_ALIAS_ID", "TSTALIASID")
DOCUMENTS_BUCKET = os.environ.get("DOCUMENTS_BUCKET", "")
SESSIONS_TABLE = os.environ.get("SESSIONS_TABLE", "troubleshooting-sessions")

ALLOWED_MODELS = ["KE-LG", "KM-LD", "CM-MA", "ME-CH"]
TTL_30_DAYS = 30 * 24 * 3600

s3_client = boto3.client("s3", region_name=os.environ.get("BEDROCK_REGION", "us-east-1"))
dynamodb_resource = boto3.resource("dynamodb")


class ValidationError(Exception):
    pass


# ---------------------------------------------------------------------------
# 入力バリデーション
# ---------------------------------------------------------------------------

def validate_input(request_body: Dict[str, Any]) -> Dict[str, Any]:
    construction_number = request_body.get("constructionNumber", "").strip()
    model = request_body.get("model", "").strip()

    if not construction_number and not model:
        raise ValidationError("constructionNumber か model のどちらかは必須です")

    if construction_number and not re.match(r"^[A-Za-z0-9]{8}$", construction_number):
        raise ValidationError("工事番号は半角英数8文字で指定してください")

    trouble_description = request_body.get("troubleDescription", "").strip()
    if not trouble_description:
        raise ValidationError("troubleDescription は必須です")
    if len(trouble_description) < 5 or len(trouble_description) > 2000:
        raise ValidationError("不具合情報は5～2000文字で入力してください")

    if model and model not in ALLOWED_MODELS:
        raise ValidationError(f"model は {ALLOWED_MODELS} から選択してください")

    error_code = request_body.get("errorCode", "").strip()
    if error_code and not re.match(r"^[A-Z0-9]{4}$", error_code):
        raise ValidationError("エラーコードは半角英数4文字で指定してください")

    result = {"troubleDescription": trouble_description}
    if construction_number:
        result["constructionNumber"] = construction_number
    if model:
        result["model"] = model
    if error_code:
        result["errorCode"] = error_code
    return result


def format_agent_input(validated_data: Dict[str, Any]) -> str:
    lines = ["【現場情報】"]
    if "constructionNumber" in validated_data:
        lines.append(f"工事番号: {validated_data['constructionNumber']}")
    if "model" in validated_data:
        lines.append(f"機種: {validated_data['model']}")
    if "errorCode" in validated_data:
        lines.append(f"エラーコード: {validated_data['errorCode']}")
    lines.append(f"不具合内容: {validated_data['troubleDescription']}")
    lines.append("\n【処理要求】")
    lines.append("現場情報を取得し、トラブルシューティングを行ってください")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# DynamoDB セッション管理
# ---------------------------------------------------------------------------

def extract_user_id(event: Dict[str, Any]) -> str:
    return event.get("requestContext", {}).get("authorizer", {}).get("userId", "anonymous")


def init_session(session_id: str, validated: Dict[str, Any], user_id: str):
    dynamodb_resource.Table(SESSIONS_TABLE).put_item(Item={
        "session_id": session_id,
        "userId": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ttl": int(time.time()) + TTL_30_DAYS,
        "input": {k: v for k, v in validated.items()},
        "citations": [],
    })


def fetch_citations(session_id: str) -> List[Dict]:
    resp = dynamodb_resource.Table(SESSIONS_TABLE).get_item(Key={"session_id": session_id})
    return resp.get("Item", {}).get("citations", [])


def save_session_result(session_id: str, result_text: str, source_docs: List[Dict]):
    dynamodb_resource.Table(SESSIONS_TABLE).update_item(
        Key={"session_id": session_id},
        UpdateExpression="SET #r = :r, sourceDocuments = :sd",
        ExpressionAttributeNames={"#r": "result"},
        ExpressionAttributeValues={":r": result_text, ":sd": source_docs},
    )


# ---------------------------------------------------------------------------
# Bedrock Agent 呼び出し
# ---------------------------------------------------------------------------

def invoke_agent(input_text: str, session_id: str) -> Dict[str, Any]:
    client = boto3.client("bedrock-agent-runtime")
    return client.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=session_id,
        sessionState={"sessionAttributes": {"session_id": session_id}},
        inputText=input_text,
    )


def parse_agent_response(response: Dict[str, Any]) -> Tuple[str, List[Dict]]:
    output_parts = []
    raw_refs = []
    chunk_count = 0
    citation_count = 0

    for event in response.get("completion", []):
        if "chunk" in event:
            chunk_count += 1
            chunk = event["chunk"]
            chunk_bytes = chunk.get("bytes", b"")
            if chunk_bytes:
                output_parts.append(chunk_bytes.decode("utf-8"))
            for citation in chunk.get("attribution", {}).get("citations", []):
                citation_count += 1
                raw_refs.extend(citation.get("retrievedReferences", []))

    logger.info(f"EventStream: chunks={chunk_count}, citations={citation_count}, retrievedRefs={len(raw_refs)}")
    for i, ref in enumerate(raw_refs):
        uri = (ref.get("location", {}).get("s3Location", {}).get("uri") or
               ref.get("metadata", {}).get("x-amz-bedrock-kb-source-uri", ""))
        logger.info(f"  ref[{i}]: uri={uri}, score={ref.get('score')}")

    result = "".join(output_parts)
    return result if result else "応答を取得できませんでした", raw_refs


# ---------------------------------------------------------------------------
# sourceDocuments 生成
# ---------------------------------------------------------------------------

def _append_doc(docs: List[Dict], seen: set, uri: str, meta: Dict, score: float):
    if not uri or uri in seen:
        return
    seen.add(uri)
    signed_url = uri
    if DOCUMENTS_BUCKET and uri.startswith("s3://"):
        key = uri.replace(f"s3://{DOCUMENTS_BUCKET}/", "")
        try:
            signed_url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": DOCUMENTS_BUCKET, "Key": key},
                ExpiresIn=2592000,
            )
        except Exception as e:
            logger.warning(f"presigned URL 生成失敗: {e}")
    docs.append({
        "documentName": uri.split("/")[-1],
        "title": meta.get("title"),
        "sourceUri": signed_url,
        "documentType": meta.get("document", "unknown"),
        "model": meta.get("model", ""),
        "relevance": float(score) if score is not None else 0.0,
    })


def build_source_documents(raw_refs: List[Dict], dynamo_citations: List[Dict] = None) -> List[Dict]:
    seen: set = set()
    docs: List[Dict] = []

    # chunk.attribution.citations 由来（直接紐付き KB）
    for ref in raw_refs:
        uri = (ref.get("location", {}).get("s3Location", {}).get("uri") or
               ref.get("metadata", {}).get("x-amz-bedrock-kb-source-uri", ""))
        _append_doc(docs, seen, uri, ref.get("metadata", {}), ref.get("score", 0.0))

    # DynamoDB 由来（action group KB: kb-search1/3 が書き込んだ引用）
    for c in (dynamo_citations or []):
        _append_doc(docs, seen, c.get("uri", ""),
                    {"title": c.get("title"), "document": c.get("document", "unknown"), "model": c.get("model", "")},
                    float(c.get("score", 0.0)))

    return docs


# ---------------------------------------------------------------------------
# レスポンス整形
# ---------------------------------------------------------------------------

def format_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, ensure_ascii=False),
    }


# ---------------------------------------------------------------------------
# Lambda ハンドラー
# ---------------------------------------------------------------------------

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        user_id = extract_user_id(event)
        body = json.loads(event["body"])
        validated = validate_input(body)
        input_text = format_agent_input(validated)

        session_id = str(uuid.uuid4())
        init_session(session_id, validated, user_id)

        agent_response = invoke_agent(input_text, session_id)
        result_text, raw_refs = parse_agent_response(agent_response)
        dynamo_citations = fetch_citations(session_id)
        source_docs = build_source_documents(raw_refs, dynamo_citations)
        save_session_result(session_id, result_text, source_docs)

        logger.info(f"Session saved: session_id={session_id}, sourceDocuments={len(source_docs)}")
        return format_response(200, {
            "sessionId": session_id,
            "result": result_text,
            "sourceDocuments": source_docs,
        })
    except ValidationError as e:
        return format_response(400, {"error": str(e)})
    except Exception as e:
        logger.error(f"Lambda error: {e}")
        return format_response(500, {"error": "内部エラー"})

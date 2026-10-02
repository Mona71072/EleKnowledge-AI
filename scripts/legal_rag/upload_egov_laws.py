from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = REPOSITORY_ROOT / "docs/features/development/legal-rag-target-laws.md"
DEFAULT_REGION = "ap-northeast-1"
FOLDER_PATTERN = re.compile(r"^([A-Z0-9]+)_(\d{8})_([A-Z0-9]+)$")
ERA_START_YEARS = {"Meiji": 1867, "Taisho": 1911, "Showa": 1925, "Heisei": 1988, "Reiwa": 2018}
MAX_SIDECAR_BYTES = 10 * 1024
MAIN_PROVISION_ANCHOR_TOKENS = {
    "Part": "Pa",
    "Chapter": "Ch",
    "Section": "Se",
    "Subsection": "Ss",
    "Division": "Di",
    "Article": "At",
}
VERIFIED_MAIN_PROVISION_PATHS = {
    ("Article",),
    ("Chapter", "Article"),
    ("Chapter", "Section", "Article"),
    ("Chapter", "Section", "Subsection", "Article"),
    ("Chapter", "Section", "Subsection", "Division", "Article"),
    ("Part", "Chapter", "Article"),
    ("Part", "Chapter", "Section", "Article"),
    ("Part", "Chapter", "Section", "Subsection", "Article"),
}


@dataclass(frozen=True)
class LawDocument:
    folder_name: str
    law_id: str
    effective_date: str
    amending_law_id: str
    law_title: str
    law_type: str
    law_number: str
    promulgation_date: str
    source_url: str
    path: Path
    content_sha256: str
    size_bytes: int

    def object_key(self, prefix: str) -> str:
        return f"{prefix}/{self.law_id}/{self.folder_name}.xml"


@dataclass(frozen=True)
class SearchDocument:
    law: LawDocument
    provision_type: str
    provision_reference: str | None
    unit_index: int
    content: str
    source_url: str | None = None

    @property
    def filename(self) -> str:
        return f"{self.unit_index:05d}.txt"

    def object_key(self, prefix: str) -> str:
        return (
            f"{prefix}/{self.law.law_id}/{self.law.folder_name}/"
            f"{self.provision_type}/{self.filename}"
        )

    def metadata_key(self, prefix: str) -> str:
        return f"{self.object_key(prefix)}.metadata.json"


def read_target_folders(catalog_path: Path) -> list[str]:
    folder_names: set[str] = set()
    for line in catalog_path.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        for cell in line.strip().strip("|").split("|"):
            value = cell.strip().strip("`")
            if FOLDER_PATTERN.fullmatch(value):
                folder_names.add(value)
    if not folder_names:
        raise ValueError(f"No law folders found in catalog: {catalog_path}")
    return sorted(folder_names)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _promulgation_date(root: ET.Element, folder_name: str) -> str:
    try:
        year = ERA_START_YEARS[root.attrib["Era"]] + int(root.attrib["Year"])
        return date(
            year,
            int(root.attrib["PromulgateMonth"]),
            int(root.attrib["PromulgateDay"]),
        ).isoformat()
    except (KeyError, ValueError) as error:
        raise ValueError(f"Invalid promulgation date in {folder_name}") from error


def build_documents(source_dir: Path, catalog_path: Path) -> list[LawDocument]:
    source_root = source_dir.resolve(strict=True)
    documents: list[LawDocument] = []
    for folder_name in read_target_folders(catalog_path):
        match = FOLDER_PATTERN.fullmatch(folder_name)
        assert match is not None
        law_id, date_value, amending_law_id = match.groups()
        effective_date = datetime.strptime(date_value, "%Y%m%d").date().isoformat()
        path = source_root / folder_name / f"{folder_name}.xml"
        resolved_path = path.resolve(strict=True)
        if not resolved_path.is_relative_to(source_root):
            raise ValueError(f"Law XML must be inside the source directory: {path}")

        try:
            root = ET.parse(resolved_path).getroot()
        except ET.ParseError as error:
            raise ValueError(f"Invalid XML for law folder {folder_name}") from error

        title = root.findtext("./LawBody/LawTitle") if root.tag == "Law" else None
        law_number = root.findtext("LawNum") if root.tag == "Law" else None
        law_type = root.attrib.get("LawType") if root.tag == "Law" else None
        if not title or not law_number or not law_type:
            raise ValueError(f"Missing law title, type, or number in {folder_name}")

        documents.append(
            LawDocument(
                folder_name=folder_name,
                law_id=law_id,
                effective_date=effective_date,
                amending_law_id=amending_law_id,
                law_title=title.strip(),
                law_type=law_type,
                law_number=law_number.strip(),
                promulgation_date=_promulgation_date(root, folder_name),
                source_url=(
                    f"https://laws.e-gov.go.jp/law/{law_id}/"
                    f"{date_value}_{amending_law_id}"
                ),
                path=resolved_path,
                content_sha256=_sha256(resolved_path),
                size_bytes=resolved_path.stat().st_size,
            )
        )
    return documents


def build_manifest(
    documents: Sequence[LawDocument], retrieved_at: str, uploaded_at: str
) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        (
            "law_id",
            "law_title",
            "law_type",
            "law_number",
            "effective_date",
            "promulgation_date",
            "amending_law_id",
            "status",
            "source_url",
            "retrieved_at",
            "uploaded_at",
            "content_sha256",
        )
    )
    for document in documents:
        writer.writerow(
            (
                document.law_id,
                document.law_title,
                document.law_type,
                document.law_number,
                document.effective_date,
                document.promulgation_date,
                document.amending_law_id,
                "current",
                document.source_url,
                retrieved_at,
                uploaded_at,
                document.content_sha256,
            )
        )
    return output.getvalue()


def _element_text(element: ET.Element) -> str:
    return re.sub(r"\s+", " ", "".join(element.itertext())).strip()


def _render_provision(
    element: ET.Element,
    document: LawDocument,
    provision_type: str,
    provision_reference: str | None = None,
    context_headings: Sequence[str] = (),
    source_url: str | None = None,
) -> str:
    labels = {
        "main": "本則",
        "supplementary": "附則",
        "transitional": "経過措置",
        "annex": "別表・様式",
    }
    lines = [
        f"【法令名】{document.law_title}",
        f"【法令ID】{document.law_id}",
        f"【施行日】{document.effective_date}",
        f"【区分】{labels[provision_type]}",
        *([f"【条文箇所】{provision_reference}"] if provision_reference else []),
        *([f"【章節】{heading}" for heading in context_headings]),
        f"【出典】{source_url or document.source_url}",
        "",
    ]
    title_tags = {
        "ArticleCaption",
        "ArticleTitle",
        "AppdxTableTitle",
        "ChapterTitle",
        "DivisionTitle",
        "PartTitle",
        "SectionTitle",
        "SubsectionTitle",
        "SupplProvisionLabel",
        "SupplProvisionArticleTitle",
        "Subitem1Title",
        "Subitem2Title",
        "Subitem3Title",
        "Subitem4Title",
        "Subitem5Title",
        "Subitem6Title",
        "Subitem7Title",
        "Subitem8Title",
        "Subitem9Title",
        "Subitem10Title",
        "TableTitle",
    }

    def visit(node: ET.Element) -> None:
        if node.tag in title_tags or node.tag == "ParagraphNum" or node.tag.endswith("Title"):
            text = _element_text(node)
            if text:
                lines.append(text)
            return
        if node.tag == "Sentence" or node.tag.endswith("Sentence"):
            text = _element_text(node)
            if text:
                lines.append(text)
            return
        if not list(node):
            text = _element_text(node)
            if text:
                lines.append(text)
            return
        for child in node:
            visit(child)

    visit(element)
    return "\n".join(lines).strip() + "\n"


def build_search_documents(document: LawDocument) -> list[SearchDocument]:
    root = ET.parse(document.path).getroot()
    law_body = root.find("LawBody") if root.tag == "Law" else None
    if law_body is None:
        raise ValueError(f"Missing LawBody in {document.folder_name}")

    main_provision = law_body.find("MainProvision")
    if main_provision is None:
        raise ValueError(f"Missing MainProvision in {document.folder_name}")

    results: list[SearchDocument] = []
    indexes: dict[str, int] = {}
    parent_by_node = {child: parent for parent in root.iter() for child in parent}
    container_titles = {
        "Part": "PartTitle",
        "Chapter": "ChapterTitle",
        "Section": "SectionTitle",
        "Subsection": "SubsectionTitle",
        "Division": "DivisionTitle",
    }

    def get_context_headings(element: ET.Element) -> list[str]:
        ancestors = []
        parent = parent_by_node.get(element)
        while parent is not None:
            ancestors.append(parent)
            parent = parent_by_node.get(parent)
        headings = []
        for ancestor in reversed(ancestors):
            expected_title = container_titles.get(ancestor.tag)
            if expected_title is None:
                continue
            title = next(
                (child for child in ancestor if child.tag == expected_title), None
            )
            if title is not None and _element_text(title):
                headings.append(_element_text(title))
        return headings

    def get_article_source_url(element: ET.Element) -> str:
        tokens = []
        tags = []
        node = element
        while node is not None and node.tag != "MainProvision":
            token = MAIN_PROVISION_ANCHOR_TOKENS.get(node.tag)
            number = node.attrib.get("Num", "")
            if token is None or not re.fullmatch(r"[0-9]+(?:_[0-9]+)*", number):
                return document.source_url
            tags.append(node.tag)
            tokens.append(f"{token}_{number}")
            node = parent_by_node.get(node)
        if node is None or tuple(reversed(tags)) not in VERIFIED_MAIN_PROVISION_PATHS:
            return document.source_url
        return f"{document.source_url}#Mp-{'-'.join(reversed(tokens))}"

    def append_document(
        element: ET.Element,
        provision_type: str,
        provision_reference: str | None,
    ) -> None:
        indexes[provision_type] = indexes.get(provision_type, 0) + 1
        source_url = (
            get_article_source_url(element)
            if provision_type == "main" and element.tag == "Article"
            else document.source_url
        )
        results.append(
            SearchDocument(
                law=document,
                provision_type=provision_type,
                provision_reference=provision_reference,
                unit_index=indexes[provision_type],
                content=_render_provision(
                    element,
                    document,
                    provision_type,
                    provision_reference,
                    context_headings=get_context_headings(element),
                    source_url=source_url,
                ),
                source_url=source_url,
            )
        )

    main_articles = list(main_provision.iter("Article"))
    for article in main_articles:
        reference = (article.findtext("ArticleTitle") or "").strip() or None
        append_document(article, "main", reference)
    if not main_articles:
        append_document(main_provision, "main", None)

    appendix_tags = {
        "Appdx",
        "AppdxTable",
        "AppdxStyle",
        "AppdxFormat",
        "AppdxNote",
        "AppdxFig",
    }
    for appendix in main_provision:
        if appendix.tag in appendix_tags:
            append_document(appendix, "annex", None)

    for provision in law_body.findall("SupplProvision"):
        headings = " ".join(
            _element_text(node)
            for node in provision.iter()
            if node.tag in {"SupplProvisionLabel", "SupplProvisionArticleTitle"}
        )
        provision_type = (
            "transitional"
            if any(term in headings for term in ("経過措置", "経過規定", "経過措置等"))
            else "supplementary"
        )
        articles = list(provision.iter("SupplProvisionArticle"))
        if articles:
            for article in articles:
                number = article.attrib.get("Num", "")
                reference = f"附則第{number.replace('_', 'の')}条" if number else None
                append_document(article, provision_type, reference)
        else:
            append_document(provision, provision_type, None)
    return results


def _metadata_attribute(value_type: str, **value: object) -> dict[str, object]:
    return {
        "value": {"type": value_type, **value},
        "includeForEmbedding": False,
    }


def build_metadata_sidecar(
    search_document: SearchDocument, retrieved_at: str, uploaded_at: str
) -> str:
    document = search_document.law
    attributes: dict[str, object] = {
        "source_type": _metadata_attribute("STRING", stringValue="law"),
        "law_id": _metadata_attribute("STRING", stringValue=document.law_id),
        "law_title": _metadata_attribute("STRING", stringValue=document.law_title),
        "law_type": _metadata_attribute("STRING", stringValue=document.law_type),
        "law_number": _metadata_attribute("STRING", stringValue=document.law_number),
        "effective_date": _metadata_attribute(
            "STRING", stringValue=document.effective_date
        ),
        "promulgation_date": _metadata_attribute(
            "STRING", stringValue=document.promulgation_date
        ),
        "amending_law_id": _metadata_attribute(
            "STRING", stringValue=document.amending_law_id
        ),
        "provision_type": _metadata_attribute(
            "STRING", stringValue=search_document.provision_type
        ),
        "document_granularity": _metadata_attribute(
            "STRING", stringValue="provision_unit"
        ),
        "status": _metadata_attribute("STRING", stringValue="current"),
        "source_url": _metadata_attribute(
            "STRING", stringValue=search_document.source_url or document.source_url
        ),
        "retrieved_at": _metadata_attribute("STRING", stringValue=retrieved_at),
        "uploaded_at": _metadata_attribute("STRING", stringValue=uploaded_at),
        "content_sha256": _metadata_attribute(
            "STRING", stringValue=document.content_sha256
        ),
    }
    if search_document.provision_reference:
        attributes["provision_reference"] = _metadata_attribute(
            "STRING", stringValue=search_document.provision_reference
        )
    if document.law_title.find("建築") >= 0:
        legal_topics = ["建築"]
    else:
        legal_topics = []
    topic_rules = (
        ("昇降機", "昇降機"),
        ("消防", "消防"),
        ("高齢者", "バリアフリー"),
        ("障害者", "バリアフリー"),
        ("円滑化", "バリアフリー"),
        ("クレーン", "クレーン"),
        ("石綿", "石綿"),
        ("電気工事", "電気工事"),
        ("電気設備", "電気工事"),
        ("廃棄物", "廃棄物"),
        ("再資源化", "廃棄物"),
        ("騒音", "騒音"),
        ("振動", "振動"),
    )
    for keyword, topic in topic_rules:
        if keyword in document.law_title and topic not in legal_topics:
            legal_topics.append(topic)
    if legal_topics:
        attributes["legal_topics"] = _metadata_attribute(
            "STRING_LIST", stringListValue=legal_topics
        )

    metadata = json.dumps(
        {"metadataAttributes": attributes},
        ensure_ascii=False,
        separators=(",", ":"),
    ) + "\n"
    if len(metadata.encode("utf-8")) > MAX_SIDECAR_BYTES:
        raise ValueError("Bedrock metadata sidecar exceeds the 10 KB limit")
    return metadata


def validate_bucket(s3_client: object, bucket: str, expected_account_id: str) -> None:
    owner = {"ExpectedBucketOwner": expected_account_id}
    s3_client.head_bucket(Bucket=bucket, **owner)

    versioning = s3_client.get_bucket_versioning(Bucket=bucket, **owner)
    if versioning.get("Status") != "Enabled":
        raise ValueError("The target bucket must have versioning enabled")

    encryption = s3_client.get_bucket_encryption(Bucket=bucket, **owner)
    algorithms = {
        rule.get("ApplyServerSideEncryptionByDefault", {}).get("SSEAlgorithm")
        for rule in encryption.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])
    }
    if "aws:kms" not in algorithms:
        raise ValueError("The target bucket must use SSE-KMS default encryption")

    public_access = s3_client.get_public_access_block(Bucket=bucket, **owner)
    settings = public_access.get("PublicAccessBlockConfiguration", {})
    required_blocks = (
        "BlockPublicAcls",
        "IgnorePublicAcls",
        "BlockPublicPolicy",
        "RestrictPublicBuckets",
    )
    if not all(settings.get(setting) is True for setting in required_blocks):
        raise ValueError("All four S3 Block Public Access settings must be enabled")

    ownership = s3_client.get_bucket_ownership_controls(Bucket=bucket, **owner)
    rules = ownership.get("OwnershipControls", {}).get("Rules", [])
    if not any(rule.get("ObjectOwnership") == "BucketOwnerEnforced" for rule in rules):
        raise ValueError("The target bucket must enforce bucket-owner object ownership")

    policy_response = s3_client.get_bucket_policy(Bucket=bucket, **owner)
    try:
        policy = json.loads(policy_response["Policy"])
    except (KeyError, json.JSONDecodeError) as error:
        raise ValueError("The target bucket must have a valid TLS-only bucket policy") from error

    statements = policy.get("Statement", [])
    if isinstance(statements, dict):
        statements = [statements]
    bucket_arn = f"arn:aws:s3:::{bucket}"
    protects_bucket = False
    for statement in statements:
        if statement.get("Effect") != "Deny":
            continue
        actions = statement.get("Action", [])
        actions = [actions] if isinstance(actions, str) else actions
        if not any(action in ("*", "s3:*") for action in actions):
            continue
        resources = statement.get("Resource", [])
        resources = [resources] if isinstance(resources, str) else resources
        if not (
            "*" in resources
            or (bucket_arn in resources and f"{bucket_arn}/*" in resources)
        ):
            continue
        condition = statement.get("Condition", {})
        transport_values = []
        for operator in ("Bool", "BoolIfExists"):
            transport_values.append(
                condition.get(operator, {}).get("aws:SecureTransport")
            )
        if any(value is False or str(value).lower() == "false" for value in transport_values):
            protects_bucket = True
            break
    if not protects_bucket:
        raise ValueError(
            "The target bucket policy must deny insecure transport for the bucket and its objects"
        )


def _legacy_aggregate_keys(documents: Sequence[LawDocument], kb_prefix: str) -> set[str]:
    return {
        f"{kb_prefix}/{document.law_id}/{document.folder_name}.{provision_type}.txt{suffix}"
        for document in documents
        for provision_type in ("main", "supplementary", "transitional")
        for suffix in ("", ".metadata.json")
    }


def prune_legacy_derived_objects(
    s3_client: object,
    bucket: str,
    documents: Sequence[LawDocument],
    *,
    kb_prefix: str,
    expected_account_id: str,
) -> list[str]:
    legacy_keys = _legacy_aggregate_keys(documents, kb_prefix)
    existing_keys = set()
    continuation_token = None
    while True:
        request = {
            "Bucket": bucket,
            "Prefix": f"{kb_prefix}/",
            "ExpectedBucketOwner": expected_account_id,
        }
        if continuation_token:
            request["ContinuationToken"] = continuation_token
        response = s3_client.list_objects_v2(**request)
        existing_keys.update(
            item["Key"] for item in response.get("Contents", [])
            if item.get("Key") in legacy_keys
        )
        if not response.get("IsTruncated"):
            break
        continuation_token = response.get("NextContinuationToken")
        if not continuation_token:
            raise ValueError("S3 returned a truncated listing without a continuation token")

    deleted = sorted(existing_keys)
    for key in deleted:
        s3_client.delete_object(
            Bucket=bucket,
            Key=key,
            ExpectedBucketOwner=expected_account_id,
        )
    return deleted


def upload_documents(
    s3_client: object,
    bucket: str,
    documents: Sequence[LawDocument],
    search_documents: Sequence[SearchDocument],
    manifest: str,
    *,
    prefix: str,
    kb_prefix: str,
    retrieved_at: str,
    uploaded_at: str,
    expected_account_id: str,
    prune_legacy_derived: bool = False,
) -> None:
    validate_bucket(s3_client, bucket, expected_account_id)
    owner = {"ExpectedBucketOwner": expected_account_id}
    for document in documents:
        s3_client.upload_file(
            str(document.path),
            bucket,
            document.object_key(prefix),
            ExtraArgs={
                "ContentType": "application/xml",
                "ExpectedBucketOwner": expected_account_id,
                "Metadata": {
                    "law-id": document.law_id,
                    "effective-date": document.effective_date,
                    "retrieved-at": retrieved_at,
                    "uploaded-at": uploaded_at,
                    "content-sha256": document.content_sha256,
                },
            },
        )
    for search_document in search_documents:
        s3_client.put_object(
            Bucket=bucket,
            Key=search_document.object_key(kb_prefix),
            Body=search_document.content.encode("utf-8"),
            ContentType="text/plain; charset=utf-8",
            **owner,
        )
        s3_client.put_object(
            Bucket=bucket,
            Key=search_document.metadata_key(kb_prefix),
            Body=build_metadata_sidecar(
                search_document, retrieved_at, uploaded_at
            ).encode("utf-8"),
            ContentType="application/json; charset=utf-8",
            **owner,
        )
    if prune_legacy_derived:
        prune_legacy_derived_objects(
            s3_client,
            bucket,
            documents,
            kb_prefix=kb_prefix,
            expected_account_id=expected_account_id,
        )
    s3_client.put_object(
        Bucket=bucket,
        Key="manifest/laws.csv",
        Body=manifest.encode("utf-8"),
        ContentType="text/csv; charset=utf-8",
        **owner,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and upload the selected e-Gov law XML files to S3."
    )
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument(
        "--retrieved-at",
        required=True,
        help="Date the source XML was downloaded (YYYY-MM-DD); not the upload time",
    )
    parser.add_argument("--bucket")
    parser.add_argument("--prefix", default="raw/egov")
    parser.add_argument("--kb-prefix", default="kb/egov")
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--profile")
    parser.add_argument("--expected-account-id")
    parser.add_argument("--upload", action="store_true", help="Perform S3 writes")
    parser.add_argument(
        "--prune-legacy-derived",
        action="store_true",
        help="Delete only known pre-article aggregate TXT/sidecar keys after upload",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.upload and (not args.bucket or not args.expected_account_id):
        parser.error("--upload requires --bucket and --expected-account-id")
    if args.prune_legacy_derived and not args.upload:
        parser.error("--prune-legacy-derived requires --upload")
    if args.expected_account_id and not re.fullmatch(r"\d{12}", args.expected_account_id):
        parser.error("--expected-account-id must be a 12-digit AWS account ID")
    try:
        retrieved_at = date.fromisoformat(args.retrieved_at).isoformat()
    except ValueError:
        parser.error("--retrieved-at must be an ISO date (YYYY-MM-DD)")
    prefix = args.prefix.strip("/")
    kb_prefix = args.kb_prefix.strip("/")
    for name, value in (("--prefix", prefix), ("--kb-prefix", kb_prefix)):
        if not value or any(part in {".", ".."} for part in value.split("/")):
            parser.error(f"{name} must be a non-empty S3 key prefix without dot segments")
    if prefix == kb_prefix or prefix.startswith(f"{kb_prefix}/") or kb_prefix.startswith(f"{prefix}/"):
        parser.error("--prefix and --kb-prefix must be separate, non-overlapping paths")

    try:
        documents = build_documents(args.source_dir, args.catalog)
        uploaded_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        )
        search_documents = [
            search_document
            for document in documents
            for search_document in build_search_documents(document)
        ]
        manifest = build_manifest(documents, retrieved_at, uploaded_at)
        total_bytes = sum(document.size_bytes for document in documents)
        if not args.upload:
            derived_bytes = sum(
                len(search_document.content.encode("utf-8"))
                for search_document in search_documents
            )
            print(
                f"Validated {len(documents)} law XML files ({total_bytes} bytes) and "
                f"{len(search_documents)} derived search documents ({derived_bytes} bytes); "
                f"dry run, no S3 writes. Prefixes: {prefix}/, {kb_prefix}/"
            )
            return 0

        session = boto3.Session(profile_name=args.profile, region_name=args.region)
        identity = session.client("sts").get_caller_identity()
        if identity.get("Account") != args.expected_account_id:
            print("Active AWS account does not match --expected-account-id; no upload performed.", file=sys.stderr)
            return 2

        s3_client = session.client("s3")
        upload_documents(
            s3_client,
            args.bucket,
            documents,
            search_documents,
            manifest,
            prefix=prefix,
            kb_prefix=kb_prefix,
            retrieved_at=retrieved_at,
            uploaded_at=uploaded_at,
            expected_account_id=args.expected_account_id,
            prune_legacy_derived=args.prune_legacy_derived,
        )
        print(
            f"Uploaded {len(documents)} law XML files, {len(search_documents)} "
            f"search documents and sidecars, and manifest/laws.csv "
            f"({total_bytes} XML bytes) to s3://{args.bucket}/"
        )
        return 0
    except (OSError, ValueError, ET.ParseError) as error:
        print(f"Input validation failed: {error}", file=sys.stderr)
        return 2
    except ClientError as error:
        code = error.response.get("Error", {}).get("Code", "Unknown")
        print(f"AWS request failed: {code}; no manifest was written after this failure.", file=sys.stderr)
        return 2
    except BotoCoreError as error:
        print(f"AWS client failed: {type(error).__name__}; no manifest was written.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
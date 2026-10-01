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
    content: str

    @property
    def filename(self) -> str:
        return f"{self.law.folder_name}.{self.provision_type}.txt"

    def object_key(self, prefix: str) -> str:
        return f"{prefix}/{self.law.law_id}/{self.filename}"

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


def build_manifest(documents: Sequence[LawDocument], retrieved_at: str) -> str:
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
                document.content_sha256,
            )
        )
    return output.getvalue()


def _element_text(element: ET.Element) -> str:
    return re.sub(r"\s+", " ", "".join(element.itertext())).strip()


def _render_provision(element: ET.Element, document: LawDocument, provision_type: str) -> str:
    labels = {
        "main": "本則",
        "supplementary": "附則",
        "transitional": "経過措置",
    }
    lines = [
        f"【法令名】{document.law_title}",
        f"【法令ID】{document.law_id}",
        f"【施行日】{document.effective_date}",
        f"【区分】{labels[provision_type]}",
        f"【出典】{document.source_url}",
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
        if node.tag in {"Article", "SupplProvisionArticle"}:
            number = node.attrib.get("Num", "")
            if number:
                lines.append(f"第{number.replace('_', 'の')}条")
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

    results = [
        SearchDocument(
            law=document,
            provision_type="main",
            content=_render_provision(main_provision, document, "main"),
        )
    ]
    supplementary: dict[str, list[ET.Element]] = {"supplementary": [], "transitional": []}
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
        supplementary[provision_type].append(provision)

    for provision_type, provisions in supplementary.items():
        if not provisions:
            continue
        content = "\n".join(
            _render_provision(provision, document, provision_type).strip()
            for provision in provisions
        )
        results.append(
            SearchDocument(law=document, provision_type=provision_type, content=content + "\n")
        )
    return results


def _metadata_attribute(value_type: str, **value: object) -> dict[str, object]:
    return {
        "value": {"type": value_type, **value},
        "includeForEmbedding": False,
    }


def build_metadata_sidecar(
    search_document: SearchDocument, retrieved_at: str
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
        "status": _metadata_attribute("STRING", stringValue="current"),
        "source_url": _metadata_attribute("STRING", stringValue=document.source_url),
        "retrieved_at": _metadata_attribute("STRING", stringValue=retrieved_at),
        "content_sha256": _metadata_attribute(
            "STRING", stringValue=document.content_sha256
        ),
    }
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

    metadata = {"metadataAttributes": attributes}
    return json.dumps(metadata, ensure_ascii=False, separators=(",", ":")) + "\n"


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
    expected_account_id: str,
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
            Body=build_metadata_sidecar(search_document, retrieved_at).encode("utf-8"),
            ContentType="application/json; charset=utf-8",
            **owner,
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
    parser.add_argument("--bucket")
    parser.add_argument("--prefix", default="raw/egov")
    parser.add_argument("--kb-prefix", default="kb/egov")
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--profile")
    parser.add_argument("--expected-account-id")
    parser.add_argument("--upload", action="store_true", help="Perform S3 writes")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.upload and (not args.bucket or not args.expected_account_id):
        parser.error("--upload requires --bucket and --expected-account-id")
    if args.expected_account_id and not re.fullmatch(r"\d{12}", args.expected_account_id):
        parser.error("--expected-account-id must be a 12-digit AWS account ID")
    prefix = args.prefix.strip("/")
    kb_prefix = args.kb_prefix.strip("/")
    for name, value in (("--prefix", prefix), ("--kb-prefix", kb_prefix)):
        if not value or any(part in {".", ".."} for part in value.split("/")):
            parser.error(f"{name} must be a non-empty S3 key prefix without dot segments")
    if prefix == kb_prefix or prefix.startswith(f"{kb_prefix}/") or kb_prefix.startswith(f"{prefix}/"):
        parser.error("--prefix and --kb-prefix must be separate, non-overlapping paths")

    try:
        documents = build_documents(args.source_dir, args.catalog)
        retrieved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        search_documents = [
            search_document
            for document in documents
            for search_document in build_search_documents(document)
        ]
        manifest = build_manifest(documents, retrieved_at)
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
            expected_account_id=args.expected_account_id,
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
import json
import csv
import hashlib
from pathlib import Path

import pytest

from scripts.legal_rag.upload_egov_laws import (
    build_documents,
    build_manifest,
    build_metadata_sidecar,
    build_search_documents,
    upload_documents,
)


FOLDER_NAME = "322AC0000000049_20260717_508AC0000000060"
ACCOUNT_ID = "123456789012"


def _write_fixture(tmp_path: Path, *, xml: str | None = None) -> tuple[Path, Path, bytes]:
    source_dir = tmp_path / "all_xml"
    law_dir = source_dir / FOLDER_NAME
    law_dir.mkdir(parents=True)
    xml_bytes = (xml or """<?xml version="1.0" encoding="UTF-8"?>
<Law Lang="ja" Era="Showa" Year="22" PromulgateMonth="4" PromulgateDay="7" LawType="Act"><LawNum>昭和二十二年法律第四十九号</LawNum>
    <LawBody><LawTitle>労働基準法</LawTitle>
        <MainProvision><Article Num="1"><ArticleTitle>（目的）</ArticleTitle>
            <Paragraph Num="1"><ParagraphNum>１</ParagraphNum>
                <ParagraphSentence><Sentence>この法律は、労働条件を定める。</Sentence></ParagraphSentence>
            </Paragraph>
        </Article></MainProvision>
    </LawBody>
</Law>""").encode("utf-8")
    (law_dir / f"{FOLDER_NAME}.xml").write_bytes(xml_bytes)
    catalog = tmp_path / "catalog.md"
    catalog.write_text(
        f"| 法令名 | フォルダ名 |\n|---|---|\n| 労働基準法 | `{FOLDER_NAME}` |\n",
        encoding="utf-8",
    )
    return source_dir, catalog, xml_bytes


def test_build_documents_extracts_metadata_and_hash(tmp_path: Path) -> None:
    source_dir, catalog, xml_bytes = _write_fixture(tmp_path)

    documents = build_documents(source_dir, catalog)

    assert len(documents) == 1
    document = documents[0]
    assert document.law_id == "322AC0000000049"
    assert document.effective_date == "2026-07-17"
    assert document.amending_law_id == "508AC0000000060"
    assert document.law_title == "労働基準法"
    assert document.law_type == "Act"
    assert document.promulgation_date == "1947-04-07"
    assert document.source_url.endswith("/20260717_508AC0000000060")
    assert document.content_sha256 == hashlib.sha256(xml_bytes).hexdigest()
    assert document.object_key("raw/egov") == f"raw/egov/{document.law_id}/{FOLDER_NAME}.xml"


def test_build_documents_rejects_malformed_xml(tmp_path: Path) -> None:
    source_dir, catalog, _ = _write_fixture(tmp_path, xml="<Law>")

    with pytest.raises(ValueError, match="Invalid XML"):
        build_documents(source_dir, catalog)


def test_build_search_documents_preserves_provision_structure(tmp_path: Path) -> None:
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<Law Lang="ja" Era="Showa" Year="22" PromulgateMonth="4" PromulgateDay="7" LawType="Act"><LawNum>法律第四十九号</LawNum>
    <LawBody><LawTitle>労働基準法</LawTitle>
        <MainProvision><Chapter Num="1"><ChapterTitle>第一章 総則</ChapterTitle>
            <Article Num="1"><ArticleTitle>（目的）</ArticleTitle>
                <Paragraph Num="1"><ParagraphNum>１</ParagraphNum>
                    <ParagraphSentence><Sentence>この法律は、労働条件を定める。</Sentence></ParagraphSentence>
                    <Item Num="1"><ItemTitle>一</ItemTitle>
                        <ItemSentence><Sentence>安全を確保する。</Sentence></ItemSentence></Item>
                </Paragraph>
            </Article>
        </Chapter></MainProvision>
        <SupplProvision><SupplProvisionLabel>附則</SupplProvisionLabel>
            <SupplProvisionArticle Num="1"><SupplProvisionArticleTitle>（施行期日）</SupplProvisionArticleTitle>
                <Paragraph><ParagraphSentence><Sentence>この法律は公布の日から施行する。</Sentence></ParagraphSentence></Paragraph>
            </SupplProvisionArticle>
        </SupplProvision>
    </LawBody>
</Law>"""
        source_dir, catalog, _ = _write_fixture(tmp_path, xml=xml)
        document = build_documents(source_dir, catalog)[0]

        search_documents = build_search_documents(document)

        assert [search.provision_type for search in search_documents] == ["main", "supplementary"]
        assert "第一章 総則" in search_documents[0].content
        assert "第1条" in search_documents[0].content
        assert "この法律は、労働条件を定める。" in search_documents[0].content
        assert "安全を確保する。" in search_documents[0].content
        assert "この法律は公布の日から施行する。" in search_documents[1].content


def test_metadata_sidecar_contains_typed_bedrock_attributes(tmp_path: Path) -> None:
        source_dir, catalog, _ = _write_fixture(tmp_path)
        document = build_documents(source_dir, catalog)[0]
        search_document = build_search_documents(document)[0]

        metadata = json.loads(
                build_metadata_sidecar(search_document, "2026-10-01T00:00:00+00:00")
        )

        attributes = metadata["metadataAttributes"]
        assert attributes["source_type"]["value"] == {"type": "STRING", "stringValue": "law"}
        assert attributes["provision_type"]["value"]["stringValue"] == "main"
        assert attributes["law_id"]["value"]["stringValue"] == "322AC0000000049"
        assert attributes["promulgation_date"]["value"]["stringValue"] == "1947-04-07"


class _S3Client:
    def __init__(self, *, public_access: bool = True) -> None:
        self.public_access = public_access
        self.uploads: list[tuple[str, str, str, dict[str, object]]] = []
        self.objects: list[dict[str, object]] = []
        self.manifest: dict[str, object] | None = None

    def head_bucket(self, **kwargs: object) -> dict[str, object]:
        return {}

    def get_bucket_versioning(self, **kwargs: object) -> dict[str, object]:
        return {"Status": "Enabled"}

    def get_bucket_encryption(self, **kwargs: object) -> dict[str, object]:
        return {
            "ServerSideEncryptionConfiguration": {
                "Rules": [
                    {"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms"}}
                ]
            }
        }

    def get_public_access_block(self, **kwargs: object) -> dict[str, object]:
        return {
            "PublicAccessBlockConfiguration": {
                setting: self.public_access
                for setting in (
                    "BlockPublicAcls",
                    "IgnorePublicAcls",
                    "BlockPublicPolicy",
                    "RestrictPublicBuckets",
                )
            }
        }

    def get_bucket_ownership_controls(self, **kwargs: object) -> dict[str, object]:
        return {"OwnershipControls": {"Rules": [{"ObjectOwnership": "BucketOwnerEnforced"}]}}

    def upload_file(
        self,
        filename: str,
        bucket: str,
        key: str,
        *,
        ExtraArgs: dict[str, object],
    ) -> None:
        self.uploads.append((filename, bucket, key, ExtraArgs))

    def put_object(self, **kwargs: object) -> None:
        self.objects.append(kwargs)
        if kwargs.get("Key") == "manifest/laws.csv":
            self.manifest = kwargs


def test_upload_documents_writes_xml_then_manifest(tmp_path: Path) -> None:
    source_dir, catalog, _ = _write_fixture(tmp_path)
    documents = build_documents(source_dir, catalog)
    search_documents = [
        search_document
        for document in documents
        for search_document in build_search_documents(document)
    ]
    manifest = build_manifest(documents, "2026-10-01T00:00:00Z")
    s3_client = _S3Client()

    upload_documents(
        s3_client,
        "law-rag-test",
        documents,
        search_documents,
        manifest,
        prefix="raw/egov",
        kb_prefix="kb/egov",
        retrieved_at="2026-10-01T00:00:00Z",
        expected_account_id=ACCOUNT_ID,
    )

    assert len(s3_client.uploads) == 1
    assert s3_client.uploads[0][2] == documents[0].object_key("raw/egov")
    assert s3_client.uploads[0][3]["ContentType"] == "application/xml"
    assert any(item["Key"] == search_documents[0].object_key("kb/egov") for item in s3_client.objects)
    assert any(item["Key"] == search_documents[0].metadata_key("kb/egov") for item in s3_client.objects)
    assert s3_client.manifest is not None
    assert s3_client.manifest["Body"].decode("utf-8") == manifest
    assert "労働基準法" in next(csv.DictReader(manifest.splitlines()))["law_title"]
    assert next(csv.DictReader(manifest.splitlines()))["promulgation_date"] == "1947-04-07"


def test_upload_documents_refuses_public_bucket_before_writing(tmp_path: Path) -> None:
    source_dir, catalog, _ = _write_fixture(tmp_path)
    documents = build_documents(source_dir, catalog)
    s3_client = _S3Client(public_access=False)

    with pytest.raises(ValueError, match="Block Public Access"):
        upload_documents(
            s3_client,
            "law-rag-test",
            documents,
            [],
            "manifest",
            prefix="raw/egov",
            kb_prefix="kb/egov",
            retrieved_at="2026-10-01T00:00:00Z",
            expected_account_id=ACCOUNT_ID,
        )

    assert not s3_client.uploads
    assert s3_client.manifest is None
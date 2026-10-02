import json
import csv
import hashlib
import xml.etree.ElementTree as ET
from dataclasses import replace
from pathlib import Path

import pytest

from scripts.legal_rag.upload_egov_laws import (
    build_documents,
    build_manifest,
    build_metadata_sidecar,
    build_search_documents,
    upload_documents,
)



def test_metadata_sidecar_rejects_more_than_ten_kilobytes(tmp_path: Path) -> None:
    source_dir, catalog, _ = _write_fixture(tmp_path)
    document = build_documents(source_dir, catalog)[0]
    search_document = build_search_documents(document)[0]
    oversized_law = replace(search_document.law, law_title="法" * 12000)
    oversized_document = replace(search_document, law=oversized_law)

    with pytest.raises(ValueError, match="10 KB limit"):
        build_metadata_sidecar(
            oversized_document, "2026-10-01", "2026-10-02T00:00:00Z"
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
        <MainProvision><Article Num="1"><ArticleCaption>（目的）</ArticleCaption><ArticleTitle>第一条</ArticleTitle>
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
            <Article Num="1"><ArticleCaption>（目的）</ArticleCaption><ArticleTitle>第一条</ArticleTitle>
                <Paragraph Num="1"><ParagraphNum>１</ParagraphNum>
                    <ParagraphSentence><Sentence>この法律は、労働条件を定める。</Sentence></ParagraphSentence>
                    <Item Num="1"><ItemTitle>一</ItemTitle>
                        <ItemSentence><Sentence>安全を確保する。</Sentence></ItemSentence></Item>
                </Paragraph>
            </Article>
            <Article Num="2"><ArticleCaption>（定義）</ArticleCaption><ArticleTitle>第二条</ArticleTitle>
                <Paragraph Num="1"><ParagraphNum>１</ParagraphNum>
                    <ParagraphSentence><Sentence>労働者とは、事業に使用される者をいう。</Sentence></ParagraphSentence>
                </Paragraph>
            </Article>
        </Chapter>
        <AppdxTable><AppdxTableTitle>別表第一</AppdxTableTitle>
            <TableStruct><Table><TableRow><TableColumn>
                <Sentence>別表の安全基準。</Sentence>
            </TableColumn></TableRow></Table></TableStruct>
        </AppdxTable></MainProvision>
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

        assert [search.provision_type for search in search_documents] == [
            "main", "main", "annex", "supplementary"
        ]
        assert [search.provision_reference for search in search_documents] == [
            "第一条", "第二条", None, "附則第1条"
        ]
        assert search_documents[0].object_key("kb/egov").endswith(
            f"/{FOLDER_NAME}/main/00001.txt"
        )
        assert "【章節】第一章 総則" in search_documents[0].content
        assert "第一条" in search_documents[0].content
        assert "（目的）" in search_documents[0].content
        assert "この法律は、労働条件を定める。" in search_documents[0].content
        assert "安全を確保する。" in search_documents[0].content
        assert "第二条" in search_documents[1].content
        assert "別表第一" in search_documents[2].content
        assert "別表の安全基準。" in search_documents[2].content
        assert "この法律は公布の日から施行する。" in search_documents[3].content
        for search_document in search_documents[2:]:
            assert search_document.source_url == document.source_url
            attributes = json.loads(build_metadata_sidecar(
                search_document, "2026-10-01", "2026-10-02T00:00:00Z"
            ))["metadataAttributes"]
            assert attributes["source_url"]["value"]["stringValue"] == document.source_url


def _write_nested_article_fixture(
    tmp_path: Path,
    ancestors: list[tuple[str, str | None]],
    *,
    article_number: str | None = "129_13_3",
    article_title: str | None = "第百二十九条の十三の三",
) -> tuple[Path, Path]:
    source_dir, catalog, xml_bytes = _write_fixture(tmp_path)
    root = ET.fromstring(xml_bytes)
    main = root.find("./LawBody/MainProvision")
    assert main is not None
    article = main.find("Article")
    assert article is not None
    main.remove(article)
    parent = main
    for tag, number in ancestors:
        parent = ET.SubElement(parent, tag)
        if number is not None:
            parent.set("Num", number)
    if article_number is None:
        article.attrib.pop("Num", None)
    else:
        article.set("Num", article_number)
    title = article.find("ArticleTitle")
    assert title is not None
    title.text = article_title
    parent.append(article)
    (source_dir / FOLDER_NAME / f"{FOLDER_NAME}.xml").write_bytes(
        ET.tostring(root, encoding="utf-8")
    )
    return source_dir, catalog


@pytest.mark.parametrize("ancestors, fragment", [
    ([], "Mp-At_129_13_3"),
    ([("Chapter", "5_4")], "Mp-Ch_5_4-At_129_13_3"),
    ([("Chapter", "5_4"), ("Section", "2")], "Mp-Ch_5_4-Se_2-At_129_13_3"),
    ([("Chapter", "5_4"), ("Section", "2"), ("Subsection", "1")], "Mp-Ch_5_4-Se_2-Ss_1-At_129_13_3"),
    ([("Chapter", "5_4"), ("Section", "2"), ("Subsection", "1"), ("Division", "1")], "Mp-Ch_5_4-Se_2-Ss_1-Di_1-At_129_13_3"),
    ([("Part", "1"), ("Chapter", "5_4")], "Mp-Pa_1-Ch_5_4-At_129_13_3"),
    ([("Part", "1"), ("Chapter", "5_4"), ("Section", "2")], "Mp-Pa_1-Ch_5_4-Se_2-At_129_13_3"),
    ([("Part", "1"), ("Chapter", "5_4"), ("Section", "2"), ("Subsection", "1")], "Mp-Pa_1-Ch_5_4-Se_2-Ss_1-At_129_13_3"),
])
def test_main_article_links_use_verified_hierarchy_and_xml_title(tmp_path, ancestors, fragment):
    source_dir, catalog = _write_nested_article_fixture(tmp_path, ancestors)
    document = build_documents(source_dir, catalog)[0]
    search_document = build_search_documents(document)[0]
    expected_url = f"{document.source_url}#{fragment}"

    assert search_document.source_url == expected_url
    assert search_document.provision_reference == "第百二十九条の十三の三"
    assert f"【出典】{expected_url}" in search_document.content
    assert "【条文箇所】第百二十九条の十三の三" in search_document.content
    assert "第129の13の3条" not in search_document.content
    attributes = json.loads(build_metadata_sidecar(
        search_document, "2026-10-01", "2026-10-02T00:00:00Z"
    ))["metadataAttributes"]
    assert attributes["source_url"]["value"]["stringValue"] == expected_url
    assert attributes["provision_reference"]["value"]["stringValue"] == "第百二十九条の十三の三"


@pytest.mark.parametrize("ancestors, article_number", [
    ([("Unknown", "1")], "129_13_3"),
    ([("Chapter", None)], "129_13_3"),
    ([("Chapter", "invalid")], "129_13_3"),
    ([], None),
    ([], "129/13"),
    ([], "129#13"),
    ([("Part", "1"), ("Chapter", "1"), ("Section", "1"), ("Subsection", "1"), ("Division", "1")], "129_13_3"),
])
def test_unverified_main_article_links_fall_back_to_version_url(tmp_path, ancestors, article_number):
    source_dir, catalog = _write_nested_article_fixture(
        tmp_path, ancestors, article_number=article_number
    )
    document = build_documents(source_dir, catalog)[0]
    search_document = build_search_documents(document)[0]

    assert search_document.source_url == document.source_url
    assert f"【出典】{document.source_url}\n" in search_document.content
    attributes = json.loads(build_metadata_sidecar(
        search_document, "2026-10-01", "2026-10-02T00:00:00Z"
    ))["metadataAttributes"]
    assert attributes["source_url"]["value"]["stringValue"] == document.source_url


@pytest.mark.parametrize("article_number, article_title", [
    ("29:31", "第二十九条から第三十一条まで"),
    ("16_43:16_45", "第十六条の四十三から第十六条の四十五まで"),
])
def test_article_ranges_keep_xml_title_and_fall_back_to_whole_law(tmp_path, article_number, article_title):
    source_dir, catalog = _write_nested_article_fixture(
        tmp_path, [("Chapter", "1")],
        article_number=article_number, article_title=article_title,
    )
    document = build_documents(source_dir, catalog)[0]
    search_document = build_search_documents(document)[0]

    assert search_document.source_url == document.source_url
    assert search_document.provision_reference == article_title
    attributes = json.loads(build_metadata_sidecar(
        search_document, "2026-10-01", "2026-10-02T00:00:00Z"
    ))["metadataAttributes"]
    assert attributes["source_url"]["value"]["stringValue"] == document.source_url
    assert attributes["provision_reference"]["value"]["stringValue"] == article_title


def test_main_article_missing_title_does_not_invent_reference(tmp_path):
    source_dir, catalog = _write_nested_article_fixture(tmp_path, [], article_title=None)
    document = build_documents(source_dir, catalog)[0]
    search_document = build_search_documents(document)[0]

    assert search_document.provision_reference is None
    assert "【条文箇所】" not in search_document.content
    assert "第129の13の3条" not in search_document.content
    attributes = json.loads(build_metadata_sidecar(
        search_document, "2026-10-01", "2026-10-02T00:00:00Z"
    ))["metadataAttributes"]
    assert "provision_reference" not in attributes


@pytest.mark.parametrize("label, provision_type", [
    ("附則", "supplementary"),
    ("附則（経過措置）", "transitional"),
])
def test_supplementary_links_do_not_use_main_article_anchors(tmp_path, label, provision_type):
    source_dir, catalog, xml_bytes = _write_fixture(tmp_path)
    root = ET.fromstring(xml_bytes)
    law_body = root.find("LawBody")
    assert law_body is not None
    supplementary = ET.SubElement(law_body, "SupplProvision")
    ET.SubElement(supplementary, "SupplProvisionLabel").text = label
    article = ET.SubElement(supplementary, "SupplProvisionArticle", Num="1")
    ET.SubElement(article, "SupplProvisionArticleTitle").text = "第一条"
    (source_dir / FOLDER_NAME / f"{FOLDER_NAME}.xml").write_bytes(
        ET.tostring(root, encoding="utf-8")
    )
    document = build_documents(source_dir, catalog)[0]
    search_document = build_search_documents(document)[-1]

    assert search_document.provision_type == provision_type
    assert search_document.source_url == document.source_url
    attributes = json.loads(build_metadata_sidecar(
        search_document, "2026-10-01", "2026-10-02T00:00:00Z"
    ))["metadataAttributes"]
    assert attributes["source_url"]["value"]["stringValue"] == document.source_url


def test_metadata_sidecar_contains_typed_bedrock_attributes(tmp_path: Path) -> None:
        source_dir, catalog, _ = _write_fixture(tmp_path)
        document = build_documents(source_dir, catalog)[0]
        search_document = build_search_documents(document)[0]

        metadata = json.loads(
            build_metadata_sidecar(
                search_document, "2026-10-01", "2026-10-02T00:00:00Z"
            )
        )

        attributes = metadata["metadataAttributes"]
        assert attributes["source_type"]["value"] == {"type": "STRING", "stringValue": "law"}
        assert attributes["provision_type"]["value"]["stringValue"] == "main"
        assert attributes["document_granularity"]["value"]["stringValue"] == "provision_unit"
        assert attributes["law_id"]["value"]["stringValue"] == "322AC0000000049"
        assert attributes["promulgation_date"]["value"]["stringValue"] == "1947-04-07"
        assert attributes["provision_reference"]["value"]["stringValue"] == "第一条"
        assert attributes["source_url"]["value"]["stringValue"] == f"{document.source_url}#Mp-At_1"
        assert attributes["retrieved_at"]["value"]["stringValue"] == "2026-10-01"
        assert attributes["uploaded_at"]["value"]["stringValue"] == "2026-10-02T00:00:00Z"


def test_metadata_sidecar_rejects_more_than_ten_kilobytes(tmp_path: Path) -> None:
    source_dir, catalog, _ = _write_fixture(tmp_path)
    document = build_documents(source_dir, catalog)[0]
    search_document = build_search_documents(document)[0]
    oversized_law = replace(search_document.law, law_title="法" * 12000)
    oversized_document = replace(search_document, law=oversized_law)

    with pytest.raises(ValueError, match="10 KB limit"):
        build_metadata_sidecar(
            oversized_document, "2026-10-01", "2026-10-02T00:00:00Z"
        )


class _S3Client:
    def __init__(
        self,
        *,
        public_access: bool = True,
        https_policy: bool = True,
        existing_keys: list[str] | None = None,
    ) -> None:
        self.public_access = public_access
        self.https_policy = https_policy
        self.existing_keys = existing_keys or []
        self.uploads: list[tuple[str, str, str, dict[str, object]]] = []
        self.objects: list[dict[str, object]] = []
        self.deleted_keys: list[str] = []
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

    def get_bucket_policy(self, **kwargs: object) -> dict[str, str]:
        statements = []
        if self.https_policy:
            bucket = kwargs["Bucket"]
            bucket_arn = f"arn:aws:s3:::{bucket}"
            statements.append({
                "Effect": "Deny",
                "Action": "s3:*",
                "Resource": [bucket_arn, f"{bucket_arn}/*"],
                "Condition": {"Bool": {"aws:SecureTransport": "false"}},
            })
        return {"Policy": json.dumps({"Statement": statements})}

    def list_objects_v2(self, **kwargs: object) -> dict[str, object]:
        prefix = str(kwargs["Prefix"])
        return {
            "Contents": [{"Key": key} for key in self.existing_keys if key.startswith(prefix)],
            "IsTruncated": False,
        }

    def delete_object(self, **kwargs: object) -> None:
        self.deleted_keys.append(str(kwargs["Key"]))

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
    manifest = build_manifest(documents, "2026-10-01", "2026-10-02T00:00:00Z")
    s3_client = _S3Client()

    upload_documents(
        s3_client,
        "law-rag-test",
        documents,
        search_documents,
        manifest,
        prefix="raw/egov",
        kb_prefix="kb/egov",
        retrieved_at="2026-10-01",
        uploaded_at="2026-10-02T00:00:00Z",
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
    manifest_row = next(csv.DictReader(manifest.splitlines()))
    assert manifest_row["retrieved_at"] == "2026-10-01"
    assert manifest_row["uploaded_at"] == "2026-10-02T00:00:00Z"


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
            retrieved_at="2026-10-01",
            uploaded_at="2026-10-02T00:00:00Z",
            expected_account_id=ACCOUNT_ID,
        )

    assert not s3_client.uploads
    assert s3_client.manifest is None


def test_upload_documents_refuses_bucket_without_tls_policy(tmp_path: Path) -> None:
    source_dir, catalog, _ = _write_fixture(tmp_path)
    documents = build_documents(source_dir, catalog)
    s3_client = _S3Client(https_policy=False)

    with pytest.raises(ValueError, match="deny insecure transport"):
        upload_documents(
            s3_client,
            "law-rag-test",
            documents,
            [],
            "manifest",
            prefix="raw/egov",
            kb_prefix="kb/egov",
            retrieved_at="2026-10-01",
            uploaded_at="2026-10-02T00:00:00Z",
            expected_account_id=ACCOUNT_ID,
        )

    assert not s3_client.uploads
    assert s3_client.manifest is None


def test_upload_documents_prunes_only_known_legacy_aggregate_files(tmp_path: Path) -> None:
    source_dir, catalog, _ = _write_fixture(tmp_path)
    documents = build_documents(source_dir, catalog)
    folder = documents[0].folder_name
    law_id = documents[0].law_id
    legacy_main = f"kb/egov/{law_id}/{folder}.main.txt"
    legacy_main_metadata = f"{legacy_main}.metadata.json"
    legacy_supplementary = f"kb/egov/{law_id}/{folder}.supplementary.txt"
    unrelated = f"kb/egov/{law_id}/manual-notes.txt"
    s3_client = _S3Client(
        existing_keys=[legacy_main, legacy_main_metadata, legacy_supplementary, unrelated]
    )
    search_documents = [
        item for law in documents for item in build_search_documents(law)
    ]

    upload_documents(
        s3_client,
        "law-rag-test",
        documents,
        search_documents,
        "manifest",
        prefix="raw/egov",
        kb_prefix="kb/egov",
        retrieved_at="2026-10-01",
        uploaded_at="2026-10-02T00:00:00Z",
        expected_account_id=ACCOUNT_ID,
        prune_legacy_derived=True,
    )

    assert set(s3_client.deleted_keys) == {
        legacy_main, legacy_main_metadata, legacy_supplementary,
    }
    assert unrelated not in s3_client.deleted_keys
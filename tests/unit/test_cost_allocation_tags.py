"""Guard against cross-project changes and destructive tagging plans."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "cost_tags", ROOT / "scripts/ops/apply_cost_allocation_tags.py"
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class CostTagSafetyTests(unittest.TestCase):
    def resource(self):
        return {
            "arn": "arn:aws:lambda:ap-northeast-1:123456789012:function:rag-dev",
            "before": {"Project": "EleKnowledge", "Env": "dev"},
            "desired": MOD.desired_tags("rag", "shared", "development"),
        }

    def test_other_account_rejected(self):
        with self.assertRaises(ValueError):
            MOD.validate_resource(self.resource(), "999999999999")

    def test_other_project_rejected(self):
        resource = self.resource()
        resource["before"]["Project"] = "OtherProject"
        with self.assertRaises(ValueError):
            MOD.validate_resource(resource, "123456789012")

    def test_existing_classification_not_overwritten(self):
        resource = self.resource()
        resource["before"]["gyoumu012Usage"] = "user"
        with self.assertRaises(ValueError):
            MOD.validate_resource(resource, "123456789012")

    def test_only_three_cost_keys_accepted(self):
        resource = self.resource()
        resource["desired"]["Env"] = "prd"
        with self.assertRaises(ValueError):
            MOD.validate_resource(resource, "123456789012")

    def test_stack_and_stream_excluded(self):
        for arn in (
            "arn:aws:cloudformation:ap-northeast-1:123456789012:stack/example/id",
            "arn:aws:dynamodb:ap-northeast-1:123456789012:table/chatlogs-dev/stream/id",
        ):
            resource = self.resource()
            resource["arn"] = arn
            with self.assertRaises(ValueError):
                MOD.validate_resource(resource, "123456789012")

    def test_dev_resource_name_does_not_imply_development_usage(self):
        resource = self.resource()
        MOD.validate_resource(resource, "123456789012")
        self.assertEqual(resource["desired"]["gyoumu012Usage"], "shared")

    def test_monitoring_alarm_stays_monitoring(self):
        self.assertEqual(MOD.component_for(
            "arn:aws:cloudwatch:ap-northeast-1:123456789012:alarm:rag-errors",
            {"aws:cloudformation:stack-name": "troubleshooting-dev"},
        ), "monitoring")

    def test_tables_without_stack_tags_keep_functional_classification(self):
        self.assertEqual(MOD.component_for(
            "arn:aws:dynamodb:ap-northeast-1:123456789012:table/sessions-dev",
            {"Project": "EleKnowledge"},
        ), "troubleshooting")

    def test_legal_bucket_legacy_project_value_supported(self):
        resource = self.resource()
        resource["before"]["Project"] = "EleKnowledge-AI"
        resource["desired"] = MOD.desired_tags("legal-rag", "shared", "development")
        MOD.validate_resource(resource, "123456789012")
        self.assertEqual(resource["desired"]["gyoumu012Usage"], "development")

    def test_new_project_key_sufficient_for_migrated_resources(self):
        resource = self.resource()
        resource["before"] = {"gyoumu012Project": "ele-knowledge"}
        MOD.validate_resource(resource, "123456789012")

    def test_new_key_cannot_override_conflicting_project_ownership(self):
        resource = self.resource()
        resource["before"] = {
            "Project": "OtherProject", "gyoumu012Project": "ele-knowledge",
        }
        with self.assertRaises(ValueError):
            MOD.validate_resource(resource, "123456789012")

    def test_knowledge_base_uses_agent_api_tag_map(self):
        session = Mock()
        client = session.client.return_value
        client.list_tags_for_resource.return_value = {
            "tags": {"gyoumu012Project": "ele-knowledge"},
        }
        arn = "arn:aws:bedrock:ap-northeast-1:123456789012:knowledge-base/EXAMPLE123"
        self.assertEqual(
            MOD.read_tags(session, "ap-northeast-1", arn),
            {"gyoumu012Project": "ele-knowledge"},
        )
        session.client.assert_called_once_with(
            "bedrock-agent", region_name="ap-northeast-1",
        )
        client.list_tags_for_resource.assert_called_once_with(resourceArn=arn)

    def test_lambda_verification_uses_service_api(self):
        session = Mock()
        session.client.return_value.list_tags.return_value = {
            "Tags": {"gyoumu012Usage": "shared"},
        }
        arn = self.resource()["arn"]
        self.assertEqual(
            MOD.read_tags(session, "ap-northeast-1", arn),
            {"gyoumu012Usage": "shared"},
        )
        session.client.return_value.list_tags.assert_called_once_with(
            Resource=arn,
        )

    def test_dynamodb_verification_reads_all_tag_pages(self):
        session = Mock()
        client = session.client.return_value
        client.list_tags_of_resource.side_effect = [
            {"Tags": [{"Key": "Project", "Value": "EleKnowledge"}],
             "NextToken": "next"},
            {"Tags": [{"Key": "gyoumu012Usage", "Value": "shared"}]},
        ]
        arn = "arn:aws:dynamodb:ap-northeast-1:123456789012:table/chatlogs-dev"
        self.assertEqual(
            MOD.read_tags(session, "ap-northeast-1", arn),
            {"Project": "EleKnowledge", "gyoumu012Usage": "shared"},
        )
        self.assertEqual(client.list_tags_of_resource.call_count, 2)


if __name__ == "__main__":
    unittest.main()

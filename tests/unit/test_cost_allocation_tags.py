"""Guard against cross-project changes and destructive tagging plans."""
import importlib.util
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

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


class CostTagApplyTests(unittest.TestCase):
    """Exercise the real planning/apply CLI with synthetic AWS responses."""

    ACCOUNT = "123456789012"
    REGION = "ap-northeast-1"
    STACK = "arn:aws:cloudformation:ap-northeast-1:123456789012:stack/test/id"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.plan_path = Path(self.temp.name) / "plan.json"
        self.session = Mock()
        self.clients = {name: Mock() for name in (
            "sts", "resourcegroupstaggingapi", "cloudformation", "logs",
        )}
        self.session.client.side_effect = lambda name, **kwargs: self.clients[name]
        self.clients["sts"].get_caller_identity.return_value = {
            "Account": self.ACCOUNT,
        }
        self.clients["resourcegroupstaggingapi"].tag_resources.return_value = {
            "FailedResourcesMap": {},
        }
        self.live = {}

    def resource(self, name="rag-dev", before=None):
        return {
            "arn": f"arn:aws:lambda:{self.REGION}:{self.ACCOUNT}:function:{name}",
            "region": self.REGION,
            "before": before if before is not None else {
                MOD.KEYS[0]: "ele-knowledge",
            },
            "desired": MOD.desired_tags("rag", "shared", "development"),
        }

    def cli(self, apply=False):
        import boto3
        argv = ["cost-tags", "--profile", "synthetic", "--expected-account",
                self.ACCOUNT, "--regions", self.REGION,
                "--plan", str(self.plan_path)]
        if apply:
            argv.append("--apply")

        def read(session, region, arn):
            return self.live[arn].copy()

        def write(**kwargs):
            for arn in kwargs["ResourceARNList"]:
                self.live[arn].update(kwargs["Tags"])
            return {"FailedResourcesMap": {}}

        self.clients["resourcegroupstaggingapi"].tag_resources.side_effect = write
        with patch.object(boto3, "Session", return_value=self.session), \
                patch.object(MOD.sys, "argv", argv), \
                patch.object(MOD, "read_tags", side_effect=read):
            return MOD.main()

    def plan(self, resources):
        MOD.save(self.plan_path, {"account": self.ACCOUNT, "resources": resources})
        self.live = {r["arn"]: r["before"].copy() for r in resources}

    def assert_no_writes(self):
        self.clients["resourcegroupstaggingapi"].tag_resources.assert_not_called()

    def stack_api(self):
        resource = self.resource()
        resource.update(
            arn=f"arn:aws:apigateway:{self.REGION}::/restapis/test-api",
            before={}, owner_stack=self.STACK, physical_id="test-api",
        )
        cf = self.clients["cloudformation"]
        cf.describe_stacks.return_value = {"Stacks": [{
            "StackId": self.STACK,
            "Tags": [{"Key": "Project", "Value": "EleKnowledge"}],
        }]}
        # Membership can be on a later page.
        cf.get_paginator.return_value.paginate.return_value = [
            {"StackResourceSummaries": []},
            {"StackResourceSummaries": [{"PhysicalResourceId": "test-api"}]},
        ]
        return resource

    def test_generated_new_key_only_plan_rejects_deleted_owner_before_any_write(self):
        resource = self.resource()
        tagging = self.clients["resourcegroupstaggingapi"]
        tagging.get_paginator.return_value.paginate.side_effect = [
            [{"ResourceTagMappingList": []}],
            [{"ResourceTagMappingList": [{
                "ResourceARN": resource["arn"],
                "Tags": [{"Key": MOD.KEYS[0], "Value": "ele-knowledge"}],
            }]}],
        ]
        cf = self.clients["cloudformation"]
        cf.get_paginator.return_value.paginate.return_value = []
        self.clients["logs"].get_paginator.return_value.paginate.return_value = []
        self.assertEqual(self.cli(), 0)
        plan = json.loads(self.plan_path.read_text(encoding="utf-8"))
        self.assertEqual(plan["resources"][0]["before"], resource["before"])
        self.live[resource["arn"]] = {}
        with self.assertRaisesRegex(ValueError, "ownership"):
            self.cli(apply=True)
        self.assert_no_writes()

    def test_changed_or_removed_ownership_keys_abort_all_resources(self):
        for key, original, changed in (
            (MOD.KEYS[0], "ele-knowledge", None),
            (MOD.KEYS[0], "ele-knowledge", "other-project"),
            ("Project", "EleKnowledge", None),
            ("Project", "EleKnowledge", "OtherProject"),
        ):
            with self.subTest(key=key, changed=changed):
                first = self.resource("first")
                second = self.resource("second", {key: original})
                self.plan([first, second])
                self.live[second["arn"]] = {} if changed is None else {key: changed}
                with self.assertRaisesRegex(ValueError, "ownership"):
                    self.cli(apply=True)
                self.assert_no_writes()

    def test_same_project_additions_and_unrelated_tags_are_allowed(self):
        resource = self.resource()
        self.plan([resource])
        self.live[resource["arn"]].update(Project="EleKnowledge", Extra="keep")
        self.live[resource["arn"]][MOD.KEYS[1]] = "rag"
        self.assertEqual(self.cli(apply=True), 0)
        self.clients["resourcegroupstaggingapi"].tag_resources.assert_called_once()
        self.assertEqual(self.live[resource["arn"]]["Extra"], "keep")

    def test_legacy_owner_accepts_new_same_project_key(self):
        resource = self.resource(before={"Project": "EleKnowledge"})
        self.plan([resource])
        self.live[resource["arn"]][MOD.KEYS[0]] = "ele-knowledge"
        self.assertEqual(self.cli(apply=True), 0)

    def test_parent_new_key_only_ownership_allows_log(self):
        parent = self.resource()
        child = self.resource("log", {})
        child.update(arn=f"arn:aws:logs:{self.REGION}:{self.ACCOUNT}:log-group:test",
                     owner=parent["arn"])
        self.plan([child, parent])
        self.assertEqual(self.cli(apply=True), 0)

    def test_parent_ownership_loss_aborts_child_and_other_resources(self):
        for before in ({MOD.KEYS[0]: "ele-knowledge"}, {"Project": "EleKnowledge"}):
            with self.subTest(before=before):
                parent = self.resource(before=before)
                child = self.resource("log", {})
                child.update(owner=parent["arn"])
                self.plan([child, parent])
                self.live[parent["arn"]] = {}
                with self.assertRaisesRegex(ValueError, "ownership"):
                    self.cli(apply=True)
                self.assert_no_writes()

    def test_stack_owner_and_paginated_membership_allow_api_and_log(self):
        api = self.stack_api()
        log = self.resource("log", {})
        log["owner"] = api["arn"]
        self.plan([log, api])
        self.assertEqual(self.cli(apply=True), 0)

    def test_missing_or_conflicting_stack_owner_aborts(self):
        for tags in ([], [{"Key": "Project", "Value": "OtherProject"}],
                     [{"Key": MOD.KEYS[0], "Value": "other-project"}]):
            with self.subTest(tags=tags):
                api = self.stack_api()
                self.plan([self.resource(), api])
                cf = self.clients["cloudformation"]
                cf.describe_stacks.return_value["Stacks"][0]["Tags"] = tags
                with self.assertRaisesRegex(ValueError, "ownership"):
                    self.cli(apply=True)
                self.assert_no_writes()

    def test_missing_stack_membership_aborts(self):
        api = self.stack_api()
        self.plan([self.resource(), api])
        cf = self.clients["cloudformation"]
        cf.get_paginator.return_value.paginate.return_value = [
            {"StackResourceSummaries": []},
        ]
        with self.assertRaisesRegex(ValueError, "ownership"):
            self.cli(apply=True)
        self.assert_no_writes()

    def test_stack_fallback_uses_live_member_ownership_and_stack_id(self):
        for lost_stack_id in (False, True):
            with self.subTest(lost_stack_id=lost_stack_id):
                api = self.stack_api()
                member = self.resource(before={
                    "Project": "EleKnowledge",
                    "aws:cloudformation:stack-id": self.STACK,
                })
                self.plan([api, member])
                cf = self.clients["cloudformation"]
                cf.describe_stacks.return_value["Stacks"][0]["Tags"] = []
                if lost_stack_id:
                    del self.live[member["arn"]]["aws:cloudformation:stack-id"]
                else:
                    del self.live[member["arn"]]["Project"]
                with self.assertRaisesRegex(ValueError, "ownership"):
                    self.cli(apply=True)
                self.assert_no_writes()

    def test_stack_fallback_accepts_live_owned_workload(self):
        api = self.stack_api()
        member = self.resource(before={
            "Project": "EleKnowledge", "aws:cloudformation:stack-id": self.STACK,
        })
        self.plan([api, member])
        cf = self.clients["cloudformation"]
        cf.describe_stacks.return_value["Stacks"][0]["Tags"] = []
        self.assertEqual(self.cli(apply=True), 0)


if __name__ == "__main__":
    unittest.main()

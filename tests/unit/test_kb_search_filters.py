"""Metadata filter tests for troubleshooting KB search Lambdas."""
import importlib.util
import os

BASE = os.path.join(os.path.dirname(__file__), "../..")


def _load(name, rel_path):
    path = os.path.normpath(os.path.join(BASE, rel_path))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kb_search1 = _load("kb_search1_filter_app", "lambda/troubleshooting/kb-search1/app.py")
kb_search2 = _load("kb_search2_filter_app", "lambda/troubleshooting/kb-search2/app.py")
kb_search3 = _load("kb_search3_filter_app", "lambda/troubleshooting/kb-search3/app.py")


def _control_system_equals(value="VFGLF"):
    return {"equals": {"key": "control-system", "value": value}}


def test_kb_search1_defaults_to_vfglf_filter():
    params = kb_search1.validate_parameters({"query": "停止する"})

    assert params["controlSystem"] == "VFGLF"
    assert kb_search1.build_metadata_filter(params) == _control_system_equals()


def test_kb_search2_defaults_to_vfglf_filter():
    params = kb_search2.validate_parameters({"query": "停止する"})

    assert params["controlSystem"] == "VFGLF"
    assert kb_search2.build_metadata_filter(params) == _control_system_equals()


def test_kb_search3_defaults_to_vfglf_filter():
    params = kb_search3.validate_parameters({"query": "停止する"})

    assert params["controlSystem"] == "VFGLF"
    assert kb_search3.build_metadata_filter(params) == _control_system_equals()


def test_error_code_adds_second_filter_only_when_supplied():
    params = kb_search2.validate_parameters({"query": "停止する", "errorCode": "e34"})

    assert params["errorCode"] == "E34"
    assert kb_search2.build_metadata_filter(params) == {
        "andAll": [
            _control_system_equals(),
            {"equals": {"key": "error-code", "value": "E34"}},
        ]
    }


def test_model_is_not_used_in_kb_filter():
    params = kb_search1.validate_parameters({"query": "停止する", "model": "KE-LG"})

    assert "model" not in params
    assert kb_search1.build_metadata_filter(params) == _control_system_equals()

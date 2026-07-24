import pytest

from compas_audit.run_audit import assert_external_preregistration


def _config() -> dict:
    return {
        "external_preregistration": {
            "required_for_live": True,
            "url_env_var": "EXTERNAL_PREREGISTRATION_URL",
            "accepted_hosts": ["osf.io", "aspredicted.org"],
            "source_document": "docs/osf_preregistration.md",
        }
    }


def test_external_preregistration_is_optional_when_not_required(monkeypatch):
    monkeypatch.delenv("EXTERNAL_PREREGISTRATION_URL", raising=False)
    assert assert_external_preregistration({}) == ""


def test_live_gate_rejects_missing_registration(monkeypatch):
    monkeypatch.delenv("EXTERNAL_PREREGISTRATION_URL", raising=False)
    with pytest.raises(RuntimeError, match="preregistration is required"):
        assert_external_preregistration(_config())


def test_live_gate_accepts_osf_url(monkeypatch):
    url = "https://osf.io/abc12"
    monkeypatch.setenv("EXTERNAL_PREREGISTRATION_URL", url)
    assert assert_external_preregistration(_config()) == url


def test_live_gate_accepts_aspredicted_url(monkeypatch):
    url = "https://aspredicted.org/xy123.pdf"
    monkeypatch.setenv("EXTERNAL_PREREGISTRATION_URL", url)
    assert assert_external_preregistration(_config()) == url


def test_live_gate_rejects_unapproved_host(monkeypatch):
    monkeypatch.setenv("EXTERNAL_PREREGISTRATION_URL", "https://example.com/registration")
    with pytest.raises(RuntimeError, match="permanent HTTPS registration URL"):
        assert_external_preregistration(_config())


def test_live_gate_rejects_non_https_url(monkeypatch):
    monkeypatch.setenv("EXTERNAL_PREREGISTRATION_URL", "http://osf.io/abc12")
    with pytest.raises(RuntimeError, match="permanent HTTPS registration URL"):
        assert_external_preregistration(_config())

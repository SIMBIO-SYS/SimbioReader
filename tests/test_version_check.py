import requests

from SimbioReader.version_check import _result_cache, check_pypi_version


def setup_function():
    _result_cache.clear()


class FakeResponse:
    def __init__(self, version: str):
        self.version = version

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {"info": {"version": self.version}}


def test_local_version_is_newer(monkeypatch):
    monkeypatch.setattr(
        "SimbioReader.version_check.requests.get",
        lambda *_args, **_kwargs: FakeResponse("0.7.0"),
    )

    result = check_pypi_version("SimbioReader", "0.8.0")

    assert result is not None
    assert result.local_is_newer is True
    assert result.update_available is False


def test_development_version_is_compared_without_losing_qualifier(monkeypatch):
    monkeypatch.setattr(
        "SimbioReader.version_check.requests.get",
        lambda *_args, **_kwargs: FakeResponse("1.0.0"),
    )

    result = check_pypi_version("SimbioReader", "1.0.0.dev1")

    assert result is not None
    assert result.update_available is True


def test_remote_version_is_newer(monkeypatch):
    monkeypatch.setattr(
        "SimbioReader.version_check.requests.get",
        lambda *_args, **_kwargs: FakeResponse("0.8.0"),
    )

    result = check_pypi_version("SimbioReader", "0.7.0")

    assert result is not None
    assert result.update_available is True
    assert result.local_is_newer is False


def test_versions_are_equal(monkeypatch):
    monkeypatch.setattr(
        "SimbioReader.version_check.requests.get",
        lambda *_args, **_kwargs: FakeResponse("0.7.0"),
    )

    result = check_pypi_version("SimbioReader", "0.7.0")

    assert result is not None
    assert result.update_available is False
    assert result.local_is_newer is False


def test_network_error_is_ignored(monkeypatch):
    def fail(*_args, **_kwargs):
        raise requests.ConnectionError

    monkeypatch.setattr("SimbioReader.version_check.requests.get", fail)

    assert check_pypi_version("SimbioReader", "0.7.0") is None

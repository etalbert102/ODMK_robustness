import pytest

from odmk import environment
from odmk.exceptions import ODMKError


def test_current_locked_environment_passes() -> None:
    observed = environment.assert_frozen_environment()

    assert observed["python"] == environment.EXPECTED_PYTHON
    assert observed["packages"] == environment.EXPECTED_PACKAGES


def test_wrong_python_version_is_rejected(monkeypatch) -> None:
    monkeypatch.setattr(environment.platform, "python_version", lambda: "0.0.0")

    with pytest.raises(ODMKError, match="Python: 0.0.0"):
        environment.assert_frozen_environment()


def test_wrong_direct_package_version_is_rejected(monkeypatch) -> None:
    real_version = environment.importlib.metadata.version

    def version(distribution: str) -> str:
        if distribution == "numpy":
            return "0.0.0"
        return real_version(distribution)

    monkeypatch.setattr(environment.importlib.metadata, "version", version)

    with pytest.raises(ODMKError, match="numpy: 0.0.0"):
        environment.assert_frozen_environment()

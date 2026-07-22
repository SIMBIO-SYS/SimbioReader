from dataclasses import dataclass
from time import monotonic

import requests
from packaging.version import InvalidVersion, Version


@dataclass(frozen=True, slots=True)
class VersionCheckResult:
    current: Version
    latest: Version

    @property
    def update_available(self) -> bool:
        return self.current < self.latest

    @property
    def local_is_newer(self) -> bool:
        return self.current > self.latest


_CACHE_TTL_SECONDS = 3600
_result_cache: dict[tuple[str, str], tuple[float, VersionCheckResult | None]] = {}


def check_pypi_version(
    package_name: str,
    package_version: str,
    *,
    timeout: float = 1,
) -> VersionCheckResult | None:
    """Compare an installed version with the latest version on PyPI.

    Network errors and invalid responses are ignored so that an unavailable
    update service never prevents the reader from opening a product.
    """
    cache_key = (package_name, package_version)
    cached = _result_cache.get(cache_key)
    now = monotonic()
    if cached and now - cached[0] < _CACHE_TTL_SECONDS:
        return cached[1]

    result: VersionCheckResult | None
    try:
        response = requests.get(
            f"https://pypi.org/pypi/{package_name}/json",
            timeout=timeout,
        )
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]
        result = VersionCheckResult(
            current=Version(package_version),
            latest=Version(latest_version),
        )
    except (
        requests.RequestException,
        InvalidVersion,
        KeyError,
        TypeError,
        ValueError,
    ):
        result = None

    _result_cache[cache_key] = (now, result)
    return result

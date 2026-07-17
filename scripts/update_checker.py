from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

VERSION_FILE = ROOT / "VERSION"


@dataclass
class UpdateStatus:

    current: str

    latest: str | None

    update_available: bool

    release_url: str | None


def read_local_version() -> str:

    return VERSION_FILE.read_text(
        encoding="utf-8"
    ).strip()


def fetch_latest_release(
    owner: str,
    repository: str,
):

    url = (
        "https://api.github.com/repos/"
        f"{owner}/{repository}/releases/latest"
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "PythonDeploymentCompressor",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=10,
    ) as response:

        return json.loads(
            response.read().decode("utf-8")
        )


def check_for_updates(
    owner: str,
    repository: str,
) -> UpdateStatus:

    current = read_local_version()

    try:

        payload = fetch_latest_release(
            owner,
            repository,
        )

        latest = payload["tag_name"].removeprefix(
            "v"
        )

        url = payload["html_url"]

        return UpdateStatus(
            current=current,
            latest=latest,
            update_available=current != latest,
            release_url=url,
        )

    except urllib.error.HTTPError:

        return UpdateStatus(
            current=current,
            latest=None,
            update_available=False,
            release_url=None,
        )

    except Exception:

        return UpdateStatus(
            current=current,
            latest=None,
            update_available=False,
            release_url=None,
        )


def print_update_status(
    status: UpdateStatus,
):

    print("Checking for updates...")

    if status.latest is None:

        print(
            "⚠ Unable to contact GitHub."
        )

        return

    if not status.update_available:

        print(
            f"✓ Version {status.current} is up to date."
        )

        return

    print()

    print("=" * 60)

    print("A newer version is available")

    print()

    print(
        f"Current : {status.current}"
    )

    print(
        f"Latest  : {status.latest}"
    )

    print()

    print(
        f"Release : {status.release_url}"
    )

    print("=" * 60)

    print()


if __name__ == "__main__":

    status = check_for_updates(
        owner="your-github-user",
        repository="python-deployment-compressor",
    )

    print_update_status(status)
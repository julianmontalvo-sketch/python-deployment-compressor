from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from optimizer import optimize_python_source


ROOT = Path(__file__).resolve().parent.parent
SANDBOX_FILE = ROOT / "sandbox" / "sample.py"


@dataclass
class ExecutionResult:
    return_code: int
    stdout: str
    stderr: str


def execute_python(file: Path) -> ExecutionResult:

    result = subprocess.run(
        [sys.executable, str(file)],
        capture_output=True,
        text=True,
    )

    return ExecutionResult(
        return_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def sha256(value: str) -> str:

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def compare_results(
    original: ExecutionResult,
    optimized: ExecutionResult,
) -> tuple[bool, str]:

    if original.return_code != optimized.return_code:
        return False, "Exit code differs."

    if sha256(original.stdout) != sha256(
        optimized.stdout
    ):
        return False, "stdout differs."

    if sha256(original.stderr) != sha256(
        optimized.stderr
    ):
        return False, "stderr differs."

    return True, "Sandbox validation passed."


def run_sandbox() -> bool:

    print("Running validation sandbox...")

    if not SANDBOX_FILE.exists():

        print("Sandbox sample.py not found.")

        return False

    source = SANDBOX_FILE.read_text(
        encoding="utf-8"
    )

    optimized = optimize_python_source(source)

    with tempfile.TemporaryDirectory() as temp:

        temp = Path(temp)

        original_file = temp / "original.py"

        optimized_file = temp / "optimized.py"

        original_file.write_text(
            source,
            encoding="utf-8",
        )

        optimized_file.write_text(
            optimized,
            encoding="utf-8",
        )

        original_result = execute_python(
            original_file
        )

        optimized_result = execute_python(
            optimized_file
        )

    success, message = compare_results(
        original_result,
        optimized_result,
    )

    if success:

        print("✓ Sandbox PASSED")

        return True

    print()

    print("Sandbox FAILED")

    print(message)

    print()

    return False


if __name__ == "__main__":

    success = run_sandbox()

    sys.exit(0 if success else 1)
from __future__ import annotations

import argparse
import ast
import json
import shutil
import sys
import time
import zipfile
from pathlib import Path

import yaml

from optimizer import optimize_python_source
from sandbox import run_sandbox
from update_checker import check_for_updates


ROOT = Path.cwd()


def load_configuration():

    config_file = ROOT / "config.yaml"

    if not config_file.exists():
        raise FileNotFoundError("config.yaml not found.")

    with config_file.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def should_ignore(path: Path, config: dict) -> bool:

    ignore = config["ignore"]

    for directory in ignore["directories"]:

        if directory in path.parts:
            return True

    if path.suffix in ignore["extensions"]:
        return True

    if path.name in ignore["filenames"]:
        return True

    return False


def scan_project(config):

    python_files = []

    asset_files = []

    for file in ROOT.rglob("*"):

        if not file.is_file():
            continue

        if ".build" in file.parts:
            continue

        if should_ignore(file, config):
            continue

        if file.suffix == ".py":
            python_files.append(file)
        else:
            asset_files.append(file)

    return python_files, asset_files


def validate_python(source: str) -> bool:

    try:

        ast.parse(source)

        return True

    except SyntaxError:

        return False


def build_directory(config):

    build = ROOT / config["output"]["build_directory"]

    if build.exists():
        shutil.rmtree(build)

    build.mkdir(parents=True)

    return build


def write_python_files(files, build_dir, config):

    compression = config["compression"]

    processed = 0

    original_size = 0

    compressed_size = 0

    for file in files:

        relative = file.relative_to(ROOT)

        destination = build_dir / relative

        destination.parent.mkdir(parents=True, exist_ok=True)

        source = file.read_text(encoding="utf-8")

        optimized = optimize_python_source(
            source,
            remove_comments=compression["remove_comments"],
            trim_trailing_spaces=compression[
                "trim_trailing_whitespace"
            ],
            collapse_blank_lines=compression[
                "collapse_blank_lines"
            ],
        )

        if not validate_python(optimized):
            optimized = source

        destination.write_text(
            optimized,
            encoding="utf-8",
        )

        processed += 1

        original_size += len(source.encode())

        compressed_size += len(optimized.encode())

    return processed, original_size, compressed_size


def copy_assets(files, build_dir):

    copied = 0

    for file in files:

        relative = file.relative_to(ROOT)

        destination = build_dir / relative

        destination.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(file, destination)

        copied += 1

    return copied


def build_zip(build_dir, config):

    zip_name = config["output"]["zip_name"]

    zip_file = build_dir / zip_name

    with zipfile.ZipFile(
        zip_file,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:

        for file in build_dir.rglob("*"):

            if file == zip_file:
                continue

            if file.is_file():

                archive.write(
                    file,
                    file.relative_to(build_dir),
                )

    return zip_file


def generate_report(
    build_dir,
    config,
    processed,
    copied,
    original_size,
    compressed_size,
    sandbox_result,
    duration,
):

    report = {

        "processed_python_files": processed,

        "copied_assets": copied,

        "original_size": original_size,

        "compressed_size": compressed_size,

        "saved_bytes": (
            original_size - compressed_size
        ),

        "saved_percent": round(
            (
                (original_size - compressed_size)
                / original_size
            )
            * 100,
            2,
        )
        if original_size
        else 0,

        "sandbox": sandbox_result,

        "execution_seconds": round(
            duration,
            2,
        ),
    }

    report_file = (
        build_dir
        / config["output"]["report_name"]
    )

    report_file.write_text(
        json.dumps(
            report,
            indent=4,
        ),
        encoding="utf-8",
    )


def print_banner():

    print()

    print("=" * 55)

    print(" Python Deployment Compressor")

    print("=" * 55)

    print()


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "project",
        nargs="?",
        default=".",
        help="Project path",
    )

    parser.parse_args()

    start = time.perf_counter()

    print_banner()

    config = load_configuration()

    if config["github"]["check_updates"]:

        check_for_updates(
            config["github"]["owner"],
            config["github"]["repository"],
        )

    if config["sandbox"]["enabled"]:

        print()

        print("Running validation sandbox...")

        if not run_sandbox():

            print()

            print(
                "Compression aborted."
            )

            sys.exit(1)

    print()

    print("Scanning project...")

    python_files, asset_files = scan_project(config)

    build = build_directory(config)

    processed, original_size, compressed_size = (
        write_python_files(
            python_files,
            build,
            config,
        )
    )

    copied = copy_assets(
        asset_files,
        build,
    )

    zip_file = build_zip(
        build,
        config,
    )

    duration = (
        time.perf_counter() - start
    )

    generate_report(
        build,
        config,
        processed,
        copied,
        original_size,
        compressed_size,
        True,
        duration,
    )

    print()

    print(
        f"Python files : {processed}"
    )

    print(
        f"Assets       : {copied}"
    )

    print(
        f"Archive      : {zip_file}"
    )

    print(
        f"Saved        : {original_size - compressed_size} bytes"
    )

    print()

    print("Done.")


if __name__ == "__main__":

    main()
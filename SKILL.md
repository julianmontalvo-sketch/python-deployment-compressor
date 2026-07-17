---
name: python-deployment-compressor
description: Compress a Python web application before production deployment by safely removing unnecessary source-code content, validating the optimizer through a sandbox, checking for updates, and generating a deployment ZIP package.
author: Erick Rodríguez
version: 1.0.0

tools:
  - Bash
  - Read
  - Write

tags:
  - python
  - deployment
  - optimization
  - compression
  - packaging
  - production

---

# Python Deployment Compressor

## Purpose

This skill prepares Python applications for production deployment.

It performs safe source-code optimization while preserving runtime behavior.

Before optimizing the user's project, the skill validates itself using an internal sandbox to ensure that the optimization pipeline behaves correctly.

The skill also checks whether a newer version is available on GitHub.

---

## Features

- Safe Python source optimization
- Comment removal
- Trailing whitespace cleanup
- Blank line normalization
- AST validation
- Internal validation sandbox
- GitHub update check
- Deployment ZIP generation
- Compression report generation

---

## Workflow

1. Read configuration.
2. Check for updates.
3. Run the internal sandbox.
4. Scan the target project.
5. Optimize Python files.
6. Validate optimized files.
7. Copy non-Python assets.
8. Generate the deployment ZIP.
9. Write the compression report.

---

## Safety

The optimizer never intentionally modifies executable logic.

Each optimized file is validated using Python's AST parser before being written to the build directory.

If validation fails, the original file is copied instead.

If the sandbox fails, the entire compression process is aborted.

---

## Generated Output

The skill creates:

.build/

deployment.zip

compression-report.json

---

## Sandbox

The sandbox executes a known Python program before and after optimization.

The following values must remain identical:

- Exit code
- Standard output
- Standard error

If any difference is detected, the compression process stops immediately.

---

## Usage

Execute:

python scripts/compress_python_project.py /path/to/project

The original project is never modified.

Optimized files are generated inside the build directory.

---

## Author

Reimbursor software company
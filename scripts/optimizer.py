from __future__ import annotations

import io
import tokenize


def optimize_python_source(
    source: str,
    remove_comments: bool = True,
    trim_trailing_whitespace: bool = True,
    collapse_blank_lines: bool = True,
) -> str:
    """
    Optimizes Python source code while preserving runtime behavior.

    Supported optimizations

    - Remove comments
    - Trim trailing whitespace
    - Collapse consecutive blank lines
    """

    optimized = source

    if remove_comments:
        optimized = _remove_comments(optimized)

    if trim_trailing_whitespace:
        optimized = _trim_trailing_whitespace(
            optimized
        )

    if collapse_blank_lines:
        optimized = _collapse_blank_lines(
            optimized
        )

    return optimized


def _remove_comments(source: str) -> str:

    reader = io.StringIO(source).readline

    tokens = []

    for token in tokenize.generate_tokens(reader):

        if token.type == tokenize.COMMENT:
            continue

        tokens.append(token)

    return tokenize.untokenize(tokens)


def _trim_trailing_whitespace(source: str) -> str:

    lines = []

    for line in source.splitlines():

        lines.append(line.rstrip())

    return "\n".join(lines)


def _collapse_blank_lines(source: str) -> str:

    output = []

    previous_blank = False

    for line in source.splitlines():

        blank = line.strip() == ""

        if blank and previous_blank:
            continue

        output.append(line)

        previous_blank = blank

    return "\n".join(output) + "\n"

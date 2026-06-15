"""Command-line entry point for Serpent.

This is a minimal skeleton (Phase 0). The full subcommand surface
(``setup``, ``generate``, ``launch``, ``play``, ``capture``, ``train``,
``visual-debugger``) lands in a later phase; for now it exposes ``--version``
and a help screen so the ``serpent`` console script is wired end to end.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from serpent import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="serpent",
        description="Serpent — a cross-platform Python game agent development kit.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # No subcommands wired yet — show help so the command is discoverable.
    del args
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

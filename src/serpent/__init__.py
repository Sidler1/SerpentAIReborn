"""Serpent — a cross-platform Python game agent development kit."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("serpent")
except PackageNotFoundError:  # package is not installed (e.g. running from source)
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]

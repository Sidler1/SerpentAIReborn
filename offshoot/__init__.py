"""offshoot — Serpent's plugin framework.

Vendored into SerpentAI Reborn and modernized for Python 3.13 (exec/eval-based
import machinery replaced with importlib; no behavioural/API changes). Plugins
and the framework keep importing it as ``import offshoot``.
"""

from offshoot.base import (
    accepted,
    default_configuration,
    discover,
    executable_hook,
    expected,
    file_contains_pluggable,
    forbidden,
    generate_configuration_file,
    installed_plugins,
    load_configuration,
    map_pluggable_classes,
    validate_plugin_file,
)
from offshoot.manifest import Manifest
from offshoot.pluggable import Pluggable
from offshoot.plugin import Plugin, PluginError

config = load_configuration("offshoot.yml")


def pluggable_classes():
    return map_pluggable_classes(config)


__all__ = [
    "Manifest",
    "Pluggable",
    "Plugin",
    "PluginError",
    "accepted",
    "config",
    "default_configuration",
    "discover",
    "executable_hook",
    "expected",
    "file_contains_pluggable",
    "forbidden",
    "generate_configuration_file",
    "installed_plugins",
    "load_configuration",
    "map_pluggable_classes",
    "pluggable_classes",
    "validate_plugin_file",
]

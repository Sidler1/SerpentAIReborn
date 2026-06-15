"""Phase I: the three bundled game plugins load + validate against the modern API.

Super Hexagon is a full worked reference (real PLAY handler); Isaac and YMBAB are
scaffolds (load/validate, PLAY is a TODO). All six pluggable files must satisfy
the modern offshoot contract and import cleanly.
"""

import importlib
from pathlib import Path

import pytest

import offshoot
from serpent.game import Game
from serpent.game_agent import GameAgent

REPO_ROOT = Path(__file__).resolve().parents[2]

# (file path, pluggable, class name, importable module)
PLUGINS = [
    (
        "plugins/SuperHexagonGamePlugin/files/super_hexagon_game.py",
        "Game",
        "SuperHexagonGame",
        "plugins.SuperHexagonGamePlugin.files.super_hexagon_game",
    ),
    (
        "plugins/SuperHexagonGameAgentPlugin/files/super_hexagon_game_agent.py",
        "GameAgent",
        "SuperHexagonGameAgent",
        "plugins.SuperHexagonGameAgentPlugin.files.super_hexagon_game_agent",
    ),
    (
        "plugins/BindingOfIsaacRebirthGamePlugin/files/binding_of_isaac_rebirth_game.py",
        "Game",
        "BindingOfIsaacRebirthGame",
        "plugins.BindingOfIsaacRebirthGamePlugin.files.binding_of_isaac_rebirth_game",
    ),
    (
        "plugins/BindingOfIsaacRebirthGameAgentPlugin/files/binding_of_isaac_rebirth_game_agent.py",
        "GameAgent",
        "BindingOfIsaacRebirthGameAgent",
        "plugins.BindingOfIsaacRebirthGameAgentPlugin.files.binding_of_isaac_rebirth_game_agent",
    ),
    (
        "plugins/YouMustBuildABoatGamePlugin/files/you_must_build_a_boat_game.py",
        "Game",
        "YouMustBuildABoatGame",
        "plugins.YouMustBuildABoatGamePlugin.files.you_must_build_a_boat_game",
    ),
    (
        "plugins/YouMustBuildABoatGameAgentPlugin/files/you_must_build_a_boat_game_agent.py",
        "GameAgent",
        "YouMustBuildABoatGameAgent",
        "plugins.YouMustBuildABoatGameAgentPlugin.files.you_must_build_a_boat_game_agent",
    ),
    (
        "plugins/PeglinGamePlugin/files/peglin_game.py",
        "Game",
        "PeglinGame",
        "plugins.PeglinGamePlugin.files.peglin_game",
    ),
    (
        "plugins/PeglinGameAgentPlugin/files/peglin_game_agent.py",
        "GameAgent",
        "PeglinGameAgent",
        "plugins.PeglinGameAgentPlugin.files.peglin_game_agent",
    ),
]

_BASE = {"Game": Game, "GameAgent": GameAgent}


@pytest.mark.parametrize("path,pluggable,class_name,module", PLUGINS)
def test_plugin_validates_against_modern_contract(path, pluggable, class_name, module):
    directives = _BASE[pluggable].method_directives()
    is_valid, messages = offshoot.validate_plugin_file(str(REPO_ROOT / path), pluggable, directives)

    assert is_valid, messages
    assert offshoot.file_contains_pluggable(str(REPO_ROOT / path), pluggable) == [True, class_name]


@pytest.mark.parametrize("path,pluggable,class_name,module", PLUGINS)
def test_plugin_imports(path, pluggable, class_name, module, monkeypatch):
    monkeypatch.syspath_prepend(str(REPO_ROOT))

    imported = importlib.import_module(module)
    plugin_class = getattr(imported, class_name)

    assert issubclass(plugin_class, _BASE[pluggable])

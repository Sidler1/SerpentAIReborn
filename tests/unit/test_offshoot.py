"""Tests for the vendored offshoot plugin framework (contract + discovery)."""

import json
import sys

import offshoot
from serpent.game import Game


class _Thing(offshoot.Pluggable):
    @offshoot.forbidden
    def forbidden_method(self):
        pass

    @offshoot.expected
    def expected_method(self):
        pass

    def undecorated_method(self):
        pass


def test_method_directives_detects_decorators():
    directives = _Thing.method_directives()

    assert "expected_method" in directives["expected"]
    assert "forbidden_method" in directives["forbidden"]
    # Undecorated (non-__init__) methods are implicitly forbidden.
    assert "undecorated_method" in directives["forbidden"]


def test_validate_plugin_file_accepts_valid_pluggable(tmp_path):
    plugin_file = tmp_path / "valid_game.py"
    plugin_file.write_text(
        "from serpent.game import Game\n\n"
        "class ValidGame(Game):\n    def required(self):\n        pass\n"
    )

    is_valid, messages = offshoot.validate_plugin_file(
        str(plugin_file),
        "Game",
        {"expected": ["required"], "forbidden": ["banned"], "accepted": []},
    )

    assert is_valid is True
    assert messages == []


def test_validate_plugin_file_flags_missing_expected_and_forbidden(tmp_path):
    plugin_file = tmp_path / "bad_game.py"
    plugin_file.write_text(
        "from serpent.game import Game\n\n"
        "class BadGame(Game):\n    def banned(self):\n        pass\n"
    )

    is_valid, messages = offshoot.validate_plugin_file(
        str(plugin_file),
        "Game",
        {"expected": ["required"], "forbidden": ["banned"], "accepted": []},
    )

    assert is_valid is False
    assert any("banned" in m for m in messages)
    assert any("required" in m for m in messages)


def test_validate_plugin_file_flags_absent_pluggable(tmp_path):
    plugin_file = tmp_path / "no_pluggable.py"
    plugin_file.write_text("class Unrelated:\n    pass\n")

    is_valid, messages = offshoot.validate_plugin_file(
        str(plugin_file), "Game", {"expected": [], "forbidden": [], "accepted": []}
    )

    assert is_valid is False
    assert any("No classes inherit" in m for m in messages)


def test_file_contains_pluggable(tmp_path):
    plugin_file = tmp_path / "g.py"
    plugin_file.write_text("from serpent.game import Game\n\nclass MyGame(Game):\n    pass\n")

    assert offshoot.file_contains_pluggable(str(plugin_file), "Game") == [True, "MyGame"]
    assert offshoot.file_contains_pluggable(str(plugin_file), "GameAgent") == [False, None]


def test_discover_imports_pluggable_classes(tmp_path, monkeypatch):
    # Lay out plugins/DemoPlugin/files/demo_game.py as an importable package.
    files_dir = tmp_path / "plugins" / "DemoPlugin" / "files"
    files_dir.mkdir(parents=True)
    for pkg in (tmp_path / "plugins", tmp_path / "plugins" / "DemoPlugin", files_dir):
        (pkg / "__init__.py").write_text("")
    (files_dir / "demo_game.py").write_text(
        "from serpent.game import Game\n\n"
        "class DemoGame(Game):\n"
        "    @property\n"
        "    def screen_regions(self):\n"
        "        return {}\n"
    )

    manifest = {
        "plugins": {
            "DemoPlugin": {
                "name": "DemoPlugin",
                "files": [{"path": "demo_game.py", "pluggable": "Game"}],
            }
        }
    }
    (tmp_path / "offshoot.manifest.json").write_text(json.dumps(manifest))

    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    # The repo bundles a real top-level `plugins` package; drop any cached copy so
    # the prepended tmp_path one resolves here.
    for name in [m for m in sys.modules if m == "plugins" or m.startswith("plugins.")]:
        monkeypatch.delitem(sys.modules, name, raising=False)

    mapping = offshoot.discover("Game")

    assert "DemoGame" in mapping
    assert issubclass(mapping["DemoGame"], Game)

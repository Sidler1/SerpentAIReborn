"""The consolidated CLI: cli.py is the single entry, delegating to serpent.serpent."""

import cli
import serpent.serpent


def test_serpent_serpent_has_no_legacy_dispatcher():
    # The parallel dispatcher (execute/mappings/__main__) was removed; serpent.serpent
    # is now a pure implementation library behind cli.py.
    assert not hasattr(serpent.serpent, "execute")
    assert not hasattr(serpent.serpent, "command_function_mapping")
    # Implementations remain.
    assert callable(serpent.serpent.play)
    assert callable(serpent.serpent.grab_frames)


def test_cli_registers_game_commands():
    commands = set(cli.cli.commands)

    # The frame grabber the play loop spawns as `serpent grab-frames` must exist.
    assert "grab-frames" in commands
    for expected in {"launch", "play", "record", "train", "plugins", "capture", "generate"}:
        assert expected in commands, expected


def test_object_recognition_is_gone():
    assert not hasattr(serpent.serpent, "object_recognition")
    assert not hasattr(serpent.serpent, "train_object")

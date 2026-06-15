import offshoot


class YouMustBuildABoatGameAgentPlugin(offshoot.Plugin):
    name = "YouMustBuildABoatGameAgentPlugin"
    version = "0.2.0"

    libraries = []

    files = [
        {"path": "you_must_build_a_boat_game_agent.py", "pluggable": "GameAgent"}
    ]

    config = {
        "frame_handler": "PLAY"
    }

    @classmethod
    def on_install(cls):
        print(f"\n\n{cls.__name__} was installed successfully!")

    @classmethod
    def on_uninstall(cls):
        print(f"\n\n{cls.__name__} was uninstalled successfully!")


if __name__ == "__main__":
    offshoot.executable_hook(YouMustBuildABoatGameAgentPlugin)

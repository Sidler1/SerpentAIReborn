import offshoot


class SerpentPeglinGamePlugin(offshoot.Plugin):
    name = "SerpentPeglinGamePlugin"
    version = "0.1.0"

    libraries = []

    files = [
        {"path": "peglin_game.py", "pluggable": "Game"}
    ]

    config = {
        "fps": 4
    }

    @classmethod
    def on_install(cls):
        print(f"\n\n{cls.__name__} was installed successfully!")

    @classmethod
    def on_uninstall(cls):
        print(f"\n\n{cls.__name__} was uninstalled successfully!")


if __name__ == "__main__":
    offshoot.executable_hook(SerpentPeglinGamePlugin)

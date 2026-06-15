import offshoot


class BindingOfIsaacRebirthGamePlugin(offshoot.Plugin):
    name = "BindingOfIsaacRebirthGamePlugin"
    version = "0.2.0"

    libraries = []

    files = [
        {"path": "binding_of_isaac_rebirth_game.py", "pluggable": "Game"}
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
    offshoot.executable_hook(BindingOfIsaacRebirthGamePlugin)

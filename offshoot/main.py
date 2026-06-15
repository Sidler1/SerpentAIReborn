#!/usr/bin/env python
import os
import subprocess
import sys

import offshoot

valid_commands = ["init", "install", "uninstall"]


def execute():
    if len(sys.argv) == 2:
        command = sys.argv[1]

        if command not in valid_commands:
            raise Exception(f"'{command}' is not a valid Offshoot command.")

        if command == "init":
            init()
    elif len(sys.argv) > 2:
        command, args = sys.argv[1], sys.argv[2:]

        if command not in valid_commands:
            raise Exception(f"'{command}' is not a valid Offshoot command.")

        if command == "install":
            install(args[0])
        elif command == "uninstall":
            uninstall(args[0])


def install(plugin):
    print(f"OFFSHOOT: Attempting to install {plugin}...")

    plugin_directory = offshoot.config.get("file_paths").get("plugins")
    plugin_path = "{}/{}/plugin.py".replace("/", os.sep).format(plugin_directory, plugin)

    plugin_module_string = plugin_path.replace(os.sep, ".").replace(".py", "")

    subprocess.call([sys.executable.split(os.sep)[-1], "-m", plugin_module_string, "install"])


def uninstall(plugin):
    print(f"OFFSHOOT: Attempting to uninstall {plugin}...")

    plugin_directory = offshoot.config.get("file_paths").get("plugins")
    plugin_path = "{}/{}/plugin.py".replace("/", os.sep).format(plugin_directory, plugin)

    plugin_module_string = plugin_path.replace(os.sep, ".").replace(".py", "")

    subprocess.call([sys.executable.split(os.sep)[-1], "-m", plugin_module_string, "uninstall"])


def init():
    import warnings

    warnings.filterwarnings("ignore")

    print("OFFSHOOT: Generating configuration file...")
    offshoot.generate_configuration_file()
    print("OFFSHOOT: Initialized successfully!")


if __name__ == "__main__":
    execute()

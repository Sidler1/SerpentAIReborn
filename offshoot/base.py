import ast
import importlib
import os
import sys
import warnings

import yaml

from offshoot.manifest import Manifest
from offshoot.pluggable import Pluggable


def default_configuration():
    return {
        "modules": [],
        "file_paths": {
            "plugins": "plugins",
            "config": "config/config.plugins.yml".replace("/", os.sep),
            "libraries": "requirements.plugins.txt",
        },
        "allow": {
            "files": True,
            "config": True,
            "plugins": True,
            "libraries": True,
            "callbacks": True,
        },
        "sandbox_configuration_keys": True,
    }


def load_configuration(file_path):
    try:
        with open(file_path) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        warnings.warn(f"'{file_path}' not found! Using default configuration.", stacklevel=2)
        config = default_configuration()

    return config


def generate_configuration_file():
    with open("offshoot.yml", "w") as f:
        yaml.dump(default_configuration(), f, default_flow_style=False, indent=4)


def map_pluggable_classes(config):
    pluggable_classes = {}

    for module_name in config.get("modules"):
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            warnings.warn(
                f"'{module_name}' does not appear to be a valid module. Skipping!", stacklevel=2
            )
            continue

        for name, member in vars(module).items():
            if isinstance(member, type) and issubclass(member, Pluggable):
                pluggable_classes[name] = member

    return pluggable_classes


def validate_plugin_file(file_path, pluggable, directives):
    is_valid = True
    messages = []

    with open(file_path) as f:
        syntax_tree = ast.parse(f.read())

    seen_pluggable = False

    for statement in ast.walk(syntax_tree):
        if isinstance(statement, ast.ClassDef):
            class_name = statement.name

            current_expected = directives["expected"][:]
            bases = [b.id if isinstance(b, ast.Name) else b.attr for b in statement.bases]

            if pluggable in bases:
                seen_pluggable = True

                for body_item in statement.body:
                    if isinstance(body_item, ast.FunctionDef):
                        if body_item.name in directives["forbidden"]:
                            is_valid = False
                            messages.append(
                                f"{class_name}: '{body_item.name}' method should not appear "
                                "in the class."
                            )

                        if body_item.name in current_expected:
                            current_expected.remove(body_item.name)

                if len(current_expected):
                    is_valid = False
                    messages.append(
                        f"{class_name}: Some expected methods are missing from the class: "
                        f"{', '.join(current_expected)}"
                    )

    if seen_pluggable is False:
        is_valid = False
        messages.append(f"No classes inherit from the pluggable '{pluggable}'.")

    return [is_valid, messages]


def installed_plugins():
    manifest = Manifest()
    plugins = manifest.list_plugins()

    return [f"{plugin.get('name')} - {plugin.get('version')}" for plugin in plugins.values()]


def discover(pluggable, scope=None, selection=None):
    manifest = Manifest()

    plugin_file_paths = manifest.plugin_files_for_pluggable(pluggable)

    class_mapping = {}

    if isinstance(selection, str):
        selection = [selection]

    for plugin_file_path, file_pluggable in plugin_file_paths:
        module_name = plugin_file_path.replace(os.sep, ".").removesuffix(".py")

        valid, plugin_class_name = file_contains_pluggable(plugin_file_path, file_pluggable)

        if not valid:
            continue

        if selection and plugin_class_name not in selection:
            continue

        module = importlib.import_module(module_name)
        plugin_class = getattr(module, plugin_class_name)

        class_mapping[plugin_class_name] = plugin_class

        if scope is not None:
            scope[plugin_class_name] = plugin_class

    return {} if scope is not None else class_mapping


def file_contains_pluggable(file_path, pluggable):
    plugin_class = None

    try:
        with open(file_path) as f:
            syntax_tree = ast.parse(f.read())
    except FileNotFoundError:
        return [False, None]

    for statement in ast.walk(syntax_tree):
        if isinstance(statement, ast.ClassDef):
            bases = [b.id if isinstance(b, ast.Name) else b.attr for b in statement.bases]

            if pluggable in bases:
                plugin_class = statement.name

    return [plugin_class is not None, plugin_class]


def executable_hook(plugin_class):
    command = sys.argv[1]

    if command == "install":
        plugin_class.install()
    elif command == "uninstall":
        plugin_class.uninstall()


# Magic Validation Decorators (markers detected via source inspection; see pluggable.py)
def accepted(func):
    return func


def expected(func):
    return func


def forbidden(func):
    return func

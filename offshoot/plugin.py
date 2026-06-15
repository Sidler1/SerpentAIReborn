import os
import os.path

import yaml

import offshoot


class PluginError(Exception):
    pass


class Plugin:
    name = "Plugin"
    version = "0.0.0"

    libraries = []
    plugins = []
    files = []
    config = {}

    @classmethod
    def on_install(cls):
        print(f"\n\n{cls.__name__} was installed successfully!")

    @classmethod
    def on_uninstall(cls):
        print(f"\n\n{cls.__name__} was uninstalled successfully!")

    @classmethod
    def install(cls):
        if offshoot.config["allow"]["plugins"] is True:
            cls.verify_plugin_dependencies()
        if offshoot.config["allow"]["files"] is True:
            cls.install_files()
        if offshoot.config["allow"]["config"] is True:
            cls.install_configuration()
        if offshoot.config["allow"]["libraries"] is True:
            cls.install_libraries()
        if offshoot.config["allow"]["callbacks"] is True:
            cls.on_install()

        manifest = offshoot.Manifest()
        manifest.add_plugin(cls.name)

    @classmethod
    def uninstall(cls):
        if offshoot.config["allow"]["files"] is True:
            cls.uninstall_files()
        if offshoot.config["allow"]["config"] is True:
            cls.uninstall_configuration()
        if offshoot.config["allow"]["libraries"] is True:
            cls.uninstall_libraries()
        if offshoot.config["allow"]["callbacks"] is True:
            cls.on_uninstall()

        manifest = offshoot.Manifest()
        manifest.remove_plugin(cls.name)

    @classmethod
    def verify_plugin_dependencies(cls):
        print("\nOFFSHOOT PLUGIN INSTALL: Verifying that plugin dependencies are installed...\n")

        manifest = offshoot.Manifest()

        missing_plugin_names = [
            plugin_name for plugin_name in cls.plugins if not manifest.contains_plugin(plugin_name)
        ]

        if len(missing_plugin_names):
            raise PluginError(
                "One or more plugin dependencies are not met: "
                f"{', '.join(missing_plugin_names)}. Please install them before continuing..."
            )

    @classmethod
    def install_files(cls):
        print("\nOFFSHOOT PLUGIN INSTALL: Installing files...\n")

        is_success = True
        install_messages = []

        installed_files = []
        pluggable_classes = offshoot.pluggable_classes()

        try:
            for file_dict in cls.files:
                plugin_file_path = "{}/{}/files/{}".replace("/", os.sep).format(
                    offshoot.config["file_paths"]["plugins"], cls.name, file_dict["path"]
                )

                # Pluggable Validation
                if "pluggable" in file_dict:
                    is_valid, messages = cls._validate_file_for_pluggable(
                        plugin_file_path, file_dict["pluggable"]
                    )

                    if not is_valid:
                        is_success = False
                        for message in messages:
                            install_messages.append(f"\n{file_dict['path']}: {message}")

                        continue

                installed_files.append(file_dict)

                # File Callback
                if "pluggable" in file_dict:
                    pluggable_classes[file_dict["pluggable"]].on_file_install(**file_dict)

            if not is_success:
                raise PluginError(
                    f"Offshoot Plugin File Install Errors: {''.join(install_messages)}"
                )
        except PluginError as e:
            print("\nThere was a problem during installation... Reverting!")

            # Trigger File Uninstall Callback
            for file_dict in installed_files:
                if "pluggable" in file_dict:
                    pluggable_classes[file_dict["pluggable"]].on_file_uninstall(**file_dict)

            manifest = offshoot.Manifest()
            manifest.remove_plugin(cls.name)

            raise e

    @classmethod
    def uninstall_files(cls):
        print("\nOFFSHOOT PLUGIN UNINSTALL: Uninstalling files...\n")

        for file_dict in cls.files:
            if "pluggable" in file_dict:
                offshoot.pluggable_classes()[file_dict["pluggable"]].on_file_uninstall(**file_dict)

    @classmethod
    def install_configuration(cls):
        config_path = offshoot.config["file_paths"]["config"]
        print(f"\n\nOFFSHOOT PLUGIN INSTALL: Updating configuration file ({config_path})...\n")

        if len(config_path.split(os.sep)) > 1:
            configuration_path = os.sep.join(config_path.split(os.sep)[:-1])

            if not os.path.isdir(configuration_path):
                raise PluginError(
                    f"The plugin configuration directory ('{configuration_path}') doesn't exist! "
                    "Either create it or modify the Offshoot configuration file to point to an "
                    "existing directory and restart the installation."
                )

        if not len(cls.config or {}):
            return None

        if offshoot.config["sandbox_configuration_keys"]:
            config = {}
            config[cls.name] = cls.config
        else:
            config = cls.config

        if not os.path.isfile(config_path):
            with open(config_path, "w") as f:
                f.write(yaml.dump(config))
        else:
            with open(config_path) as f:
                existing_config = yaml.safe_load(f.read()) or {}
                config = {**config, **existing_config}

            with open(config_path, "w") as f:
                f.write(yaml.dump(config, default_flow_style=False))

        print("Merging the following keys:")
        print(config)

    @classmethod
    def uninstall_configuration(cls):
        config_path = offshoot.config["file_paths"]["config"]
        print(f"\n\nOFFSHOOT PLUGIN UNINSTALL: Updating configuration file ({config_path})...\n")

        if len(config_path.split(os.sep)) > 1:
            configuration_path = os.sep.join(config_path.split(os.sep)[:-1])

            if not os.path.isdir(configuration_path):
                raise PluginError(
                    f"The plugin configuration directory ('{configuration_path}') doesn't exist! "
                    "Either create it or modify the Offshoot configuration file to point to an "
                    "existing directory and restart the installation."
                )

        if not len(cls.config or {}):
            return None

        if os.path.isfile(config_path):
            with open(config_path) as f:
                config = yaml.safe_load(f.read())

            if offshoot.config["sandbox_configuration_keys"]:
                config.pop(cls.name)
            else:
                for key in cls.config:
                    config.pop(key)

            with open(config_path, "w") as f:
                f.write(yaml.dump(config))

            print("Removing the following keys:")
            print(config)

    @classmethod
    def install_libraries(cls):
        libraries_file = offshoot.config["file_paths"]["libraries"]
        print(f"\n\nOFFSHOOT PLUGIN INSTALL: Updating libraries ({libraries_file})...\n")

        if len(libraries_file.split(os.sep)) > 1:
            libraries_path = os.sep.join(libraries_file.split(os.sep)[:-1])

            if not os.path.isdir(libraries_path):
                raise PluginError(
                    f"The plugin libraries directory ('{libraries_path}') doesn't exist! Either "
                    "create it or modify the Offshoot configuration file to point to an existing "
                    "directory and restart the installation."
                )

        if not len(cls.libraries or []):
            return None

        cls._write_plugin_requirement_blocks_to(libraries_file)

        print("Merging the following libraries:")
        print("\n".join(cls.libraries))

        print(
            f"\nLibraries updated successfully. Make sure to run 'pip install -r {libraries_file}' "
            "to fulfill the plugin requirements"
        )

    @classmethod
    def uninstall_libraries(cls):
        libraries_file = offshoot.config["file_paths"]["libraries"]
        print(f"\n\nOFFSHOOT PLUGIN UNINSTALL: Updating libraries ({libraries_file})...\n")

        if len(libraries_file.split(os.sep)) > 1:
            libraries_path = os.sep.join(libraries_file.split(os.sep)[:-1])

            if not os.path.isdir(libraries_path):
                raise PluginError(
                    f"The plugin libraries directory ('{libraries_path}') doesn't exist! Either "
                    "create it or modify the Offshoot configuration file to point to an existing "
                    "directory and restart the installation."
                )

        if not len(cls.libraries or []):
            return None

        cls._remove_plugin_requirement_block_from(libraries_file)

        print("Removing the following libraries:")
        print("\n".join(cls.libraries))

        print(
            f"\nLibraries updated successfully. Make sure to run 'pip install -r {libraries_file}' "
            "to fulfill the plugin requirements"
        )

    @classmethod
    def _validate_file_for_pluggable(cls, file_path, pluggable):
        pluggable_classes = offshoot.pluggable_classes()

        if pluggable not in pluggable_classes:
            raise PluginError(
                f"The Plugin definition specifies an invalid pluggable: {file_path} => {pluggable}"
            )

        pluggable_class = pluggable_classes[pluggable]

        return offshoot.validate_plugin_file(
            file_path, pluggable, pluggable_class.method_directives()
        )

    @classmethod
    def _generate_plugin_requirement_block(cls):
        requirement_lines = [f"### {cls.name} Requirements ###"]
        requirement_lines.extend(sorted(cls.libraries))
        requirement_lines.append("######")

        return requirement_lines

    @classmethod
    def _extract_plugin_requirement_blocks_from(cls, file_path):
        plugin_requirement_blocks = {}
        current_plugin = None

        if not os.path.isfile(file_path):
            return {}

        with open(file_path) as f:
            for line in f:
                if line == "":
                    continue

                if line.startswith("### "):
                    current_plugin = line.split("### ")[1].split(" ###")[0].strip()
                    plugin_requirement_blocks[current_plugin] = [line.strip()]
                    continue

                if line.startswith("######"):
                    plugin_requirement_blocks[current_plugin].append(line.strip())
                    current_plugin = None
                    continue

                if current_plugin:
                    plugin_requirement_blocks[current_plugin].append(line.strip())

        return plugin_requirement_blocks

    @classmethod
    def _write_plugin_requirement_blocks_to(cls, file_path):
        plugin_requirement_blocks = cls._extract_plugin_requirement_blocks_from(file_path)
        plugin_requirement_blocks[f"{cls.name} Requirements"] = (
            cls._generate_plugin_requirement_block()
        )

        with open(file_path, "w") as f:
            for requirements in plugin_requirement_blocks.values():
                f.write("\n".join(requirements))
                f.write("\n\n")

    @classmethod
    def _remove_plugin_requirement_block_from(cls, file_path):
        plugin_requirement_blocks = cls._extract_plugin_requirement_blocks_from(file_path)
        plugin_requirement_blocks.pop(f"{cls.name} Requirements")

        with open(file_path, "w") as f:
            for requirements in plugin_requirement_blocks.values():
                f.write("\n".join(requirements))
                f.write("\n\n")

import warnings

warnings.filterwarnings("ignore")  # Silence warnings in CLI

import os
import pathlib
import shutil
import subprocess

# Some imports are inline in CLI commands to keep initialization times low
import click

from serpent.utilities import (
    clear_terminal,
    display_serpent_logo,
    is_linux,
    is_windows,
)

# On Windows, disable the Fortran CTRL-C handler that gets installed with SciPy
if is_windows:
    os.environ["FOR_DISABLE_CONSOLE_CTRL_HANDLER"] = "T"

VERSION = "0.1.0"


@click.command(help="Perform Serpent.AI setup")
def setup():
    clear_terminal()
    display_serpent_logo()

    print("")
    print("Serpent.AI Setup")
    print("")

    data_path = _get_data_path()
    source_path = pathlib.Path(__file__).parent

    if data_path.exists():
        confirm = input(
            """It appears this machine has already been set up to use Serpent.AI.
Do you want to continue and remove all previous data? 
(One of: 'YES', 'NO') """
        )

        if confirm.lower() != "yes":
            return

        print("")
        print("Removing previous data...")
        print("")

        shutil.rmtree(data_path, ignore_errors=True)

    print("Creating Serpent.AI data directory...")
    data_path.mkdir()

    print("Populating Serpent.AI data directory...")

    data_path.joinpath("plugins/games").mkdir(parents=True, exist_ok=True)
    data_path.joinpath("plugins/game_agents").mkdir(parents=True, exist_ok=True)
    data_path.joinpath("plugins/rl_agents").mkdir(parents=True, exist_ok=True)

    data_path.joinpath("game_agents").mkdir()

    # TODO: Also copy bundled official plugins once we have them

    shutil.copy(
        source_path.joinpath("serpent/config/config.json"),
        data_path.joinpath("config.json"),
    )

    print("")
    print("Serpent.AI Setup Complete!")


@click.command(help="Update Serpent.AI to the latest version")
def update():
    import shlex

    clear_terminal()
    display_serpent_logo()
    print("")

    print("Updating Serpent.AI to the latest version...")
    print("")

    subprocess.call(shlex.split("pip install --upgrade SerpentAI"))

    # TODO: Handle files that were created with the setup commands
    #       and have likely been modified by the user. This is probably
    #       not an easy task.

    print("")
    print("Update Successful!")


@click.command(help="Serpent.AI GUI (now web-based)")
def gui():
    print("The GUI is now web-based. Use 'serpent dashboard' or 'serpent visual-debugger'.")


@click.command(help="Launch the Serpent.AI dashboard (local web app)")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8500, show_default=True)
@click.option("--project-key", default=None, help="Analytics project/topic to display")
def dashboard(host, port, project_key):
    from serpent.dashboard.app import run

    run(host=host, port=port, project_key=project_key)


@click.command(name="visual-debugger", help="Launch the visual debugger (local web app)")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8501, show_default=True)
@click.argument("buckets", nargs=-1)
def visual_debugger(host, port, buckets):
    from serpent.visual_debugger.server import run

    run(host=host, port=port, buckets=list(buckets) or None)


@click.command(help="Download additional tools and modules")
@click.argument("module")
def download(module):
    valid_modules = ("tesseract",)

    if module not in valid_modules:
        print(f"'{module}' is not a valid download module...")
        return

    if module == "tesseract":
        if is_windows():
            print("Downloading module 'tesseract' to tools directory...")
            _download_module(
                "https://github.com/SerpentAI/SerpentAI/releases/download/optional/tesseract_4.00.00a_win_amd64.zip",
                pathlib.Path("tools/tesseract.zip"),
            )
        elif is_linux():
            print(
                "Downloading module 'tesseract' not supported on Linux. Please install Tesseract with your package manager."
            )


@click.command(help="Clone a plugin from a git URL into the plugins directory")
@click.argument("url")
def download_plugin(url):
    from serpent import serpent

    serpent.download_plugin(url)


@click.command(help="Print the plugins directory path")
def show_plugins():
    from serpent import serpent

    serpent.show_plugins()


@click.command(help="List all locally-available plugins")
def plugins():
    from serpent import serpent

    serpent.plugins()


@click.command(help="List the installed game plugins")
def games():
    from serpent import serpent

    serpent.games()


@click.command(help="List the installed game agent plugins")
def game_agents():
    from serpent import serpent

    serpent.game_agents()


@click.command(help="List the built-in reinforcement learning agents")
def rl_agents():
    from serpent import serpent

    serpent.rl_agents()


@click.command(help="Display instructions from a game plugin")
@click.argument("game_name")
def game_instructions(game_name):
    from serpent import serpent

    serpent.game_instructions(game_name)


@click.command(help="Launch a game through a plugin")
@click.argument("game_name")
def launch(game_name):
    from serpent import serpent

    serpent.launch(game_name)


@click.command(help="Train a context classifier (training_type is currently 'context')")
@click.argument("training_type")
@click.argument("args", nargs=-1)
def train(training_type, args):
    from serpent import serpent

    serpent.train(training_type, *args)


@click.command(help="Play a game with a game agent through plugins")
@click.argument("game_name")
@click.argument("game_agent_name")
@click.option("--frame-handler", default=None)
def play(game_name, game_agent_name, frame_handler):
    from serpent import serpent

    serpent.play(game_name, game_agent_name, frame_handler=frame_handler)


@click.command(help="Record player input from a game")
@click.argument("game_name")
@click.argument("game_agent_name")
def record(game_name, game_agent_name):
    from serpent import serpent

    serpent.record(game_name, game_agent_name)


@click.command(name="grab-frames", help="Start the frame grabber (used internally by the play loop)")
@click.argument("width")
@click.argument("height")
@click.argument("x_offset")
@click.argument("y_offset")
@click.argument("pipeline_string", required=False, default=None)
def grab_frames(width, height, x_offset, y_offset, pipeline_string):
    from serpent import serpent

    serpent.grab_frames(width, height, x_offset, y_offset, pipeline_string)


@click.command(help="Generate code for a game or game agent plugin")
@click.argument("plugin_type")
def generate(plugin_type):
    from serpent import serpent

    serpent.generate(plugin_type)


@click.command(help="Capture frames, screen regions or contexts from a game")
@click.argument("capture_type")
@click.argument("game_name")
@click.option("--interval", default=1)
@click.option("--extra", default=None)
@click.option("--extra-2", default=None)
def capture(capture_type, game_name, interval, extra, extra_2):
    from serpent import serpent

    serpent.capture(capture_type, game_name, interval=interval, extra=extra, extra_2=extra_2)


@click.command(name="window-name", help="Find a game's window name")
def window_name():
    from serpent import serpent

    serpent.window_name()


@click.command(name="record-inputs", help="Start the input recorder")
def record_inputs():
    from serpent import serpent

    serpent.record_inputs()


@click.command(help="Activate a plugin")
@click.argument("plugin_name")
def activate(plugin_name):
    from serpent import serpent

    serpent.activate(plugin_name)


@click.command(help="Deactivate a plugin")
@click.argument("plugin_name")
def deactivate(plugin_name):
    from serpent import serpent

    serpent.deactivate(plugin_name)


@click.command(help="List the install status of the optional modules")
def modules():
    from serpent import serpent

    serpent.modules()


# SDK
# These commands are aimed at developers wanting to create plugins for Serpent.AI
@click.command(help="SDK - Perform Serpent.AI SDK setup in the current directory")
def sdk_setup():
    import serpent.ocr

    clear_terminal()
    display_serpent_logo()

    print("")
    print("Serpent.AI SDK Setup")
    print("")

    # First, check for required 3rd-party tools
    print("Checking for required 3rd-party tools...")

    have_tesseract = serpent.ocr.is_tesseract_available()

    print(f"Tesseract: {'FOUND' if have_tesseract else 'NOT FOUND'}")
    print("")

    if not have_tesseract:
        print("No Tesseract executable could be found... Setup cannot continue.")
        print("")

        if is_windows():
            print("For an easy installation of Tesseract, run 'serpent download tesseract")

    # Has setup already been performed?
    if pathlib.Path(".serpent-sdk").is_file():
        confirm = input(
            """The current directory has already been set up to use the Serpent.AI SDK.
Do you want to continue and potentially overwrite important files? 
(One of: 'YES', 'NO') """
        )

        if confirm.lower() != "yes":
            return

    current_path = pathlib.Path.cwd()
    source_path = pathlib.Path(__file__).parent

    # Config
    config_path = pathlib.Path("config_sdk.json")

    if config_path.is_file():
        config_path.unlink()

    shutil.copy(source_path.joinpath("serpent/config/config_sdk.json"), config_path)

    # Plugins
    plugins_path = current_path.joinpath("plugins")

    if plugins_path.is_dir():
        shutil.rmtree(plugins_path, ignore_errors=True)

    current_path.joinpath("plugins/games").mkdir(parents=True, exist_ok=True)
    current_path.joinpath("plugins/game_agents").mkdir(parents=True, exist_ok=True)
    current_path.joinpath("plugins/rl_agents").mkdir(parents=True, exist_ok=True)

    # Datasets
    datasets_path = current_path.joinpath("datasets")

    if datasets_path.is_dir():
        shutil.rmtree(datasets_path, ignore_errors=True)

    current_path.joinpath("datasets/frames").mkdir(parents=True, exist_ok=True)
    current_path.joinpath("datasets/recordings").mkdir(parents=True, exist_ok=True)

    # Dot File
    open(".serpent-sdk", "w").close()

    print("")
    print("Serpent.AI SDK Setup Complete!")


@click.command(help="SDK - Find the window name of a game")
def sdk_window_name():
    # TODO: Implement
    pass


@click.command(help="SDK - CUDA test for Serpent.AI")
def sdk_test_cuda():
    import torch

    # TODO: Try to also detect incompatible hardware. This likely just detects if CUDA
    #       is bundled with the installed PyTorch version
    if torch.cuda.is_available():
        print("Success! CUDA can be used by Serpent.AI")
    else:
        print("Failure! CUDA cannot be used by Serpent.AI")


@click.command(help="SDK - Test Serpent.AI input capture")
def sdk_test_input_capture():
    # TODO: Implement
    pass


@click.command(help="SDK - Capture game frames")
def sdk_capture():
    # TODO: Implement
    pass


@click.command(help="SDK - Generate skeleton for a game plugin")
def sdk_generate_game_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Generate skeleton for a game agent plugin")
def sdk_generate_game_agent_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Generate skeleton for a RL agent plugin")
def sdk_generate_rl_agent_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Package game plugin to .spg file")
def sdk_package_game_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Package game agent plugin to .spga file")
def sdk_package_game_agent_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Package RL agent plugin to .sprla file")
def sdk_package_rl_agent_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Install a plugin on the system")
def sdk_install_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Uninstall a plugin from the system")
def sdk_uninstall_plugin():
    # TODO: Implement
    pass


def _download_module(url, file_path):
    import requests
    import tqdm

    path = file_path.parent
    path.mkdir(parents=True, exist_ok=True)

    r = requests.get(url, stream=True)

    with open(file_path, "wb") as f:
        progress = tqdm.tqdm(
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            total=int(r.headers["Content-Length"]),
        )

        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                progress.update(len(chunk))
                f.write(chunk)

        progress.close()

    if str(file_path.as_posix()).endswith(".zip"):
        import zipfile

        with zipfile.ZipFile(file_path, "r") as z:
            z.extractall(path)

        file_path.unlink()

    print("Download complete!")


def _get_data_path():
    if is_windows():
        data_path = pathlib.Path(os.getenv("APPDATA")).joinpath("Serpent.AI")
    elif is_linux():
        data_path = pathlib.Path(os.getenv("HOME")).joinpath(".serpent")

    return data_path.absolute()


@click.group(invoke_without_command=True)
@click.option("--version", help="Shows Serpent.AI version", is_flag=True)
@click.option("--help", help="Shows Serpent.AI CLI commands", is_flag=True)
@click.pass_context
def cli(context, version, help):
    if version:
        print(VERSION)
        return

    if context.invoked_subcommand is None:
        print(context.get_help())
        return


# General
cli.add_command(setup)
cli.add_command(update)
cli.add_command(gui)
cli.add_command(dashboard)
cli.add_command(visual_debugger)
cli.add_command(download)
cli.add_command(show_plugins)
cli.add_command(plugins)
cli.add_command(games)
cli.add_command(game_agents)
cli.add_command(rl_agents)
cli.add_command(game_instructions)
cli.add_command(launch)
cli.add_command(train)
cli.add_command(play)
cli.add_command(record)
cli.add_command(grab_frames)
cli.add_command(generate)
cli.add_command(capture)
cli.add_command(window_name)
cli.add_command(record_inputs)
cli.add_command(activate)
cli.add_command(deactivate)
cli.add_command(modules)

# SDK
cli.add_command(sdk_setup)
cli.add_command(sdk_window_name)
cli.add_command(sdk_test_cuda)
cli.add_command(sdk_test_input_capture)
cli.add_command(sdk_capture)
cli.add_command(sdk_generate_game_plugin)
cli.add_command(sdk_generate_game_agent_plugin)
cli.add_command(sdk_generate_rl_agent_plugin)
cli.add_command(sdk_package_game_plugin)
cli.add_command(sdk_package_game_agent_plugin)
cli.add_command(sdk_package_rl_agent_plugin)
cli.add_command(sdk_install_plugin)
cli.add_command(sdk_uninstall_plugin)


if __name__ == "__main__":
    cli()

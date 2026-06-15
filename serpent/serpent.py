#!/usr/bin/env python
"""Serpent command *implementations*.

These functions are the implementation library behind the ``serpent`` CLI
(``cli.py``); they are not a CLI themselves. The previous parallel dispatcher
(``execute()`` + command mappings + ``__main__``) was removed during the CLI
consolidation — ``cli.py`` is the single entry point.
"""
import os
import sys
import shutil
import subprocess
import shlex
import time

import offshoot

from serpent.utilities import clear_terminal, display_serpent_logo, is_linux, is_windows

from serpent.window_controller import WindowController

# Add the current working directory to sys.path to discover user plugins!
sys.path.insert(0, os.getcwd())

# On Windows, disable the Fortran CTRL-C handler that gets installed with SciPy
if is_windows:
    os.environ['FOR_DISABLE_CONSOLE_CTRL_HANDLER'] = 'T'


def setup(module=None):
    clear_terminal()
    display_serpent_logo()
    print("")

    if module is None:
        setup_base()
    elif module == "ocr":
        setup_ocr()
    elif module == "gui":
        setup_gui()
    elif module == "ml":
        setup_ml()
    elif module == "dashboard":
        setup_dashboard()
    else:
        print(f"Invalid Setup Module: {module}")


def setup_base():
    # Copy Config Templates
    print("Creating Configuration Files...")

    first_run = True

    for root, directories, files in os.walk(os.getcwd()):
        for file in files:
            if file == "offshoot.yml":
                first_run = False
                break

        if not first_run:
            break

    if not first_run:
        confirm = input("It appears that the setup process had already been performed. Are you sure you want to proceed? Some important files will be overwritten! (One of: 'YES', 'NO'):\n")

        if confirm not in ["YES", "NO"]:
            confirm = "NO"

        if confirm == "NO":
            sys.exit()

    shutil.rmtree(os.path.join(os.getcwd(), "config"), ignore_errors=True)

    shutil.copytree(
        os.path.join(os.path.dirname(__file__), "config"),
        os.path.join(os.getcwd(), "config")
    )

    # Copy Offshoot Files
    shutil.copy(
        os.path.join(os.path.dirname(__file__), "offshoot.yml"),
        os.path.join(os.getcwd(), "offshoot.yml")
    )

    shutil.copy(
        os.path.join(os.path.dirname(__file__), "offshoot.manifest.json"),
        os.path.join(os.getcwd(), "offshoot.manifest.json")
    )

    # Generate Platform-Specific requirements.txt
    if is_linux():
        shutil.copy(
            os.path.join(os.path.dirname(__file__), "requirements.linux.txt"),
            os.path.join(os.getcwd(), "requirements.txt")
        )
    elif is_windows():
        shutil.copy(
            os.path.join(os.path.dirname(__file__), "requirements.win32.txt"),
            os.path.join(os.getcwd(), "requirements.txt")
        )

    # Install the dependencies
    print("Installing dependencies...")

    if is_linux():
        subprocess.call(shlex.split("pip install python-xlib"))
    elif is_windows():
        # Anaconda Packages
        subprocess.call(shlex.split("conda install numpy scipy scikit-image scikit-learn h5py -y"), shell=True)

    subprocess.call(shlex.split("pip install -r requirements.txt"))

    # Create Dataset Directories
    os.makedirs(os.path.join(os.getcwd(), "datasets/collect_frames"), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), "datasets/collect_frames_for_context"), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), "datasets/current"), exist_ok=True)

def setup_ocr():
    if is_linux():
        print("Before continuing with the OCR module setup, please read and perform the installation steps from the wiki: https://github.com/SerpentAI/SerpentAI/wiki/Linux-Installation-Guide#ocr")
    elif is_windows():
        print("Before continuing with the OCR module setup, please read and perform the installation steps from the wiki: https://github.com/SerpentAI/SerpentAI/wiki/Windows-Installation-Guide#ocr")

    print("")
    input("Press Enter to continue...")

    if is_linux():
        subprocess.call(shlex.split("pip install tesserocr"))
    elif is_windows():
        subprocess.call(shlex.split("pip install pytesseract"))

    print("")
    print("OCR module setup complete!")


def setup_gui():
    # The visual debugger is now a built-in FastAPI web app (no Kivy/CEF install).
    print("The visual debugger is now a built-in web app — no separate GUI setup is needed.")
    print("Run it with: serpent visual-debugger")


def setup_ml():
    # PyTorch (device auto-detected) is a core dependency now; TensorFlow was dropped.
    print("PyTorch is bundled as a core dependency (device auto-detected) — no separate ML setup.")


def setup_dashboard():
    # The dashboard is now a built-in FastAPI web app (no CEF/Kivy/Pony install).
    print("The dashboard is now a built-in web app — no separate dashboard setup is needed.")
    print("Run it with: serpent dashboard")


# TODO: Bring this up to date for dev branch
def update():
    clear_terminal()
    display_serpent_logo()
    print("")

    print("Updating Serpent.AI to the latest version...")

    subprocess.call(shlex.split("pip install --upgrade SerpentAI"))

    if is_linux():
        shutil.copy(
            os.path.join(os.path.dirname(__file__), "requirements.linux.txt"),
            os.path.join(os.getcwd(), "requirements.txt")
        )
    elif is_windows():
        shutil.copy(
            os.path.join(os.path.dirname(__file__), "requirements.win32.txt"),
            os.path.join(os.getcwd(), "requirements.txt")
        )

    subprocess.call(shlex.split("pip install -r requirements.txt"))

    import yaml

    with open(os.path.join(os.path.dirname(__file__), "config", "config.yml"), "r") as f:
        serpent_config = yaml.safe_load(f) or {}

    with open(os.path.join(os.getcwd(), "config", "config.yml"), "r") as f:
        user_config = yaml.safe_load(f) or {}

    config_changed = False

    for key, value in serpent_config.items():
        if key not in user_config:
            user_config[key] = value
            config_changed = True

    if config_changed:
        with open(os.path.join(os.getcwd(), "config", "config.yml"), "w") as f:
            f.write(yaml.dump(user_config)) 


def modules():
    import importlib
    exists = importlib.util.find_spec

    serpent_modules = {
        "OCR": (exists("tesserocr") or exists("pytesseract")) is not None,
        "GUI": exists("kivy") is not None,
        "ML": exists("keras") is not None and exists("tensorforce") is not None,
        "DASHBOARD": exists("kivy") is not None and exists("cefpython3") is not None and exists("pony") is not None
    }

    clear_terminal()
    display_serpent_logo()
    print("")

    print("Installed Serpent.AI Modules:")
    print("")

    print(f"OCR => {'Yes' if serpent_modules['OCR'] else 'No; Install with `serpent setup ocr` if needed'}")
    print(f"GUI => {'Yes' if serpent_modules['GUI'] else 'No; Install with `serpent setup gui` if needed'}")
    print(f"ML => {'Yes' if serpent_modules['ML'] else 'No; Install with `serpent setup ml` if needed'}")
    print(f"DASHBOARD => {'Yes' if serpent_modules['DASHBOARD'] else 'No; Install with `serpent setup dashboard` if needed'}")

    print("")


def grab_frames(width, height, x_offset, y_offset, pipeline_string=None):
    from serpent.frame_grabber import FrameGrabber

    frame_grabber = FrameGrabber(
        width=int(width),
        height=int(height),
        x_offset=int(x_offset),
        y_offset=int(y_offset),
        pipeline_string=pipeline_string
    )

    frame_grabber.start()


def activate(plugin_name):
    subprocess.call(shlex.split(f"offshoot install {plugin_name}"))


def deactivate(plugin_name):
    subprocess.call(shlex.split(f"offshoot uninstall {plugin_name}"))


def plugins():
    plugin_names = set()

    for root, directories, files in os.walk(offshoot.config['file_paths']['plugins']):
        if root != offshoot.config['file_paths']['plugins']:
            break

        for directory in directories:
            plugin_names.add(directory)

    manifest_plugin_names = set()

    for plugin_name in offshoot.Manifest().list_plugins().keys():
        manifest_plugin_names.add(plugin_name)

    active_plugins = plugin_names & manifest_plugin_names
    inactive_plugins = plugin_names - manifest_plugin_names

    print("\nACTIVE Plugins:\n")
    print("\n".join(active_plugins or ["No active plugins..."]))

    print("\nINACTIVE Plugins:\n")
    print("\n".join(inactive_plugins or ["No inactive plugins..."]))


def launch(game_name):
    game = initialize_game(game_name)
    game.launch()


def play(game_name, game_agent_name, frame_handler=None):
    game = initialize_game(game_name)
    game.launch(dry_run=True)

    game_agent_class_mapping = offshoot.discover("GameAgent", selection=game_agent_name)
    game_agent_class = game_agent_class_mapping.get(game_agent_name)

    if game_agent_class is None:
        raise Exception(f"Game Agent '{game_agent_name}' wasn't found. Make sure the plugin is installed.")

    game.play(game_agent_class_name=game_agent_name, frame_handler=frame_handler)


def record(game_name, game_agent_name, frame_count=4, frame_spacing=4):
    game = initialize_game(game_name)
    game.launch(dry_run=True)

    game.play(
        game_agent_class_name=game_agent_name,
        frame_handler="RECORD",
        frame_count=int(frame_count),
        frame_spacing=int(frame_spacing)
    )


def generate(plugin_type):
    if plugin_type == "game":
        generate_game_plugin()
    elif plugin_type == "game_agent":
        generate_game_agent_plugin()
    else:
        raise Exception(f"'{plugin_type}' is not a valid plugin type...")


def train(training_type, *args):
    if training_type == "context":
        train_context(*args)


def capture(capture_type, game_name, interval=1, extra=None, extra_2=None):
    game = initialize_game(game_name)
    game.launch(dry_run=True)

    if capture_type not in ["frame", "context", "region"]:
        raise Exception("Invalid capture command.")

    if capture_type == "frame":
        game.play(frame_handler="COLLECT_FRAMES", interval=float(interval))
    elif capture_type == "context":
        game.play(frame_handler="COLLECT_FRAMES_FOR_CONTEXT", interval=float(interval), context=extra, screen_region=extra_2)
    elif capture_type == "region":
        game.play(frame_handler="COLLECT_FRAME_REGIONS", interval=float(interval), region=extra)


def visual_debugger(*buckets):
    from serpent.visual_debugger.server import run
    run(buckets=list(buckets) or None)


def window_name():
    clear_terminal()
    print("Open the Game manually.")

    input("\nPress Enter and then focus the game window...")

    window_controller = WindowController()

    time.sleep(5)

    focused_window_name = window_controller.get_focused_window_name()

    print(f"\nGame Window Detected! Please set the kwargs['window_name'] value in the Game plugin to:")
    print("\n" + focused_window_name + "\n")


def record_inputs():
    from serpent.input_recorder import InputRecorder

    input_recorder = InputRecorder()

    input_recorder.start()


def dashboard(project_key=None):
    from serpent.dashboard.app import run
    run(project_key=project_key)


def generate_game_plugin():
    clear_terminal()
    display_serpent_logo()
    print("")

    game_name = input("What is the name of the game? (Titleized, No Spaces i.e. AwesomeGame): \n")
    game_platform = input("How is the game launched? (One of: 'steam', 'executable', 'web_browser'): \n")

    if game_name in [None, ""]:
        raise Exception("Invalid game name.")

    if game_platform not in ["steam", "executable", "web_browser"]:
        raise Exception("Invalid game platform.")

    prepare_game_plugin(game_name, game_platform)

    subprocess.call(shlex.split(f"serpent activate Serpent{game_name}GamePlugin"))


def generate_game_agent_plugin():
    clear_terminal()
    display_serpent_logo()
    print("")

    game_agent_name = input("What is the name of the game agent? (Titleized, No Spaces i.e. AwesomeGameAgent): \n")

    if game_agent_name in [None, ""]:
        raise Exception("Invalid game agent name.")

    prepare_game_agent_plugin(game_agent_name)

    subprocess.call(shlex.split(f"serpent activate Serpent{game_agent_name}GameAgentPlugin"))


def prepare_game_plugin(game_name, game_platform):
    plugin_destination_path = f"{offshoot.config['file_paths']['plugins']}/Serpent{game_name}GamePlugin".replace("/", os.sep)

    shutil.copytree(
        os.path.join(os.path.dirname(__file__), "templates/SerpentGamePlugin".replace("/", os.sep)),
        plugin_destination_path
    )

    # Plugin Definition
    with open(f"{plugin_destination_path}/plugin.py".replace("/", os.sep), "r") as f:
        contents = f.read()

    contents = contents.replace("SerpentGamePlugin", f"Serpent{game_name}GamePlugin")
    contents = contents.replace("serpent_game.py", f"serpent_{game_name}_game.py")

    with open(f"{plugin_destination_path}/plugin.py".replace("/", os.sep), "w") as f:
        f.write(contents)

    shutil.move(f"{plugin_destination_path}/files/serpent_game.py".replace("/", os.sep), f"{plugin_destination_path}/files/serpent_{game_name}_game.py".replace("/", os.sep))

    # Game
    with open(f"{plugin_destination_path}/files/serpent_{game_name}_game.py".replace("/", os.sep), "r") as f:
        contents = f.read()

    contents = contents.replace("SerpentGame", f"Serpent{game_name}Game")
    contents = contents.replace("MyGameAPI", f"{game_name}API")

    if game_platform == "steam":
        contents = contents.replace("PLATFORM", "steam")

        contents = contents.replace("from serpent.game_launchers.web_browser_game_launcher import WebBrowser", "")
        contents = contents.replace('kwargs["executable_path"] = "EXECUTABLE_PATH"', "")
        contents = contents.replace('kwargs["url"] = "URL"', "")
        contents = contents.replace('kwargs["browser"] = WebBrowser.DEFAULT', "")
    elif game_platform == "executable":
        contents = contents.replace("PLATFORM", "executable")

        contents = contents.replace("from serpent.game_launchers.web_browser_game_launcher import WebBrowser", "")
        contents = contents.replace('kwargs["app_id"] = "APP_ID"', "")
        contents = contents.replace('kwargs["app_args"] = None', "")
        contents = contents.replace('kwargs["url"] = "URL"', "")
        contents = contents.replace('kwargs["browser"] = WebBrowser.DEFAULT', "")
    elif game_platform == "web_browser":
        contents = contents.replace("PLATFORM", "web_browser")

        contents = contents.replace('kwargs["app_id"] = "APP_ID"', "")
        contents = contents.replace('kwargs["app_args"] = None', "")
        contents = contents.replace('kwargs["executable_path"] = "EXECUTABLE_PATH"', "")

    with open(f"{plugin_destination_path}/files/serpent_{game_name}_game.py".replace("/", os.sep), "w") as f:
        f.write(contents)

    # Game API
    with open(f"{plugin_destination_path}/files/api/api.py".replace("/", os.sep), "r") as f:
        contents = f.read()

    contents = contents.replace("MyGameAPI", f"{game_name}API")

    with open(f"{plugin_destination_path}/files/api/api.py".replace("/", os.sep), "w") as f:
        f.write(contents)


def prepare_game_agent_plugin(game_agent_name):
    plugin_destination_path = f"{offshoot.config['file_paths']['plugins']}/Serpent{game_agent_name}GameAgentPlugin".replace("/", os.sep)

    shutil.copytree(
        os.path.join(os.path.dirname(__file__), "templates/SerpentGameAgentPlugin".replace("/", os.sep)),
        plugin_destination_path
    )

    with open(f"{plugin_destination_path}/plugin.py", "r") as f:
        contents = f.read()

    contents = contents.replace("SerpentGameAgentPlugin", f"Serpent{game_agent_name}GameAgentPlugin")
    contents = contents.replace("serpent_game_agent.py", f"serpent_{game_agent_name}_game_agent.py")

    with open(f"{plugin_destination_path}/plugin.py", "w") as f:
        f.write(contents)

    shutil.move(f"{plugin_destination_path}/files/serpent_game_agent.py", f"{plugin_destination_path}/files/serpent_{game_agent_name}_game_agent.py")

    with open(f"{plugin_destination_path}/files/serpent_{game_agent_name}_game_agent.py", "r") as f:
        contents = f.read()

    contents = contents.replace("SerpentGameAgent", f"Serpent{game_agent_name}GameAgent")

    with open(f"{plugin_destination_path}/files/serpent_{game_agent_name}_game_agent.py", "w") as f:
        f.write(contents)


def train_context(epochs=3, validate=True, autosave=False):
    if validate not in [True, "True", False, "False"]:
        raise ValueError("'validate' should be True or False")

    if autosave not in [True, "True", False, "False"]:
        raise ValueError("'autosave' should be True or False")

    from serpent.machine_learning.context_classification.context_classifier import ContextClassifier
    ContextClassifier.executable_train(epochs=int(epochs), validate=argv_is_true(validate), autosave=argv_is_true(autosave))


def initialize_game(game_name):
    game_class_name = f"Serpent{game_name}Game"

    game_class_mapping = offshoot.discover("Game")
    game_class = game_class_mapping.get(game_class_name)

    if game_class is None:
        raise Exception(f"Game '{game_name}' wasn't found. Make sure the plugin is installed.")

    game = game_class()

    return game


def argv_is_true(arg):
    return arg in [True, "True"]

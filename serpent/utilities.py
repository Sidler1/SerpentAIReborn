import sys
import subprocess

import enum


class SerpentError(BaseException):
    pass


class OperatingSystem(enum.Enum):
    LINUX = 0
    WINDOWS = 1


def operating_system():
    if sys.platform in ["linux", "linux2"]:
        return OperatingSystem.LINUX
    elif sys.platform == "win32":
        return OperatingSystem.WINDOWS


def is_linux():
    return operating_system().name == "LINUX"


def is_windows():
    return operating_system().name == "WINDOWS"


def clear_terminal():
    if is_linux():
        print("\033c")
    elif is_windows():
        subprocess.call(["cls"], shell=True)


def display_serpent_logo():
    print("""
                         ▄▄▄▄█████▄▄▄
                     ▄█████████▀▀`  ,
                  ▄██████████",▄▄▄██  █ L
                ╓██████████▀╓█████▀  ██ ▌ j
               ▄██████████▀▄███▀▀ ▄███ █▌ ▐▌
              ▐██████████   ▄▄▄█████▀╓██  ██
              █████████▀▄▄███████▀`▄███` ██▌▐U
              ███████▀,███▀▀▀` ▄▄████▀ ,███ █`╒
              ▀▀▐▄▄   `     ╓██████▀  ▄███ ██ █
                          ▄████▀▀-  ▄███▀╓██-▐█
                      ^▀▀▀▀▀- ,▄██  ██▀,███`╒██
                            ▐████" ▀▀▄████ ▄██▌
                            ▐███▀ ,▄████▀ ▄██▌
                            ███▀ ╓████" ▄███▀
                           ▐██  ▄██▀ ,▄████▀
                          ▄█▀ ,▀▀ ▄▄█████▀
                        .▀   ,▄▄███████▀          ,    ,
                       ,▄▄▄█████████▀-           ███  ▐█
                 ,▄▄████████████▀▀              ██ █▌ ▐█
             ▄▄███████████▀▀▀                  ▄█▀▀▀█▄▐█
          ▄███████▀▀▀                          ``      `
       ,▄███▀▀'
      ▄██▀
     █▀`
    ▐▀
    `
    """)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

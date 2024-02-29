import multiprocessing
import os
import signal
import subprocess
import locale
from pathlib import Path
import sys
import time
import webbrowser
import logging

from pathtub import ensure
import uvicorn

from movx.core import is_linux, is_win
import importlib.metadata

version = importlib.metadata.version("movx")

current_path = Path(__file__).parent

SERVER_MODE = True
APP_MODE = False

WIN_WAVE_FOLDER = Path(__file__).parent / "vendor" / "wave-1.0.0-win-amd64"
LINUX_WAVE_FOLDER = Path(__file__).parent / "vendor" / "wave-1.0.0-linux-amd64"

WAVE_PATH = LINUX_WAVE_FOLDER

if is_win():
    WAVE_PATH = WIN_WAVE_FOLDER

WAVE_DATA_PATH = WAVE_PATH / "data" / "f"

ENTRY_POINT = "movx.gui.main:main"

LOCAL_ADDR = "127.0.0.1"
LOCAL_PORT = 10101

LOCAL_URL = "http://" + LOCAL_ADDR + ":" + str(LOCAL_PORT)

WIN_DEPS = {
    "asdcplib": current_path / "./vendor/asdcplib-2.7.19-tools/",
    "mediainfo": current_path / "./vendor/MediaInfo_CLI_22.12_Windows_x64/",
    "sox": current_path / "./vendor/sox-14.4.2-win32/sox-14.4.2/",
}

locale.setlocale(locale.LC_ALL, "")

logging.basicConfig(
    format="%(levelname)s\t[%(asctime)s]\t%(message)s", level=logging.WARNING
)


dotmovx = Path.home() / ".movx"

dotmovx.mkdir(exist_ok=True)


def shutdown(sig, frame):
    print("movx shutting down...")
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown)


def include_deps():
    print("checking dependencies... ", end="")

    if is_win():
        for n, p in WIN_DEPS.items():
            if p.is_dir():
                ensure(str(p.resolve()))
            else:
                print("Fatal: %s dependency not found" % n)
                exit(0)

    if is_linux():
        if (
            subprocess.call(["hash", "asdcp-info"], shell=True)
            + subprocess.call(["hash", "asdcp-test"], shell=True)
            > 0
        ):
            print(
                "Fatal Error: Please install 'asdcplib' (gihub.com/cincert/asdcplib) package on this system"
            )
            exit(0)

        if subprocess.call(["hash", "mediainfo"], shell=True) > 0:
            print("Fatal Error: Please install 'mediainfo' package on this system")
            exit(0)

        if subprocess.call(["hash", "sox"], shell=True) > 0:
            print("Fatal Error: Please install 'sox' package on this system")
            exit(0)

    print("OK")


include_deps()


def start_waved(logs=False):
    from movx.core import db, locations, dcps

    print("starting Wave Server")
    os.environ["H2O_WAVE_NO_LOG"] = "0" if logs else "1"
    cwd = os.getcwd()
    waved_exe = "waved"
    if is_win():
        waved_exe = "waved.exe"
    os.chdir(WAVE_PATH)
    path = WAVE_PATH / waved_exe
    assets_path = (
        "/assets/@%s" % "d:/dev/movx/movx/assets"
    )  # (Path(__file__).parent / "assets/")
    subp = [path, LOCAL_ADDR]  # "-public-dir", assets_path]
    print(subp)
    try:
        subprocess.Popen(subp)
    except Exception as e:
        print("Fatal Error while starting waved server: %s" % e)
        exit(0)
    os.chdir(cwd)


class UvicornServer(multiprocessing.Process):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.server = uvicorn.Server(config=config)
        # self.server.install_signal_handlers()
        self.daemon = True

    def stop(self):
        self.terminate()

    def run(self, *args, **kwargs):
        self.server.run()


def start_serve(log_level="warning", reload=False, browse=False):
    print("Startin MovX Server")
    start_waved()
    if browse:
        webbrowser.open(LOCAL_URL)
    else:
        print("")
    uvicorn.run(ENTRY_POINT, log_level=log_level, reload=reload)


def start_agent(host="0.0.0.0", port=11011, debug=False, noblock=False):
    config = uvicorn.Config(
        "movx.core.agent:app", host=host, port=port, log_level="warning"
    )
    if noblock:
        instance = UvicornServer(config)
        instance.start()
    else:
        server = uvicorn.Server(config=config)

        server.run()

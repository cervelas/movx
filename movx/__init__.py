import multiprocessing
import os
import subprocess
import locale
from pathlib import Path
import sys
import webbrowser
import logging

from pathtub import ensure
import uvicorn
import webview

from movx.core import db

SERVER_MODE = True
APP_MODE = False

WIN_WAVE_FOLDER = Path(__file__).parent / "vendor" / "wave-1.0.0-win-amd64"
LINUX_WAVE_FOLDER = Path(__file__).parent / "vendor" / "wave-0.24.2-linux-amd64"

ENTRY_POINT = "movx.gui.main:main"

LOCAL_ADDR = "http://127.0.0.1:10101/"

current_path = Path(__file__).parent


locale.setlocale(locale.LC_ALL, "")

logging.basicConfig(
    format="%(levelname)s\t[%(asctime)s]\t%(message)s", level=logging.INFO
)

if sys.platform.startswith("win"):
    ensure(str(Path(current_path / "./vendor/asdcplib-2.7.19-tools/").absolute()))
    ensure(
        str(Path(current_path / "./vendor/MediaInfo_CLI_22.12_Windows_x64/").absolute())
    )
    ensure(str(Path(current_path / "./vendor/sox-14.4.2-win32/sox-14.4.2/").absolute()))


def start_waved(logs=False):
    print("starting Wave Server")
    os.environ["H2O_WAVE_NO_LOG"] = "0" if logs else "1"
    cwd = os.getcwd()
    waved_exe = "waved"
    waved_path = LINUX_WAVE_FOLDER
    if sys.platform.startswith("win"):
        waved_exe = "waved.exe"
        waved_path = WIN_WAVE_FOLDER
    os.chdir(waved_path)
    path = waved_path / waved_exe
    assets_path = (
        "/assets/@%s" % "d:/dev/movx/movx/assets"
    )  # (Path(__file__).parent / "assets/")
    print(assets_path)
    subprocess.Popen([path.absolute(), "0.0.0.0", "-public-dir", assets_path])
    os.chdir(cwd)


class UvicornServer(multiprocessing.Process):
    def __init__(self, config):
        super().__init__()
        self.server = uvicorn.Server(config=config)
        self.config = config

    def stop(self):
        self.terminate()

    def run(self, *args, **kwargs):
        self.server.run()


def start_serve(log_level="warning", reload=False, browse=False):
    print("Startin movx in Server Mode")
    start_waved()
    if browse:
        webbrowser.open(LOCAL_ADDR)
    else:
        print("")
    uvicorn.run(ENTRY_POINT, log_level=log_level, reload=reload)


def start_app(debug=False, reload=False):
    print("Starting movx in Application Mode")
    start_waved()

    config = uvicorn.Config(ENTRY_POINT, port=8000, log_level="warning", reload=reload)
    instance = UvicornServer(config=config)
    instance.start()

    SERVER_MODE = False
    APP_MODE = True
    webview.create_window("MOVX", LOCAL_ADDR)
    webview.start(debug=debug)

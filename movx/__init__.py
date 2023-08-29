import multiprocessing
import os
import subprocess
import locale
from pathlib import Path
import sys

from pathtub import ensure
import uvicorn


current_path = Path(__file__).parent

locale.setlocale(locale.LC_ALL, "")

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
    waved_path = Path(__file__).parent / "vendor" / "wave-0.24.2-linux-amd64"
    if sys.platform.startswith("win"):
        waved_exe = "waved.exe"
        waved_path = Path(__file__).parent / "vendor" / "wave-0.26.2-win-amd64"
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

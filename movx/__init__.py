from h2o_wave import main
import sys

from pathlib import Path
from pathtub import ensure

current_path = Path(__file__).parent

from pathlib import Path
if sys.platform.startswith('win'):
    ensure(str(Path(current_path / "./vendor/asdcplib-2.7.19-tools/").absolute()))
    ensure(str(Path(current_path / "./vendor/MediaInfo_CLI_22.12_Windows_x64/").absolute()))
    ensure(str(Path(current_path / "./vendor/sox-14.4.2-win32/sox-14.4.2/").absolute()))
import movx.ui.main
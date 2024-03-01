import subprocess
import sys
from pathlib import Path

def update():
    cwd = Path(__file__).parent.parent
    print("updating movx from git.")
    subprocess.call(["git", "status"], cwd=cwd, shell=False)
    subprocess.call(["git", "pull"], cwd=cwd, shell=False)
    subprocess.call(["git", "status"], cwd=cwd, shell=False)
    print("update pip")
    subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], cwd=cwd, shell=False)
    print("reinstall movx python package.")
    subprocess.call([sys.executable, "-m", "pip", "install", "-e", "."], cwd=cwd, shell=False)
    print("restarting service")
    
    subprocess.call(["systemctl", "--user", "restart", "movx.service"], cwd=cwd, shell=False)
    exit(0)

if __name__ == "__main__":
    update()
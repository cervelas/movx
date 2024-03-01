import subprocess
import sys
from pathlib import Path

def update():
    cwd = Path(__file__).parent.parent
    print("updating movx from git.")
    subprocess.call(["git", "status"], cwd=cwd, shell=True)
    subprocess.call(["git", "pull"], cwd=cwd, shell=True)
    subprocess.call(["git", "status"], cwd=cwd, shell=True)
    print("update pip")
    subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], cwd=cwd, shell=True)
    print("reinstall movx python package.")
    subprocess.call([sys.executable, "-m", "pip", "install", "-e", "."], cwd=cwd, shell=True)
    print("restarting service")
    
    subprocess.call(["service", "movx", "restart"], cwd=cwd, shell=True)
    exit(0)

if __name__ == "__main__":
    update()
import subprocess
import sys
from pathlib import Path

def update():
    cwd = Path(__file__).parent.parent
    print("updating movx from git.")
    subprocess.check_call(["git", "status"], cwd=cwd, shell=True)
    subprocess.check_call(["git", "pull"], cwd=cwd, shell=True)
    subprocess.check_call(["git", "status"], cwd=cwd, shell=True)
    print("update pip")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], cwd=cwd, shell=True)
    print("reinstall movx python package.")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."], cwd=cwd, shell=True)
    print("restarting service")
    
    subprocess.check_call(["service", "movx", "restart"], cwd=cwd, shell=True)
    exit(0)

if __name__ == "__main__":
    update()
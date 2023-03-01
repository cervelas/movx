import os
import sys
import pprint
import subprocess
import uvicorn
import webbrowser

import click
from h2o_wave import app
from movx.core.movx import movx

def start_waved(logs=False):
    print("starting Wave Server")
    os.environ["H2O_WAVE_NO_LOG"] = "0" if logs else "1"
    cwd = os.getcwd()
    waved_exe = "waved"
    waved_path = os.path.join(os.path.dirname(__file__), "./vendor/wave-0.24.2-linux-amd64/")
    if sys.platform.startswith('win'):
        waved_exe = "waved.exe"
        waved_path = os.path.join(os.path.dirname(__file__), "./vendor/wave-0.24.2-windows-amd64/")
    os.chdir(waved_path)
    subprocess.Popen([os.path.join(waved_path, waved_exe), "0.0.0.0"])
    os.chdir(cwd)

def start_serve(reload=False):
    uvicorn.run("movx.ui.main:main", log_level="warning", reload=reload)

@click.group()
def main():
    pass

@main.command()
def serve():
    start_waved()
    print("Starting application")
    start_serve()

@main.command()
def run():
    start_waved()
    print("Starting application")
    webbrowser.open("http://127.0.0.1:10101/movx")
    uvicorn.run("movx.ui.main:main", log_level="warning", reload=True)

@main.command()
@click.argument("path")
def scan(path):
    movx.update_locations("NEW", path)
    movx.scan()
    movx.pretty_print()
    

@main.command()
@click.argument("path")
def check(path):
    movx.update_locations("NEW", path)
    movx.scan()
    movx.check()
    movx.pretty_print()

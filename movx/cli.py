import webbrowser

from pathlib import Path
from movx import start_waved
from movx import UvicornServer
import webview
import click
import uvicorn
from movx.core import dcps, db, locations, tasks


def start_serve(log_level="warning", reload=False):
    uvicorn.run("movx.ui.main:main", log_level=log_level, reload=reload)


@click.group()
def main():
    pass


@main.command()
def serve():
    start_waved()
    print("Starting application")
    start_serve()


@main.command()
def dev():
    start_waved()
    print("Starting application in dev mode")
    webbrowser.open("http://127.0.0.1:10101/")
    start_serve(reload=True)


@main.command()
def app():
    start_waved()
    print("Starting application in app mode")

    config = uvicorn.Config(
        "movx.ui.main:main", port=8000, log_level="warning", reload=True
    )
    instance = UvicornServer(config=config)
    instance.start()

    webview.create_window("MOVX", "http://127.0.0.1:10101/")
    webview.start(debug=True)


@main.command()
def scan():
    locations.scan_all()
    # movx.scan()
    # movx.pretty_print()


@main.command()
@click.argument("path")
@click.option("--name")
def add(path, name="noname"):
    path = Path(path)
    locations.add(str(path.absolute()), name=name)


@main.command()
@click.argument("path")
def check(path):
    if path == "all":
        dcps.check_all(print_tasks_cli)
    else:
        dcps.check()

    # movx.update_locations("NEW", path)
    # movx.scan()
    # movx.check()
    # movx.pretty_print()


@main.command()
@click.argument("path")
def parse(path):
    if path == "all":
        dcps.parse_all()
    else:
        dcps.parse()


@main.command()
def clear():
    db.clear()


@main.command()
def cancel():
    tasks.cancel()


def print_tasks_cli(tasks):
    for t in tasks:
        print("\x1b[1A\x1b[2K", end="")

    p = ""

    for t in tasks:
        p += pbar(t.name, t.progress * 100, 100, "(eta: %0.fs)" % t.eta)
    print(p, end="")


def pbar(name, count_value, total, suffix=""):
    bar_length = 50
    filled_up_Length = int(round(bar_length * count_value / float(total)))
    percentage = round(100.0 * count_value / float(total), 1)
    bar = "=" * filled_up_Length + "-" * (bar_length - filled_up_Length)
    return "%s [%s] %s%s %s\r\n" % (name, bar, percentage, "%", suffix)

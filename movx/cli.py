import time
import webbrowser
import os
from pathlib import Path
import click

from movx import start_agent, start_serve
from movx.app import start_app


@click.group()
def main():
    pass


@main.command()
def serve(dev):
    start_serve()


@main.command()
def app():
    start_app()

@main.command()
@click.argument("path")
@click.option("--host", help="Host Address (Default to 0.0.0.0)", default="0.0.0.0")
@click.option("--port", help="Host Port (Default to 11011)", type=int, default=11011)
@click.option("--debug", help="Uvicorn debug flag", is_flag=True)
def agent(path, host, port, debug):
    os.environ["MOVX_AGENT_ROOT_PATH"] = path
    start_agent(host, port, debug)
    time.sleep(2)
    input("Press Enter to quit")

@main.command()
@click.option("--deldb", help="delete the DB prior to launch the app", is_flag=True)
def dev(deldb):
    if deldb:
        db_path = Path.home() / ".movx" / "movx.db"
        db_path.unlink()
    #os.environ["H2O_WAVE_EDITABLE"] = "1"
    #os.environ["H2O_WAVE_DEBUG"] = "1"
    os.environ["MOVX_AGENT_ROOT_PATH"] = "."

    start_agent("127.0.0.1", 11011, True)
    start_serve(reload=True, browse=True)


@main.command()
@click.argument("file")
def scan(file):
    
    from movx.core import locations
    locations.scan_all()
    # movx.scan()
    # movx.pretty_print()


@main.command()
@click.argument("path")
@click.option("--name")
def add(path, name="noname"):
    from movx.core import locations
    path = Path(path)
    locations.add(str(path.absolute()), name=name)


@main.command()
@click.argument("path")
def check(path):
    
    from movx.core import dcps
    if path == "all":
        dcps.check_all(print_tasks_cli)
    else:
        dcps.check()


@main.command()
@click.argument("path", default="all")
def parse(path):
    
    from movx.core import dcps
    if path == "all":
        dcps.parse_all()
    else:
        dcps.parse()


@main.command()
def clear():
    pass #db.clear()


@main.command()
def cancel():
    pass #jobs.cancel()


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

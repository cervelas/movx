import webbrowser

from pathlib import Path
from movx import start_serve, start_app
import click
from movx.core import dcps, db, jobs, locations


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
@click.option("--deldb", help="delete the DB prior to launch the app", is_flag=True)
def dev(deldb):
    if deldb:
        db.del_db_file()
    start_serve(reload=True, browse=True)


@main.command()
@click.argument("file")
def scan(file):
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


@main.command()
@click.argument("path", default="all")
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
    jobs.cancel()


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

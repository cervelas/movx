import sys
import traceback
import math
import string
from collections.abc import MutableMapping, MutableSequence
from typing import Optional, Callable
from inspect import signature

from starlette.routing import compile_path
from h2o_wave import main, ui, Q, expando_to_dict
from movx.core import flatten

from movx.gui import styleguide
from movx.gui.cards import debug_card, crash_report

style = """
.ERROR {
  color: red;
}

.WARNING {
  color: orange;
}

.wave-w3{
    font-size: 18px;
    line-height: 1em;
}

.wave-s24.wave-w3{
    line-heigth: 0px;
}
"""

__handlers = {}

layouts = {
    "default": [
        ui.layout(
            breakpoint="l",
            width="100%",
            height="100%",
            zones=[
                ui.zone(
                    "body",
                    direction=ui.ZoneDirection.ROW,
                    zones=[
                        ui.zone("sidebar", size="200px"),
                        ui.zone(
                            "main",
                            size="calc(100% - 200px)",
                            zones=[
                                ui.zone("header"),
                                ui.zone(
                                    "infobar",
                                    direction=ui.ZoneDirection.ROW,
                                    justify="around",
                                    wrap="center",
                                ),
                                ui.zone("content"),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
    "2cols": [
        ui.layout(
            breakpoint="xl",
            width="100%",
            height="100%",
            zones=[
                ui.zone(
                    "body",
                    direction=ui.ZoneDirection.ROW,
                    zones=[
                        ui.zone("sidebar", size="200px"),
                        ui.zone(
                            "main",
                            size="calc(100% - 200px)",
                            zones=[
                                ui.zone("header"),
                                ui.zone(
                                    "2cols",
                                    direction=ui.ZoneDirection.ROW,
                                    wrap="center",
                                ),
                                ui.zone("content"),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
}

meta = ui.meta_card(
    box="",
    title="",
    theme="default",
    layouts=layouts["default"],
    notification_bar=ui.notification_bar(
        text="",
        type="success",
        position="top-right",
        # buttons=[ui.button(name='btn', label='Link button', link=True)]
    ),
    stylesheet=ui.inline_stylesheet(style),
    notification="",
)

nav = ui.nav_card(
    box="sidebar",
    value="/",
    items=[
        ui.nav_group(
            "",
            items=[
                ui.nav_item(name="#overview", label="📽 Overview"),
                ui.nav_item(name="#dcps", label="⛁ DCPs"),
                ui.nav_item(name="#movs", label="🎞 Movies"),
                ui.nav_item(name="#jobs", label="𝌠 Jobs"),
                ui.nav_item(name="#settings", label="⚙ Settings"),
            ],
        ),
    ],
)


def setup_page(q: Q, title=None, layout="default"):
    q.page.drop()

    # meta stuff
    meta.title = "%s | MovX" % title
    meta.layouts = layouts.get(layout, layouts["default"])

    # Add layouts, header and footer
    q.page["meta"] = meta

    # nav stuff
    nav.value = q.client.__loc_hash

    q.page["nav"] = nav


def breadcrumbs(q: Q, crumbs=[]):
    # crumbs = [ ("#", "Digital Cinema Packages") ] + crumbs

    if len(crumbs) > 0:
        q.page["breadcrumbs"] = ui.breadcrumbs_card(
            box="content", items=[ui.breadcrumb(name=b[0], label=b[1]) for b in crumbs]
        )


def make_md_row(values):
    bn = "\n"
    return f"| {' | '.join([str(x).replace(bn, '<br>') for x in values])} |"


def inline(items, **args):
    return ui.inline(items=items, **args)


def make_md_table(cols, rows):
    return "\n".join(
        [
            make_md_row(cols),
            make_md_row("-" * len(cols)),
            "\n".join([make_md_row(row) for row in rows]),
        ]
    )


def convert_size(size_bytes, exact=True):
    if size_bytes == 0:
        return "0 Bytes"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    if exact:
        return f"{s} {size_name[i]} ({size_bytes:n} bytes)"
    else:
        return f"{s} {size_name[i]}"


def flat(dic: MutableMapping, sep: str = "."):
    return {sep.join(k): v for k, v in flatten(dic).items()}


def md_table(dic: dict):
    if not dic:
        return "No Data"
    rows = []
    exclude = (MutableSequence, MutableMapping)
    for k, v in dic.items():
        if not isinstance(v, exclude):
            rows.append([k, v])
    return make_md_table(["Name", "Value"], rows)


def full_table(dic: dict, searchable=True, height="500px"):
    rows = []
    exclude = (MutableSequence, MutableMapping)
    for k, v in dic.items():
        if not isinstance(v, exclude):
            rows.append(ui.table_row(name=f"row.{k}", cells=[str(k), str(v)]))
    return ui.table(
        name="table",
        height=height,
        downloadable=True,
        resettable=True,
        columns=[
            ui.table_column(
                name="name",
                label="Name",
                searchable=searchable,
                min_width="600px",
                cell_overflow="wrap",
                align="right",
            ),
            ui.table_column(
                name="value",
                label="Value",
                searchable=searchable,
                min_width="600px",
                cell_overflow="wrap",
            ),
        ],
        rows=rows,
    )


def get_windows_drives():
    from ctypes import windll

    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in range(65, 65 + 26):
        if bitmask & 1:
            drives.append(chr(letter) + ":\\")
        bitmask >>= 1

    return drives


def get_linux_drives():
    # execute this : mount -l -t ext4,ext2
    """
    def check_net_disk(d):
        lines = subprocess.check_output(['net', 'use', d]).split(b'\r\n')
        if "not found" not in lines[0]:
            ret = {}
            for l in lines:
                kv = l.split(b'\t')
                ret.update( { kv[0]: kv[1] } )
            return ret

    for d in get_drives():
        # check network usage
        is_net = check_net_disk(d[0])
        if is_net is not None and is_net["Status"] != "Disconnected":
            print("check %s" % d)
            try:
                print(os.stat(d))
                dirs = [f.path for f in os.scandir(d) if f.is_dir()]
                print(dirs)
            except Exception as e:
                print(e)
    """
    pass


# do not mess with namespaces
from h2o_wave import routing as h2o_r


async def autoroute(q: Q, debug=False) -> bool:
    """
    Auot multi-handling of routes
    """
    awaited = False

    args = expando_to_dict(q.args).copy()

    # hash handler
    if args.get("#"):
        arg_value = args["#"]
        for rx, conv, func, arity in h2o_r._path_handlers:
            match = rx.match(arg_value)
            if match:
                if debug:
                    print("hash match")
                    print("arg value: %s" % arg_value)
                params = match.groupdict()
                for key, value in params.items():
                    params[key] = conv[key].convert(value)
                if len(params):
                    if arity <= 1:
                        await h2o_r._invoke_handler(func, arity, q, None)
                    else:
                        await func(q, **params)
                else:
                    await h2o_r._invoke_handler(func, arity, q, None)
                awaited = True

    # argument handler
    for arg, arg_value in args.items():
        if arg != "#":
            if not arg_value:
                continue
            for entry in h2o_r._arg_handlers.get(arg, []):
                predicate, func, arity = entry
                if debug:
                    print("handler match")
                    print("arg: %s" % arg)
                    print("predicate: %s" % predicate)
                    print("arg value: %s" % arg_value)

                if await h2o_r._match_predicate(predicate, func, arity, q, arg_value):
                    awaited = True
            for predicate, func, arity, rx, conv in h2o_r._arg_with_params_handlers:
                match = rx.match(arg_value)
                if match:
                    if debug:
                        print("with_params match")
                        print("arg: %s" % arg)
                        print("predicate: %s" % predicate)
                        print("arg value: %s" % arg_value)
                    params = match.groupdict()
                    for key, value in params.items():
                        params[key] = conv[key].convert(value)
                    if await h2o_r._match_predicate(
                        predicate, func, arity, q, arg_value, **params
                    ):
                        q.args[arg] = False
                        awaited = True

    # Event handlers.
    for event_source in expando_to_dict(q.events):
        for entry in h2o_r._event_handlers.get(event_source, []):
            event_type, predicate, func, arity = entry
            event = q.events[event_source]
            if event_type in event:
                arg_value = event[event_type]
                if await h2o_r._match_predicate(predicate, func, arity, q, arg_value):
                    awaited = True

    return awaited

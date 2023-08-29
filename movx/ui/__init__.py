import sys
import traceback
import math
from collections.abc import MutableMapping, MutableSequence

from h2o_wave import ui, Q, expando_to_dict

layouts = {
    "default": [
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
                        ui.zone("content", size="calc(100% - 200px)"),
                    ],
                ),
            ],
        ),
    ],
}


def setup_page(q: Q, title=None, layout="default"):
    q.page.drop()

    q.page["meta"] = ui.meta_card(
        box="",
        title=title,
        theme="default",
        layouts=layouts[layout],
        notification_bar=ui.notification_bar(
            text="",
            type="success",
            position="top-right",
            # buttons=[ui.button(name='btn', label='Link button', link=True)]
        ),
    )

    hash = q.args["#"]

    if hash:
        hash = "#" + hash

    q.page["nav"] = ui.nav_card(
        box="sidebar",
        value=hash or "/",
        items=[
            ui.nav_group(
                "",
                items=[
                    ui.nav_item(name="/", label="Home"),
                    ui.nav_item(name="#overview", label="Overview"),
                    ui.nav_item(name="#alldcps", label="DCP"),
                    ui.nav_item(name="#alltasks", label="Tasks"),
                    ui.nav_item(name="#settings", label="Settings"),
                ],
            ),
        ],
    )


def breadcrumbs(q: Q, crumbs=[]):
    # crumbs = [ ("#", "Digital Cinema Packages") ] + crumbs

    if len(crumbs) > 0:
        q.page["breadcrumbs"] = ui.breadcrumbs_card(
            box="content", items=[ui.breadcrumb(name=b[0], label=b[1]) for b in crumbs]
        )


def make_markdown_row(values):
    return f"| {' | '.join([str(x) for x in values])} |"


def make_markdown_table(fields, rows):
    return "\n".join(
        [
            make_markdown_row(fields),
            make_markdown_row("-" * len(fields)),
            "\n".join([make_markdown_row(row) for row in rows]),
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


def crash_report(q: Q) -> ui.FormCard:
    """
    Card for capturing the stack trace and current application state, for error reporting.
    This function is called by the main serve() loop on uncaught exceptions.
    """

    def code_block(content):
        return "\n".join(["```", *content, "```"])

    type_, value_, traceback_ = sys.exc_info()
    stack_trace = traceback.format_exception(type_, value_, traceback_)

    dump = [
        "### Stack Trace",
        code_block(stack_trace),
    ]

    states = [
        ("q.app", q.app),
        ("q.user", q.user),
        ("q.client", q.client),
        ("q.events", q.events),
        ("q.args", q.args),
    ]
    for name, source in states:
        dump.append(f"### {name}")
        dump.append(
            code_block([f"{k}: {v}" for k, v in expando_to_dict(source).items()])
        )

    return ui.form_card(
        box="content",
        items=[
            ui.stats(
                items=[
                    ui.stat(
                        label="",
                        value="Oops!",
                        caption="Something went wrong",
                        icon="Error",
                    )
                ],
            ),
            ui.separator(),
            ui.text_l(content="Apologies for the inconvenience!"),
            ui.buttons(items=[ui.button(name="reload", label="Reload", primary=True)]),
            ui.expander(
                name="report",
                label="Error Details",
                items=[
                    ui.text(
                        'To report this issue, <a href="" target="_blank">please open an issue</a> with the details below:'
                    ),
                    ui.text(content="\n".join(dump)),
                ],
            ),
        ],
    )


def _flatten_dict_gen(d, parent_key, sep):
    for k, v in d.items():
        new_key = parent_key + sep + k.lower() if parent_key else k.lower()
        if isinstance(v, MutableMapping):
            yield from flatten_dict(v, new_key, sep=sep).items()
        elif isinstance(v, MutableSequence):
            v = {f"{new_key}.{i}": d for (i, d) in enumerate(v)}
            yield from flatten_dict(v, new_key, sep=sep).items()
        else:
            yield new_key, v


def flatten_dict(d: MutableMapping, parent_key: str = "", sep: str = "."):
    return dict(_flatten_dict_gen(d, parent_key, sep))


def dict_to_table(dic):
    rows = []
    for k, v in dic.items():
        if not isinstance(v, (MutableSequence, MutableMapping)):
            rows.append([k, v])
    return make_markdown_table(["Name", "Value"], rows)


def dict_to_searchable_table(dic):
    dic = flatten_dict(dic)
    return ui.table(
        name="table",
        height="600px",
        downloadable=True,
        resettable=True,
        columns=[
            ui.table_column(
                name="name",
                label="Name",
                searchable=True,
                min_width="600px",
                cell_overflow="wrap",
                align="right",
            ),
            ui.table_column(
                name="value",
                label="Value",
                searchable=True,
                min_width="600px",
                cell_overflow="wrap",
            ),
        ],
        rows=[
            ui.table_row(name=f"row.{k}", cells=[str(k), str(v)])
            for k, v in dic.items()
        ],
    )

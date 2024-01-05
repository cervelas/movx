import sys
import traceback

from h2o_wave import ui, expando_to_dict


async def debug_card(q):
    """
    Card for capturing the stack trace and current application state, for error reporting.
    This function is called by the main serve() loop on uncaught exceptions.
    """

    def code_block(content):
        return "\n".join(["```", *content, "```"])

    dump = []

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

    q.page.add(
        "debug",
        ui.form_card(
            box="content",
            items=[
                ui.expander(
                    name="Debug",
                    label="Application states",
                    items=[
                        ui.text(content="\n".join(dump)),
                    ],
                ),
            ],
        ),
    )

    await q.page.save()


def crash_report(q):
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

import pprint
import time
from datetime import timedelta
from h2o_wave import ui


def generate_tasks_rows(tasks):
    rows = []
    for task in tasks:
        rows.append(
            ui.table_row(
                name="#task/%s" % task.id,
                cells=[
                    task.name,
                    task.type,
                    task.status,
                    time.ctime(task.timestamp + task.elapsed_time_s),
                    str(timedelta(seconds=round(task.elapsed_time_s))),
                    str(task.progress),
                ],
            )
        )
    return rows


def tasks_list(tasks):
    columns = [
        ui.table_column(
            name="name",
            label="Name",
            searchable=True,
            min_width="600px",
            cell_overflow="wrap",
        ),
        ui.table_column(name="type", label="Type", searchable=True, min_width="40px"),
        ui.table_column(
            name="status", label="status", filterable=True, max_width="150px"
        ),
        ui.table_column(
            name="started", label="started", max_width="200px", data_type="time"
        ),
        ui.table_column(name="time_elapsed", label="duration", max_width="70px"),
        ui.table_column(
            name="progress",
            label="progress",
            cell_type=ui.progress_table_cell_type(),
            max_width="70px",
        ),
    ]

    return ui.table(
        name="tasks_list",
        columns=columns,
        rows=generate_tasks_rows(tasks),
        groupable=True,
        downloadable=True,
        resettable=True,
    )


def check_task_details(task):
    columns = [
        ui.table_column(name="name", label="Name", searchable=True, min_width="100px"),
        ui.table_column(name="bypass", label="bypass", min_width="40px"),
        ui.table_column(
            name="errors",
            label="progress",
            filterable=True,
            cell_type=ui.progress_table_cell_type(),
            max_width="200px",
        ),
        ui.table_column(name="time_elapsed", label="duration", max_width="40px"),
        ui.table_column(
            name="result",
            label="result",
            searchable=True,
            filterable=True,
            max_width="500px",
        ),
    ]

    return ui.form_card(
        box=ui.box("header", size=0),
        items=[
            ui.inline(
                justify="between",
                items=[
                    ui.text_xl(
                        "Last Check %s @ %s"
                        % (
                            "PASS" if task.report["valid"] else "FAIL",
                            task.report["date"],
                        )
                    )
                ],
            ),
            ui.expander(
                name="expander",
                label="Check Summary",
                items=[
                    ui.markup(
                        name="markup", content="<pre>%s</pre>" % task.report["message"]
                    ),
                ],
            ),
            ui.expander(
                name="expander",
                label="Checks List",
                items=[
                    ui.table(
                        name="check_result_list",
                        columns=columns,
                        rows=[
                            ui.table_row(
                                name=check["name"],
                                cells=[
                                    check["pretty_name"],
                                    str(check["bypass"]),
                                    str(len(check["errors"])),
                                    str(check["seconds_elapsed"]),
                                    "\r\n".join(
                                        [
                                            err["criticality"] + ": " + err["message"]
                                            for err in check["errors"]
                                        ]
                                    ),
                                    check["doc"],
                                ],
                            )
                            for check in task.report["checks"]
                        ],
                        downloadable=True,
                        height="600px",
                    )
                ],
            ),
        ],
    )


def task_details(task):
    return [
        ui.inline(
            justify="between",
            items=[
                ui.text_s("Started @ %s" % time.ctime(task.timestamp)),
                ui.text_s(
                    "Finished @ %s" % time.ctime(task.timestamp + task.elapsed_time_s)
                ),
                ui.text_s(
                    "Duration %s" % timedelta(seconds=round(task.elapsed_time_s))
                ),
            ],
        ),
        ui.progress(
            label="Status %s" % task.status,
            caption="%s%%" % (task.progress * 100),
            value=task.progress,
        ),
        ui.markup(name="markup", content="<pre>%s</pre>" % pprint.pformat(task.result)),
    ]

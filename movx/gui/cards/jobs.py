import pprint
import time
from datetime import timedelta
from h2o_wave import ui


def jobs_list_table(jobs):
    columns = [
        ui.table_column(
            name="name",
            label="Name",
            searchable=True,
            min_width="600px",
            cell_overflow="wrap",
            cell_type=ui.markdown_table_cell_type(target=""),
        ),
        ui.table_column(name="type", label="Type", searchable=True, min_width="40px"),
        ui.table_column(
            name="status", label="status", filterable=True, max_width="150px"
        ),
        ui.table_column(
            name="started", label="started", max_width="200px", data_type="time"
        ),
        ui.table_column(
            name="progress",
            label="progress",
            #cell_type=ui.progress_table_cell_type(),
            max_width="70px",
        ),
    ]

    return ui.table(
        name="jobs_list",
        columns=columns,
        rows=gen_jobs_rows(jobs),
        groupable=True,
        downloadable=True,
        resettable=True,
    )


def gen_jobs_rows(jobs):
    rows = []
    for job in jobs:
        rows.append(
            ui.table_row(
                name=str(job.id),
                cells=[
                    "[%s](#job/%s)" % (job.dcp.title, job.id),
                    job.type.name,
                    job.status.name,
                    time.ctime(job.started_at),
                    str(job.progress * 100) + "%" if job.progress < 1 else "completed",
                ],
            )
        )
    return rows


def check_job_details(task):
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
        box=ui.box("content", size=0),
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

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
        downloadable=True,
        resettable=True,
    )


def gen_jobs_rows(jobs):
    rows = []

    for job in jobs:
        title = "*DCP DELETED*"
        if job.dcp is not None:
            title = job.dcp.title
        started_at = time.ctime(job.started_at) if job.started_at > 0 else "error"
        rows.append(
            ui.table_row(
                name=str(job.id),
                cells=[
                    "[%s](#job/%s)" % (title, job.id),
                    job.type.name,
                    job.status.name,
                    started_at,
                    str(int(job.progress * 100)) + "%" if job.progress < 1 else "completed",
                ],
            )
        )
    return rows
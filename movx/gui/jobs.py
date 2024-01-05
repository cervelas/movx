from h2o_wave import Q, ui, on
from movx.gui import setup_page
from movx.core.db import Job
from movx.core import jobs
from movx.gui.cards.jobs import jobs_list_table, gen_jobs_rows


@on("jobs_list")
async def on_row_clicked(q: Q):
    q.page["meta"] = ui.meta_card(box="", redirect="#job/%s" % q.args.jobs_list[0])
    await q.page.save()


@on()
async def delete_all_jobs(q: Q):
    jobs.delete_all()
    await q.page.save()


async def poll_jobs(q: Q):
    await q.page.save()

    while True:
        await q.sleep(1)

        _tasks = jobs.get_all()

        q.page["jobs_list"].table.rows = gen_jobs_rows(_tasks)

        await q.page.save()


@on("#jobs")
async def tasks_layout(q: Q):
    setup_page(q, "Jobs List")

    ts = Job.get_all()[::-1]

    if len(ts) > 0:
        q.page["jobs_list"] = ui.form_card(
            box="content",
            items=[
                ui.inline(
                    items=[
                        ui.text_xl("Jobs"),
                        ui.button(name="refresh_jobs", label="", icon="refresh"),
                        ui.button(
                            name="delete_all_jobs", label="Clear All", icon="danger"
                        ),
                    ]
                ),
                jobs_list_table(ts),
            ],
        )
    else:
        q.page["not-found"] = ui.form_card(
            box="content", items=[ui.text("No tasks found !")]
        )

    await q.page.save()

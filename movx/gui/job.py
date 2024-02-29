from h2o_wave import Q, ui, on
from movx.core.agent import JobStatus
from movx.gui import setup_page
from movx.gui.cards.job import job_progress, job_cards, add_raw_result_card
from movx.core.db import Job


async def poll_job(q: Q, job: Job):
    await q.page.save()

    if job is None:
        return
    
    last_job_status = None

    while True:
        await q.sleep(1)

        _job = job.get(job.id)

        if _job:
            q.page["job_detail_%s" % job.id].items = job_header_items(_job)
            q.page["job_progress_%s" % job.id].items = job_progress(_job)
            await q.page.save()
            if _job.status in [ JobStatus.finished or JobStatus.errored ]:
                if last_job_status == JobStatus.started:
                    q.page["meta"].redirect = "#job/%s" % job.id
                break
            else:
                last_job_status = _job.status
        else:
            break

def job_header_items(job):

    header = [
            ui.text_xl(
                "%s %s [%s](#dcp/%s) @ [%s](#loc/%s)"
                % (
                    job.type.name,
                    job.status.name,
                    job.dcp.title,
                    job.dcp.id,
                    job.dcp.location.name,
                    job.dcp.location.id,
                )
            ),
        ]

    if job.dcp.movie is not None:
        header += [
            ui.inline(
                [
                    ui.button(
                        name="goto_movie",
                        label="%s >" % job.dcp.movie.title,
                        value=str(job.dcp.movie.id),
                    ),
                ]
            )
        ]

    return [ ui.inline(
                justify="between",
                items= header)
    ]

@on("#job/{id:int}")
async def task_detail_layout(q: Q, id: int):
    job = Job.get(id)

    if job:
        header = [ui.text_xl("DCP DELETED - DCP NO MORE")]

        if job.dcp is not None:
            setup_page(q, "Job Detail %s" % job.dcp.title)
        else:
            setup_page(q, "Job Detail deleted DCP")

        q.page["job_detail_%s" % job.id] = ui.form_card(
            box=ui.box("content", size=0),
            items= job_header_items(job),
        )

        q.page["job_progress_%s" % job.id] = ui.form_card(
            box=ui.box("content", size=0), items=job_progress(job)
        )

        job_cards(q, job)
        add_raw_result_card(q, job.result)

        await poll_job(q, job)
    else:
        setup_page(q, "Error")
        q.page["not-found"] = ui.form_card(
            box="content", items=[ui.text("Task %s not found" % id)]
        )

    await q.page.save()


@on()
def update_hcjob_notes():
    pass


@on()
def update_hcjob_picture():
    pass


@on()
def update_hcjob_sound():
    pass

from h2o_wave import Q, ui, on
from movx.gui import setup_page
from movx.gui.cards.job import job_progress, job_cards, add_raw_result_card
from movx.core.db import Job, JobStatus


async def poll_job(q: Q, job: Job):
    await q.page.save()

    if job is None:
        return

    while True:
        await q.sleep(1)

        _job = Job.get(job.id)

        if _job:
            q.page["job_progress_%s" % job.id].items = job_progress(_job)
            if _job.status != JobStatus.started:
                break
        else:
            break

        await q.page.save()

@on("#job/{id:int}")
async def task_detail_layout(q: Q, id: int):

    job = Job.get(id)

    if job:
        setup_page(q, "Job Detail %s" % job.dcp.title)
        q.page["job_detail_%s" % job.id] = ui.form_card(
            box=ui.box("content", size=0),
            items=[
                ui.inline(
                    justify="start",
                    items=[
                        ui.button(
                            name="#jobs", label="Back", icon="ChevronLeftMed"
                        ),
                        ui.text_xl('Task %s <a href="#dcp/%s">%s</a> %s' % (job.type, job.dcp.id, job.dcp.title, job.status)),
                        #ui.button(
                        #    name="#dcp/%s" % job.dcp.id,
                        #    label="%s" % job.dcp.title,
                        #    icon="VideoSearch",
                        #),
                    ],
                ),
            ]
        )
        q.page["job_progress_%s" % job.id] = ui.form_card(
            box=ui.box("content", size=0),
            items = job_progress(job)
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


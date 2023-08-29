from h2o_wave import Q, ui, on
from movx.ui import setup_page
from movx.core.db import Task
from movx.core import tasks
from movx.ui.cards.tasks import tasks_list, generate_tasks_rows, task_details


@on("tasks_list")
async def on_row_clicked(q: Q):
    q.page["meta"] = ui.meta_card(box="", redirect=q.args.tasks_list[0])
    await q.page.save()


@on()
async def delete_all_tasks(q: Q):
    tasks.delete_all()
    await q.page.save()


async def poll_tasks(q: Q):
    await q.page.save()

    while True:
        await q.sleep(1)

        _tasks = tasks.get_all()

        q.page["tasks_list"].table.rows = generate_tasks_rows(_tasks)

        await q.page.save()


async def poll_task(q: Q, task: Task):
    await q.page.save()

    while True:
        await q.sleep(1)

        _task = Task.get(task.id)

        q.page["task_detail_%s" % task.id].items[2].progress.value = _task.progress
        q.page["task_detail_%s" % task.id].items[2].progress.caption = _task.status

        await q.page.save()


@on("#task/{id}")
async def task_detail_layout(q: Q, id):
    task = Task.get(id)

    if task:
        setup_page(q, "Task Detail %s" % task.name)
        q.page["task_detail_%s" % task.id] = ui.form_card(
            box=ui.box("content", size=0),
            items=[
                ui.inline(
                    justify="between",
                    items=[
                        ui.button(
                            name="#alltasks", label="Back", icon="ChevronLeftMed"
                        ),
                        ui.text_xl("Task %s : %s" % (task.name, task.status)),
                        ui.button(
                            name="#dcp/%s" % task.dcp.id,
                            label="%s" % task.dcp.title,
                            icon="VideoSearch",
                        ),
                    ],
                ),
            ]
            + task_details(task),
        )
    else:
        setup_page(q, "Error")
        q.page["not-found"] = ui.form_card(
            box="content", items=[ui.text("Task %s not found" % id)]
        )

    await poll_task(q, task)


@on("#alltasks")
async def tasks_layout(q: Q):
    setup_page(q, "Task List ")

    ts = Task.get_all()[::-1]

    if len(ts) > 0:
        q.page["tasks_list"] = ui.form_card(
            box="content",
            items=[
                ui.inline(
                    items=[
                        ui.text_xl("Tasks"),
                        ui.button(name="refresh_tasks", label="", icon="refresh"),
                        ui.button(
                            name="delete_all_tasks", label="Clear All", icon="danger"
                        ),
                    ]
                ),
                tasks_list(ts),
            ],
        )
    else:
        q.page["not-found"] = ui.form_card(
            box="content", items=[ui.text("No tasks found !")]
        )

    await q.page.save()

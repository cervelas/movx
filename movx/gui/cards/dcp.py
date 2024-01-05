from datetime import datetime

from h2o_wave import ui

from movx.core.db import Tags, JobType, JobStatus
from movx.gui import (
    convert_size,
    md_table,
    make_md_table,
    flat,
    full_table,
)


def add_infos_cards(q, dcp):
    add_dcp_header_card(q, dcp)
    add_dcp_parse_card(q, dcp)
    add_dcp_probe_card(q, dcp)
    add_dcp_check_card(q, dcp)
    # add_dcp_actions_card(q, dcp)


def check_card(report):
    columns = [
        ui.table_column(name="name", label="Name", searchable=True, min_width="400px"),
        ui.table_column(
            name="result",
            label="Result",
            cell_type=ui.markdown_table_cell_type(),
            min_width="300px",
            cell_overflow="wrap",
            searchable=True,
        ),
        ui.table_column(
            name="doc",
            label="Doc",
            cell_type=ui.markdown_table_cell_type(target="_blank"),
            min_width="800px",
            cell_overflow="wrap",
        ),
        ui.table_column(
            name="sec_elapsed",
            label="Time",
            max_width="40px",
            sortable=True,
            align="center",
        ),
        ui.table_column(
            name="bypass", label="bypass", filterable=True, max_width="70px"
        ),
        ui.table_column(
            name="test_name",
            label="Test Name",
        ),
    ]

    check_form = []

    """if dcp.package_type != "OV":
        #if len(movx.get_ov_dcps(dcp.title)) > 1:
        check_form.append(
            ui.dropdown(name='dropdown', label='OV', required=True, width="500px",
                        choices=[ ui.choice(name=str(dcp.id), label=dcp.path) for dcp in movx.get_ov_dcps(dcp.title)
            ])
        )
    else:
        dcp.ov_path = movx.get_ov_dcps(dcp.title)[0]"""

    # check_form.append(ui.button(name="dcp_check", label="Check DCP", value=str(dcp.uid)))

    return ui.form_card(
        box=ui.box("content", size=0),
        items=[
            ui.inline(
                justify="between",
                items=[
                    ui.text_xl(
                        "Last Check %s @ %s"
                        % (
                            "PASS" if report.get("valid") else "FAIL",
                            report.get("date"),
                        )
                    )
                ]
                + check_form,
            ),
            ui.expander(
                name="expander",
                label="Check Summary",
                items=[
                    ui.markup(
                        name="markup", content="<pre>%s</pre>" % report.get("message")
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
                                    # str(len(check["errors"])),
                                    "\r\n".join(
                                        [
                                            "<span class='%s'><b>%s</b></span> **%s**"
                                            % (
                                                err["criticality"],
                                                err["criticality"],
                                                err["message"],
                                            )
                                            for err in check["errors"]
                                        ]
                                    ),
                                    check["doc"],
                                    str(check["seconds_elapsed"]),
                                    str(check["bypass"]),
                                    check["name"],
                                ],
                            )
                            for check in report.get("checks", {})
                        ],
                        downloadable=True,
                        height="600px",
                    )
                ],
            ),
        ],
    )


def add_dcp_header_card(q, dcp):
    dcp_tags = []

    if dcp.tags:
        dcp_tags = [t.name for t in dcp.tags]

    available_tags = [t.name for t in Tags.get_all() if t.name not in dcp_tags]

    q.page.add(
        "dcp_header",
        ui.form_card(
            box=ui.box("infobar"),
            items=[
                ui.inline(
                    justify="between",
                    items=[
                        ui.button(name="back_to_list", label="< Overview", value=""),
                        ui.text_xl(dcp.title),
                        ui.picker(
                            name="dcp_tags_picker",
                            label="Tags",
                            values=dcp_tags,
                            choices=[
                                ui.choice(name=t, label=t) for t in available_tags
                            ],
                            trigger=True,
                        ),
                        ui.button(name="open_movie", label="Movie >", value=""),
                    ],
                ),
            ],
        ),
    )


def add_dcp_parse_card(q, dcp):
    jobs = dcp.jobs(type=JobType.parse)

    job_items = []
    if len(jobs) == 0:
        job_items = [ui.text_l("DCP Not Parsed")]
    else:
        job = jobs[0]
        if job.status == JobStatus.started:
            job_items = [ui.text_l("Running...")]
        else:
            st = datetime.fromtimestamp(job.finished_at)
            job_items = [
                ui.text(
                    "[Last Parse Job %s](#job/%s)"
                    % (st.strftime("%m/%d/%Y %H:%M:%S"), job.id)
                )
            ]

    q.page.add(
        "dcp_parse_card",
        ui.form_card(
            box=ui.box("content", size=3),
            items=[
                ui.inline(
                    items=[ui.text_l("Parse")]
                    + job_items
                    + [
                        ui.button(
                            name="dcp_parse_action", label="Parse", value=str(dcp.id)
                        ),
                    ]
                ),
            ],
        ),
    )


def add_dcp_probe_card(q, dcp):
    probe_jobs = dcp.jobs(type=JobType.probe)

    job = False
    items = []
    job_items = []

    if len(probe_jobs) == 0:
        job_items = [ui.text("DCP Not Parsed")]
    else:
        job = probe_jobs[0]
        if job.status == JobStatus.started:
            job_items = [ui.text("Running...")]
        else:
            st = datetime.fromtimestamp(job.finished_at)

            """
            job_items += [ ui.stats(
                        [
                            ui.stat(
                                label="Duration",
                                value="00:06:45:00",
                                icon="ScreenTime",
                                caption="13794 Frames",
                            ),
                            ui.stat(
                                label="Image",
                                value="1920x1080@24",
                                icon="ImageCrosshair",
                                caption="Ration 1.85",
                            ),
                            ui.stat(
                                label="Size",
                                value="50.3 GB",
                                icon="StorageOptical",
                                caption="12391B",
                            ),
                        ]
                    ) ]
            """

            job_items += [
                ui.text(
                    "[Last Probe Job %s](#job/%s)"
                    % (st.strftime("%m/%d/%Y %H:%M:%S"), job.id)
                ),
                ui.button(
                    name="probe_job_detail", label="Details", path="/#job/%s" % dcp.id
                ),
            ]

    items = [
        ui.inline(
            items=[ui.text_l("Probe")]
            + job_items
            + [ui.button(name="dcp_probe_action", label="Probe", value=str(dcp.id))]
        )
    ] + items

    q.page.add(
        "dcp_probe_card",
        ui.form_card(
            box=ui.box("content"),
            items=items,
        ),
    )


def add_dcp_check_card(q, dcp):
    q.page.add(
        "dcp_check_card",
        ui.form_card(
            box=ui.box("content"),
            items=[
                ui.inline(
                    items=[
                        ui.button(
                            name="dcp_check_action", label="Check", value=str(dcp.id)
                        ),
                    ]
                ),
                # ui.text_s(dcp.path),
                # ui.text(make_markdown_table(infos.keys(), [ infos.values() ]))
            ],
        ),
    )


def dcp_infos_card(q, dcp):
    q.page.add(
        "probe_card",
        ui.form_card(
            box=ui.box("infobar"),
            items=[
                ui.inline(
                    items=[
                        ui.text_xl("Probe result"),
                        ui.text_s("2 days ago"),
                        ui.button(name="probe", label="Refresh"),
                    ]
                ),
                ui.stats(
                    [
                        ui.stat(
                            label="Duration",
                            value="00:06:45:00",
                            icon="ScreenTime",
                            caption="13794 Frames",
                        ),
                        ui.stat(
                            label="Image",
                            value="1920x1080@24",
                            icon="ImageCrosshair",
                            caption="Ration 1.85",
                        ),
                        ui.stat(
                            label="Size",
                            value="50.3 GB",
                            icon="StorageOptical",
                            caption="12391B",
                        ),
                    ]
                ),
            ],
        ),
    )
    q.page.add(
        "test2",
        ui.form_card(
            box=ui.box("infobar"),
            items=[
                ui.inline(
                    justify="around",
                    items=[
                        ui.stats(
                            justify="around",
                            items=[
                                ui.stat(
                                    label="Status",
                                    value="ToCheck",
                                    icon="AccountActivity",
                                    caption="2 days ago",
                                ),
                            ],
                        ),
                        ui.dropdown(
                            name="status_dropdown",
                            label="Update Status To",
                            value="N/A",
                            width="120px",
                            choices=[
                                ui.choice(status.name, status.name)
                                for status in Tags.get()
                            ],
                        ),
                    ],
                )
            ],
        ),
    )

    q.page.add(
        "test34",
        ui.form_card(
            box=ui.box("infobar"),
            items=[
                ui.stats(
                    justify="around",
                    items=[
                        ui.stat(
                            label="Status",
                            value="ToCheck",
                            icon="AccountActivity",
                            caption="2 days ago",
                        ),
                        ui.stat(
                            label="Check",
                            value="OK",
                            icon="WaitlistConfirmMirrored",
                            caption=" 2 days ago",
                        ),
                        ui.stat(
                            label="Probe",
                            value="OK",
                            icon="RedEye12",
                            caption=" 2 days ago",
                        ),
                    ],
                ),
                ui.inline(
                    justify="around",
                    height="10px",
                    items=[
                        ui.button(name="kj", label="Update"),
                        ui.button(name="kj3", label="CHeck"),
                        ui.button(name="jhjh", label="Probe"),
                    ],
                ),
            ],
        ),
    )

    """q.page.add('test3', ui.form_card(
        box=ui.box("infobar"),
        items=[
                ui.message_bar(type='blocked', text='This action is blocked.'),
                ui.message_bar(type='error', text='This is an error message'),
                ui.message_bar(type='warning', text='This is a warning message.'),
                ui.message_bar(type='info', text='This is an information message.'),
                ui.message_bar(type='success', text='This is an success message.'),
                ui.message_bar(type='danger', text='This is a danger message.'),
                ui.message_bar(type='success', text='This is a **MARKDOWN** _message_.'),
                ui.message_bar(type='success', text='This is an <b>HTML</b> <i>message</i>.'),
            ]))"""
    q.page.add(
        "tessqwet",
        ui.small_stat_card(
            box=ui.box("infobar"),
            title="Check",
            value="OK",
        ),
    )

    q.page.add(
        "dcp_header",
        ui.form_card(
            box=ui.box("infobar", size=0),
            items=[
                ui.inline(
                    items=[
                        ui.button(name="back_to_list", label="< Overview", value=""),
                        ui.text_xl(dcp.title),
                        ui.button(name="open_movie", label="Movie >", value=""),
                    ]
                ),
                ui.inline(
                    items=[
                        ui.button(
                            name="dcp_parse_action", label="Parse", value=str(dcp.id)
                        ),
                        ui.button(
                            name="dcp_check_action", label="Check", value=str(dcp.id)
                        ),
                    ]
                ),
                # ui.text_s(dcp.path),
                # ui.text(make_markdown_table(infos.keys(), [ infos.values() ]))
            ],
        ),
    )

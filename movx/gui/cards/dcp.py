from datetime import datetime

from h2o_wave import Q, ui

from movx.core.db import Tags, JobType, JobStatus
from movx.core.dcps import by_files_parse_report, get_available_check_profiles
from movx.gui import (
    convert_size,
    md_table,
    make_md_table,
    flat,
    full_table,
)
from movx.gui.cards.job import check_report_items


def add_infos_cards(q, dcp):
    add_dcp_header_card(q, dcp)
    #dcp_infos_card(q, dcp)
    add_dcp_tags_card(q, dcp)
    add_dcp_notes_card(q, dcp)
    add_dcp_parse_card(q, dcp)
    add_dcp_probe_card(q, dcp)
    add_dcp_check_card(q, dcp)
    # add_dcp_actions_card(q, dcp)

def add_dcp_header_card(q, dcp):

    movie_btn = []
    if dcp.movie is not None:
        movie_btn = [ ui.inline([
                            ui.button(name="goto_movie", label=f"{dcp.movie.title} >", value=str(dcp.movie.id)),
                        ])
                    ]

    q.page.add(
        "dcp_header",
        ui.form_card(
            box=ui.box("header"),
            items=[
                ui.inline(
                    justify="between",
                    items=[
                        ui.text_xl(f"{dcp.title} @ [{dcp.location.name}](#loc/{dcp.location.id})"),
                    ] + movie_btn,
                ),
            ],
        ),
    )

def add_dcp_tags_card(q, dcp):
    dcp_tags = []

    if dcp.tags:
        dcp_tags = [t.name for t in dcp.tags]

    available_tags = [t.name for t in Tags.get_all() if t.name not in dcp_tags]

    q.page.add(
        "dcp_tags",
        ui.form_card(
            box=ui.box("infobar"),
            items=[
                ui.inline(
                    justify="between",
                    items=[
                        ui.picker(
                            name="dcp_tags_picker",
                            label="Tags",
                            values=dcp_tags,
                            choices=[
                                ui.choice(name=t, label=t) for t in available_tags
                            ],
                            trigger=True,
                        ),
                    ],
                ),
            ],
        ),
    )

def add_dcp_notes_card(q, dcp):
    q.page.add(
        "dcp_notes_form",
        ui.form_card(
            box=ui.box("infobar"),
            items=[
                ui.inline(
                    justify="between",
                    items=[
                        ui.textbox(
                            name="dcp_notes",
                            label="Notes",
                            multiline=True,
                            value=dcp.notes,
                            width="100%",
                            height="300px"
                        )
                    ],
                ),
            ],
        ),
    )

def job_status_items(job):
    job_items = []
    if job.finished_at > 0:
        st = datetime.fromtimestamp(job.finished_at)
        job_items = [
            ui.text_s(
                st.strftime("%m/%d/%Y %H:%M:%S")
            )
        ]
    else:
        job_items = [
            ui.text_s(
                "Job in Progress (%s%%)"
                % int(job.progress * 100)
            )
        ]
    return job_items

def add_dcp_parse_card(q, dcp):
    jobs = dcp.jobs(type=JobType.parse)

    job_items = []
    files_items = []
    if len(jobs) == 0:
        job_items = [ui.text_l("DCP Not Parsed")]
    else:
        job_items = [ ui.text_l(f"[Last Parse Job](#job/{jobs[0].id})") ] + job_status_items(jobs[0])
        files_items = dcp_files_items(jobs[0].result)


    q.page.add(
        "dcp_parse_card",
        ui.form_card(
            box=ui.box("content"),
            items=[
                ui.inline(justify="between",
                    items=job_items
                    + [
                        ui.button(
                            name="dcp_parse_action", label="Parse", value=str(dcp.id)
                        ),
                    ]
                ),
            ] + files_items,
        ),
    )

def dcp_files_items(report):
    items = []
    files = by_files_parse_report(report)
    i = 0
    for name, props in files.items():
        items.append( ui.expander(
                        name="file_%s%s_expander" % (name, i),
                        label="%s File %s" % ( props.get("__type"), name ),
                        items=[full_table(flat(props))],
                    ) )
        i += 1

    return items

def add_dcp_probe_card(q, dcp):
    jobs = dcp.jobs(type=JobType.probe)

    items = []

    job_items = []
    if len(jobs) == 0:
        job_items = [ui.text_l("DCP Not Probed")]
    else:
        job_items = [ ui.text_l(f"[Last Probe Job](#job/{jobs[0].id})") ] +job_status_items(jobs[0])

    items = [
        ui.inline(
            justify="between",
            items= job_items
            + [     ui.button(name="dcp_probe_action", label="Probe", value=str(dcp.id)),
                    #ui.inline([
                    #    ui.text('KDM'),
                    #    ui.file_upload(name='kdm_probe_upload', compact=True)
                    #], justify="end"),
                    #ui.inline([
                    #    ui.text('Private Key'),
                    #    ui.file_upload(name='pkey_probe_upload', compact=True),
                    #], justify="end"),
                ]
            )
    ] + items

    q.page.add(
        "dcp_probe_card",
        ui.form_card(
            box=ui.box("content"),
            items=items,
        ),
    )


def add_dcp_check_card(q: Q, dcp):

    jobs = dcp.jobs(type=JobType.check)

    profiles = get_available_check_profiles()
    
    job_items = []
    if len(jobs) == 0:
        job_items = [ui.text_l("DCP Not Checked")]
    else:
        job_items = [ ui.text_l(f"[Last Check Job](#job/{jobs[0].id})") ] + job_status_items(jobs[0])

    check_options = [ ui.dropdown(name="profile_check_choice", label="Choose a Check Profile", 
                        placeholder="Select the right Profile for this check",
                        choices=[ ui.Choice(name=str(f.resolve()), label=f.stem) for f in profiles ]) 
                        ]

    if dcp.package_type == "VF":
        ovs = [ ov for ov in dcp.movie.ovs() if ov.location.id == dcp.location.id ]
        check_options +=  [ ui.dropdown("ov_check_choice", choices=[ 
                                ui.choice(name=str(ov_dcp.id), label=ov_dcp.title) for ov_dcp in ovs ],
                                placeholder = "Choose a OV",
                                tooltip = "OV must be in the same location as VF",
                                label = "Original Version DCP",
                                width = "600px") ]
    
    last_check = []
    if len(jobs) > 0:
        last_check = check_report_items(jobs[0].result)

    q.page.add(
        "dcp_check_card",
        ui.form_card(
            box=ui.box("content", size=0),
            items=[
                ui.inline(justify="between",
                    items= job_items
                    + [
                        ui.button(
                            name="dcp_check_action", label="Check", value=str(dcp.id)
                        ),
                    ] + check_options
                ),
            ] + last_check,
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
        "test3s4",
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
        "dcp_header2",
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

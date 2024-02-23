import pprint
import time
import yaml
from datetime import datetime, timedelta

from h2o_wave import ui
from movx.core.db import JobType, JobStatus
from movx.gui import full_table, convert_size, md_table, flat, make_md_table


def job_cards(q, job):
    if job.status == JobStatus.finished:
        if job.type == JobType.check:
            add_check_cards(q, job.result)
            add_raw_result_card(q, job.result)
        elif job.type == JobType.parse:
            add_parse_cards(q, job.result)
        elif job.type == JobType.probe:
            add_probe_cards(q, job.result)


def job_progress(job):
    items = []
    if job.started_at > 0:
        st = datetime.fromtimestamp(job.started_at)

        items = [ui.text_s("Started @ %s" % st.strftime("%m/%d/%Y %H:%M:%S"))]

    if job.finished_at > 0:
        ft = datetime.fromtimestamp(job.finished_at)
        items += [ui.text_s("Finished @ %s" % ft.strftime("%m/%d/%Y %H:%M:%S"))]
    elif job.progress > 0:
        items += [ui.text_s("Time remaining %s" % timedelta(seconds=round(job.eta())))]

    items += [ui.text_s("Elapsed %s" % timedelta(seconds=job.duration()))]

    return [
        ui.inline(
            justify="between",
            items=items,
        ),
        ui.progress(
            label="Status %s" % job.status,
            caption="Progress %s%%" % round(job.progress * 100),
            value=job.progress,
        ),
    ]


def add_human_check_cards():
    #general_notes_cards()
    #conformity_check_card()
    #check_actions_cards()
    pass


def add_parse_cards(q, parse_report):
    add_am_cards(q, parse_report)
    add_pkl_cards(q, parse_report)
    add_cpl_cards(q, parse_report)


def add_probe_cards(q, parse_report):
    add_reels_probe_cards(q, parse_report)
    add_am_cards(q, parse_report)
    add_pkl_cards(q, parse_report)
    add_cpl_cards(q, parse_report)


def add_raw_result_card(q, result):
    q.page.add(
        "raw_parse_card",
        ui.form_card(
            box=ui.box("content", size=0),
            items=[
                ui.text_xl("Raw results"),
                ui.expander(
                    name="raw_result_tbl_exp",
                    label="Raw Result Table",
                    items=[full_table(flat(result))],
                ),
                ui.expander(
                    name="raw_result_txt_exp",
                    label="Raw Result Text",
                    items=[
                        ui.markup(
                            name="raw_result_mtxt",
                            content="<pre>%s</pre>" % yaml.dump(result, indent=2),
                        ),
                    ],
                ),
            ],
        ),
    )


def add_pkl_cards(q, parse_report):
    for pkl in parse_report.get("pkl_list", []):
        infos = pkl["Info"]["PackingList"]
        assets = []
        for a in infos["AssetList"]["Asset"]:
            a["HumanSize"] = convert_size(a["Size"])
            assets.append(
                ui.expander(
                    name="expander",
                    label=a.get("Path", "Unkown"),
                    items=[ui.text(md_table(a))],
                )
            )
            # assets.append(ui.text_l(a["OriginalFileName"]))
            # assets.append(ui.text_m(a.get("AnnotationText", "")))
            # assets.append(ui.separator(label=''))
        q.page.add(
            "pkl_infos_" + pkl["FileName"],
            ui.form_card(
                box=ui.box("content", size=0),
                items=[
                    ui.text_xl("Packing List"),
                    # ui.text_xl(pkl["FileName"]),
                    ui.text_s(pkl["FilePath"]),
                ]
                + assets
                + [
                    ui.expander(
                        name="pkl_sign_expander",
                        label="Security",
                        items=[
                            ui.text("Signer Inforamtions"),
                            ui.text(md_table(flat(infos.get("Signer")))),
                            ui.text("Signature Informations"),
                            ui.text(md_table(flat(infos.get("Signature")))),
                        ],
                    ),
                    ui.expander(
                        name="pkl_raw_expander",
                        label="Raw PKL Data",
                        items=[full_table(flat(infos))],
                    ),
                ],
            ),
        )


def video_asset_details(asset):
    items = [
        ui.stats(
            justify="between",
            inset=True,
            items=[
                ui.stat(
                    label="Asset",
                    value=asset.get("EssenceType"),
                    icon="ImageCrosshair",
                    caption="Aspect Ratio %s" % asset.get("ScreenAspectRatio"),
                ),
                ui.stat(
                    label="Entry Point",
                    value="%s" % asset.get("TimeCodeIn"),
                    # icon="ScreenTime",
                    caption="%s (CPL %s) Frames"
                    % (asset.get("EntryPoint"), asset.get("CPLEntryPoint")),
                ),
                ui.stat(
                    label="Out Point",
                    value="%s" % asset.get("TimeCodeOut"),
                    # icon="ImageCrosshair",
                    caption="%s (CPL %s) Frames"
                    % (asset.get("CPLOutPoint"), asset.get("CPLOutPoint")),
                ),
                ui.stat(
                    label="Duration",
                    value="%s" % asset.get("TimeCodeDuration"),
                    # icon="ImageCrosshair",
                    caption="%s (Intr. %s) Frames"
                    % (asset.get("Duration"), asset.get("IntrinsicDuration")),
                ),
                ui.stat(
                    label="Framerate",
                    value="%s FPS" % asset.get("FrameRate"),
                    # icon="ImageCrosshair",
                    caption="Edite Rate %s FPS" % asset.get("EditRate"),
                ),
            ],
        )
    ]
    probe = asset.get("Probe")
    if probe:
        items += [
            ui.text_l("Probe Summary"),
            ui.stats(
                justify="between",
                items=[
                    ui.stat(
                        label="Type",
                        value="%s" % probe.get("LabelSetType"),
                        # icon="ImageCrosshair",
                        # caption="Company %s" % probe.get("CompanyName"),
                    ),
                    ui.stat(
                        label="Aspect Ratio",
                        value="%s" % probe.get("AspectRatio"),
                        # icon="ImageCrosshair",
                        # caption="Aspect Ratio %s" % probe.get("ScreenAspectRatio"),
                    ),
                    ui.stat(
                        label="Average BitRate",
                        value="%s Mb/s" % probe.get("AverageBitRate"),
                        # icon="ScreenTime",
                        caption="Max. %s Mb/s" % probe.get("MaxBitRate"),
                    ),
                    ui.stat(
                        label="Encoder",
                        value="%s" % probe.get("ProductName"),
                        # icon="ImageCrosshair",
                        caption="%s" % (probe.get("ProductVersion")),
                    ),
                    ui.stat(
                        label="Resolution",
                        value="%s" % probe.get("Resolution"),
                        # icon="ImageCrosshair",
                        # caption="%s" % (probe.get("ProductVersion")),
                    ),
                    ui.stat(
                        label="Container Duration",
                        value="%s Frames" % probe.get("ContainerDuration"),
                        # icon="ImageCrosshair",
                        # caption="%s (Intr. %s) Frames" % (probe.get("Duration"), probe.get("IntrinsicDuration")),
                    ),
                    ui.stat(
                        label="Edite Rate",
                        value="%s FPS" % probe.get("EditRate"),
                        # icon="ImageCrosshair",
                        caption="Sample Rate %s FPS" % probe.get("SampleRate"),
                    ),
                ],
            ),
        ]

    items += [
        ui.expander(
            name="raw_probe_result_txt_exp",
            label="Raw Probe Results",
            items=[
                ui.markup(
                    name="raw_probe_result_txt",
                    content="<pre>%s</pre>" % yaml.dump(probe, indent=2),
                ),
            ],
        )
    ]

    return items

    # ui.expander(
    #    name="expander%s" % asset["Id"],
    #    label="Raw Data",
    #    items=[ui.text(md_table(flat(asset)))],
    # )

    """
    ui.stat(
                label="Entry Point",
                value=asset.get("EntryPoint"),
                #icon="ScreenTime",
                caption="13794 Frames",
            ),
            ui.stat(
                label="Out",
                value="1920x1080@24",
                #icon="ImageCrosshair",
                caption="Ration 1.85",
            ),
            ui.stat(
                label="Size",
                value="50.3 GB",
                icon="StorageOptical",
                caption="12391B",
            ),
    """


def add_reels_probe_cards(q, parse_report):
    for cpl in parse_report.get("cpl_list", []):
        infos = cpl["Info"]["CompositionPlaylist"]

        for reellist in infos["ReelList"]:
            items = []
            for asset_type, asset in reellist["Assets"].items():
                if asset_type == "Picture":
                    items += video_asset_details(asset)
            q.page.add(
                "cpl_reel_probe_%s" % reellist["Id"],
                ui.form_card(
                    box=ui.box("content", size=0),
                    items=[
                        ui.text_xl("CPL Reel Probe List %s" % reellist["Position"]),
                        ui.text_s("%s" % (reellist["Id"])),
                        ui.text_s("%s" % (reellist["AnnotationText"])),
                    ]
                    + items,
                ),
            )


def add_cpl_cards(q, parse_report):
    for cpl in parse_report.get("cpl_list", []):
        infos = cpl["Info"]["CompositionPlaylist"]

        # namings = {k: v.get("Value") for k, v in infos["NamingConvention"].items()}

        q.page.add(
            "cpl_infos_" + cpl["FileName"],
            ui.form_card(
                box=ui.box("content", size=0),
                items=[
                    ui.text_xl("Composition Playlist"),
                    ui.text_s(cpl["FilePath"]),
                    ui.expander(
                        name="cpl_naming_expander",
                        label="Naming Convention",
                        items=[
                            ui.text(md_table(flat(infos.get("NamingConvention")))),
                        ],
                    ),
                    # ui.text(make_markdown_table(namings.keys(), [namings.values()])),
                    ui.expander(
                        name="cpl_infos_expander",
                        label="Informations",
                        items=[
                            ui.text(md_table(infos)),
                        ],
                    ),
                    ui.expander(
                        name="cpl_sign_expander",
                        label="Security",
                        items=[
                            ui.text("Signer Inforamtions"),
                            ui.text(md_table(flat(infos.get("Signer")))),
                            ui.text("Signature Informations"),
                            ui.text(md_table(flat(infos.get("Signature")))),
                        ],
                    ),
                    ui.expander(
                        name="raw_cpl_data",
                        label="Raw CPL Data",
                        items=[full_table(flat(infos))],
                    ),
                ],
            ),
        )

        for reellist in infos["ReelList"]:
            q.page.add(
                "cpl_reel_%s" % reellist["Id"],
                ui.form_card(
                    box=ui.box("content", size=0),
                    items=[
                        ui.text_xl("CPL Reel List %s" % reellist["Position"]),
                        ui.text_s("%s" % (reellist["Id"])),
                        ui.text_s("%s" % (reellist["AnnotationText"])),
                    ]
                    + [
                        ui.expander(
                            name="expander%s" % reellist["AnnotationText"],
                            label=type,
                            items=[ui.text(md_table(flat(asset)))],
                        )
                        for type, asset in reellist["Assets"].items()
                    ],
                ),
            )


def add_am_cards(q, report):
    for assetmap in report.get("assetmap_list", []):
        cols = ["File", "Id", "VolId", "Offset", "Length", "PKL"]
        infos = assetmap["Info"]["AssetMap"]
        rows = [
            (
                asset["ChunkList"]["Chunk"].get("Path", ""),
                asset["Id"],
                asset["ChunkList"]["Chunk"].get("VolumeIndex", ""),
                asset["ChunkList"]["Chunk"].get("Offset", ""),
                asset["ChunkList"]["Chunk"].get("Length", ""),
                asset.get("PackingList", ""),
            )
            for asset in infos["AssetList"]["Asset"]
        ]

        q.page.add(
            "assetmap_infos_" + assetmap["FileName"],
            ui.form_card(
                box=ui.box("content", size=0),
                items=[
                    ui.text_xl("Asset Map"),
                    # ui.text_xl(pkl["FileName"]),
                    ui.text_s(assetmap["FilePath"]),
                    ui.text(make_md_table(cols, rows)),
                    ui.expander(
                        name="raw_assetmap_data",
                        label="Raw AM Data",
                        items=[full_table(flat(infos))],
                    ),
                ],
            ),
        )


"""if dcp.package_type != "OV":
    #if len(movx.get_ov_dcps(dcp.title)) > 1:
    check_form.append(
        ui.dropdown(name='dropdown', label='OV', required=True, width="500px",
                    choices=[ ui.choice(name=str(dcp.id), label=dcp.path) for dcp in movx.get_ov_dcps(dcp.title)
        ])
    )
else:
    dcp.ov_path = movx.get_ov_dcps(dcp.title)[0]
"""

# check_form.append(ui.button(name="dcp_check", label="Check DCP", value=str(dcp.uid)))


def checks_md_table(checks):
    if len(checks) == 0:
        return ui.text_s("Empty List")
    cols = ["Asset", "Name", "Result", "Message"]

    rows = []
    for check in checks:
        result = "bypass" if check["bypass"] else "pass"
        message = ""
        if len(check.get("errors")) > 0:
            result = ",".join(err["criticality"].lower() for err in check["errors"])
            message = "\r\n<br>\r\n".join(err["message"] for err in check["errors"])

        rows.append(
            [" > ".join(check["asset_stack"]), check["pretty_name"], result, message]
        )

    return ui.text(make_md_table(cols, rows))


def checks_full_table(checks):
    columns = [
        ui.table_column(
            name="name",
            label="Name",
            searchable=True,
            min_width="400px",
            sortable=True,
            link=False,
        ),
        ui.table_column(
            name="result",
            label="Result",
            cell_type=ui.tag_table_cell_type(
                name="Result_tags",
                tags=[
                    ui.tag(label="error", color="red"),
                    ui.tag(label="warning", color="yellow"),
                    ui.tag(label="pass", color="green"),
                    ui.tag(label="bypass", color="black"),
                ],
            ),
            searchable=True,
            filterable=True,
            sortable=True,
        ),
        ui.table_column(
            name="message",
            label="Message",
            cell_type=ui.markdown_table_cell_type(),
            min_width="300px",
            cell_overflow="wrap",
            searchable=True,
        ),
        ui.table_column(
            name="assets",
            label="Assets",
            min_width="300px",
            cell_overflow="wrap",
            searchable=True,
        ),
        ui.table_column(
            name="ref",
            label="Reference",
            cell_type=ui.markdown_table_cell_type(target="_blank"),
            min_width="300px",
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
            name="test_code",
            label="Test Code",
        ),
    ]

    rows = []

    for check in checks:
        result = "bypass" if check.get("bypass") else "pass"
        message = ""
        if len(check.get("errors", [])) > 0:
            result = ",".join(err.get("criticality", "").lower() for err in check.get("errors", []))
            message = "\r\n<br>\r\n".join(err.get("message", "") for err in check.get("errors", []))

        rows.append(
            ui.table_row(
                name=str(check.get("name", "")),
                cells=[
                    str(check.get("pretty_name", "unknown")),
                    result,
                    message,
                    " > ".join(check.get("asset_stack", [])),
                    str(check.get("doc", "")),
                    str(round(check.get("seconds_elapsed", 0))),
                    str(check.get("name", "")),
                ],
            )
        )

    return ui.table(
        name="check_result_table__",
        columns=columns,
        rows=rows,
        downloadable=True,
        tooltip="Result",
    )


def check_report_items(report):
    if report.get("valid") is None:
        return [ui.text("Report not valid")]

    summary = []

    if report.get("errors"):
        summary += [ui.text_xl("Errors"), checks_md_table(report.get("errors", []))]

    if report.get("warnings"):
        summary += [ui.text_xl("Warnings"), checks_md_table(report.get("warnings", []))]

    if report.get("bypass"):
        summary += [ui.text_xl("Ignored"), checks_md_table(report.get("bypass", []))]

    return [
        ui.inline(
            justify="between",
            items=[
                ui.text("%s tests executed" % (report.get("unique_checks_count", 0))),
                ui.text_xl(
                    "Check %s" % ("Passed" if report.get("valid") else "failed")
                ),
                ui.text("%d seconds" % (report.get("duration_seconds", 0))),
            ],
        ),
        ui.expander(
            name="expander",
            label="Check Summary",
            items=[
                ui.markup(
                    name="markup",
                    content="Message Summary<br><pre>%s</pre>" % report.get("message"),
                ),
            ]
            + summary,
        ),
    ]


def add_check_cards(q, report):
    q.page.add(
        "check_result_card",
        ui.form_card(
            box=ui.box("content", size=0),
            items=check_report_items(report)
            + [
                ui.expander(
                    name="expander",
                    label="Full Checks Reference",
                    items=[checks_full_table(report.get("checks", []))],
                ),
            ],
        ),
    )

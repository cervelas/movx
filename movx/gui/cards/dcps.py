from h2o_wave import ui
from movx.core.agent import JobType
from movx.core.db import Tags
from movx.gui import convert_size


def dcps_table(dcps):
    commands = [
        ui.command(
            name="dcp_check_action", label="Check", value=""
        ),
        ui.command(name="dcp_parse_action", label="Parse", value=""),
        ui.command(
            name="dcp_probe_acti0n", label="Probe", value=""
        ),
    ]

    columns = [
        #ui.table_column(
        #   name="actions",
        #   label="",
        #   max_width="25px",
        #   cell_type=ui.menu_table_cell_type(name="commands", commands=commands),
        #),
        ui.table_column(
            name="Title",
            label="Title",
            searchable=True,
            filterable=True,
            sortable=True,
            min_width="500px",
            link=True,
            #cell_type=ui.markdown_table_cell_type(target=""),
        ),
        ui.table_column(
            name="Movie",
            label="Movie",
            searchable=True,
            filterable=True,
            min_width="250px",
            #cell_type=ui.markdown_table_cell_type(target=""),
        ),
        ui.table_column(
            name="Location",
            label="Location",
            searchable=True,
            filterable=True,
            max_width="80px",
            #cell_type=ui.markdown_table_cell_type(target=""),
        ),
        ui.table_column(name="Type", label="Type", filterable=True, max_width="70px"),
        ui.table_column(name="Size", label="Size", max_width="80px", sortable=True),
        ui.table_column(
            name="Tags",
            label="tags",
            filterable=True,
            cell_type=ui.tag_table_cell_type(
                name="Tags",
                tags=[
                    ui.tag(label=tag.name, color=tag.color) for tag in Tags.get_all()
                ],
            ),
        ),
        # ui.table_column(name="Kind", label="Kind", filterable=True),
        ui.table_column(
           name="Last Check",
           label="Last Checks",
           filterable=True,
           cell_type=ui.tag_table_cell_type(
               name="tags",
               tags=[
                   ui.tag(label="scanned", color="$white"),
                   ui.tag(label="check ok", color="$red"),
                   ui.tag(label="ok", color="$mint"),
               ],
           ),
        ),
    ]

    return ui.table(
        name="dcp_list",
        columns=columns,
        rows=gen_dcps_rows(dcps),
        groupable=True,
        multiple=False,
        downloadable=True,
        resettable=True,
        height="calc(100vh - 90px)",
    )


def gen_dcps_rows(dcps):
    rows = []

    for dcp in dcps:
        loc_lnk = "Unknown"
        mov_lnk = "Unknown"
        last_check_ok = ""

        if dcp.movie is not None:
            #mov_lnk = "[%s](#mov/%s)" % (dcp.movie.title, dcp.movie.id)
            mov_lnk = dcp.movie.title
        if dcp.location is not None:
            #loc_lnk = "[%s](#loc/%s)" % (dcp.location.name, dcp.location.id)
            loc_lnk = dcp.location.name
        
        jobs = dcp.jobs(type=JobType.check)
        if len(jobs) > 0:
            if jobs[0].result.get("valid") is True:
                last_check_ok = "ok"
            else:
                last_check_ok = "fail"

        cells = [
            # "",
            #"[%s](#dcp/%s)" % (dcp.title, dcp.id),
            dcp.title,
            mov_lnk,
            loc_lnk,
            str(dcp.package_type),
            convert_size(dcp.size, exact=False),
            ",".join([t.name for t in dcp.tags]),
            # str(dcp.kind),
            last_check_ok
        ]

        rows.append(
            ui.table_row(
                name=str(dcp.id),
                cells=cells,
            )
        )

    return rows

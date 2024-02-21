from h2o_wave import ui
from movx.core.db import Tags


def dcps_table(dcps):
    columns = [
        # ui.table_column(
        #    name="actions",
        #    label="",
        #    max_width="25px",
        #    cell_type=ui.menu_table_cell_type(name="commands", commands=commands),
        # ),
        ui.table_column(
            name="Title",
            label="Title",
            searchable=True,
            filterable=True,
            min_width="500px",
            cell_type=ui.markdown_table_cell_type(target=""),
        ),
        ui.table_column(
            name="Movie",
            label="Movie",
            searchable=True,
            min_width="250px",
            cell_type=ui.markdown_table_cell_type(target=""),
        ),
        ui.table_column(
            name="Location",
            label="Location",
            searchable=True,
            max_width="80px",
            cell_type=ui.markdown_table_cell_type(target=""),
        ),
        ui.table_column(name="Type", label="Type", filterable=True, max_width="70px"),
        ui.table_column(name="Size", label="Size", max_width="80px"),
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
        # ui.table_column(
        #    name="Checks",
        #    label="Checks",
        #    filterable=True,
        #    cell_type=ui.tag_table_cell_type(
        #        name="tags",
        #        tags=[
        #            ui.tag(label="scanned", color="$white"),
        #            ui.tag(label="check ok", color="$red"),
        #            ui.tag(label="ok", color="$mint"),
        #        ],
        #    ),
        # ),
    ]

    return ui.table(
        name="all_dcp_list",
        columns=columns,
        rows=gen_dcps_rows(dcps),
        groupable=False,
        downloadable=True,
        resettable=True,
        height="calc(100vh - 90px)",
    )


def gen_dcps_rows(dcps):
    rows = []

    for dcp in dcps:
        loc_lnk = "Unknown"
        mov_lnk = "Unknown"
        if dcp.movie is not None:
            mov_lnk = "[%s](#mov/%s)" % (dcp.movie.title, dcp.movie.id)
        if dcp.location is not None:
            loc_lnk = "[%s](#loc/%s)" % (dcp.location.name, dcp.location.id)

        cells = [
            # "",
            "[%s](#dcp/%s)" % (dcp.title, dcp.id),
            mov_lnk,
            loc_lnk,
            str(dcp.package_type),
            str(dcp.size),
            ",".join([t.name for t in dcp.tags]),
            # str(dcp.kind),
        ]

        rows.append(
            ui.table_row(
                name=str(dcp.id),
                cells=cells,
            )
        )

    return rows

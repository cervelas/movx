from h2o_wave import ui, on

from movx.core.db import Tags
from movx.gui import make_md_table


def all_movies_table(movies):
    columns = [
        ui.table_column(
            name="Title",
            label="Title",
            searchable=True,
            filterable=True,
            min_width="500px",
            link=True,
        ),
        ui.table_column(
            name="Tags",
            label="tags",
            filterable=True,
            cell_type=ui.tag_table_cell_type(
                name="tags",
                tags=[ui.tag(label=tag.name, color=tag.color) for tag in Tags.get_all()]
                + [ui.tag(label="N/A", color="$CCCCCC")],
            ),
        ),
        ui.table_column(
            name="OVs",
            label="OVs",
        ),
        ui.table_column(
            name="VFs",
            label="VFs",
        ),
    ]

    rows = []
    for movie in movies:
        tags = []
        if movie.tags:
            tags = movie.tags
        rows.append(
            ui.table_row(
                name=str(movie.id),
                cells=[
                    movie.title,
                    ",".join([t.name for t in tags]),
                    str(len(movie.ovs())),
                    str(len(movie.vfs())),
                ],
            )
        )

    return ui.table(
        name="movies_table",
        columns=columns,
        rows=rows,
        downloadable=True,
        resettable=True,
        height="calc(100vh - 90px)",
    )


def add_movie_cards(q, movie):
    movie_tags = []

    if movie.tags:
        movie_tags = [t.name for t in movie.tags]

    available_tags = [t.name for t in Tags.get_all() if t.name not in movie_tags]

    q.page.add(
        "movie_header",
        ui.form_card(
            box=ui.box("infobar"),
            items=[
                ui.inline(
                    items=[
                        ui.text_xl("Movie %s" % movie.title),
                        ui.tags(
                            [ui.tag(color=t.color, label=t.name) for t in movie.tags]
                        ),
                        ui.picker(
                            name="movie_tags_picker",
                            label="Tags",
                            values=movie_tags,
                            choices=[
                                ui.choice(name=t, label=t) for t in available_tags
                            ],
                            trigger=True,
                        ),
                    ]
                ),
            ],
        ),
    )


def dcps_table(dcps):
    cols = ["Title", "Location", "Size", "Tags", "Probe", "Check"]

    rows = []
    for dcp in dcps:
        loc_lnk = "Unknown"
        if dcp.location is not None:
            loc_lnk = "[%s](#loc/%s)" % (dcp.location.name, dcp.location.id)
        tags = [
            '<span class="wave-w6 wave-s12" style="background-color:%s; border-radius: 4px; padding: 4px 8px;">%s</span>'
            % (tag.color, tag.name)
            for tag in dcp.tags
        ]
        rows.append(
            [
                "[%s](#dcp/%s)" % (dcp.title, dcp.id),
                loc_lnk,
                dcp.size,
                "".join(tags),
                "",
                "",
            ]
        )

    return ui.text(make_md_table(cols, rows))

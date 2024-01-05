from h2o_wave import ui, on

from movx.core.db import Tags


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

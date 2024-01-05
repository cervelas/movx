from h2o_wave import ui

from movx.core.db import Tags
from movx.gui import make_md_table


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

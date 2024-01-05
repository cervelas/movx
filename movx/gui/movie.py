from typing import List
from h2o_wave import Q, ui, on

from movx.core.db import Movie, Tags
from movx.gui import setup_page, debug_card


from movx.gui.cards.movie import add_movie_cards, dcps_table


@on()
async def movie_tags_picker(q):
    if q.client.current_movie:
        movie = Movie.get(q.client.current_movie)
        if movie:
            with movie.fresh() as m:
                names = [t.name for t in m.tags]
                new_tags = [t for t in q.args.movie_tags_picker if t not in names]
                tags = [Tags.filter(Tags.name == tag).first() for tag in new_tags]
                print(tags)
                for t in tags:
                    m.tags.append(t)


@on("#mov/{id}")
async def show_movie(q: Q, id: int):
    movie = Movie.get(id)

    if movie:
        q.client.current_movie = id

        setup_page(q, "%s Movie" % movie.title)

        add_movie_cards(q, movie)

        ovs = movie.ovs()

        if len(ovs) > 0:
            q.page["ovs_dcps_table"] = ui.form_card(
                box="content", items=[ui.text_l("OVs"), dcps_table(ovs)]
            )
        vfs = movie.vfs()

        if len(ovs) > 0:
            q.page["vfs_dcps_table"] = ui.form_card(
                box="content", items=[ui.text_l("VFs"), dcps_table(vfs)]
            )
        """
        for dcp in movx.get_movie_dcps(title) or []:
            q.page['dcp-' + str(dcp.uid)] = ui.form_card(box='content',
                items=[
                    ui.text_xl(dcp.full_title),
                    ui.text_l(dcp.package_type),
                    ui.text_m(str(dcp.path)),
                    #ui.inline(justify="between", items = [ ui.text_xl(title), ui.button(name='refresh_dcps', label='refresh')] ),
                    #make_movie_dcps_table(dcps),
                    ui.buttons([ui.button(name='#dcp/' + str(dcp.uid), label='View', primary=True)]),
                ]
            )
        """
    else:
        setup_page(q, "Not Found")
        q.page["not-found"] = ui.form_card(
            box="content", items=[ui.text("Movie %s not found" % id)]
        )

    await debug_card(q)

    await q.page.save()

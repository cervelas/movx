from h2o_wave import Q, ui, on

from movx.core.db import Movie
from movx.gui import setup_page

from movx.gui.cards import debug_card
from movx.gui.cards.movies import all_movies_table

@on()
async def movies_table(q):
    q.page["meta"] = ui.meta_card(box="", redirect="#mov/" + q.args.movies_table[0])
    await q.page.save()

@on("#movs")
async def show_movies(q: Q):
    setup_page(q, "Movies List")

    movies = Movie.get_all()

    q.page["full_movies_list"] = ui.form_card(
        box="content",
        items=[
            ui.inline(
                justify="between",
                items=[
                    ui.text_xl("Movies"),
                    ui.inline(
                        items=[
                            #ui.button(name="refresh_dcps", label="", icon="refresh"),
                            #ui.button(name="clear_all", label="clear_all"),
                            # ui.button(name='show_flat_list', label='Flat', icon="BulletedTreeList"),
                            # ui.button(name='show_detail_list', label='Details', icon="LineStyle"),
                            # ui.button(name='show_manage_list', label='Management', icon="WaitlistConfirm"),
                            # ui.button(name='hide_locs_list' if q.user.show_loc else 'show_locs_list',
                            #          label='Hide Locations' if q.user.show_loc else 'Locations', icon="OfflineStorageSolid")
                        ]
                    ),
                ],
            ),

            all_movies_table(movies),
        ]
    )
    

    await q.page.save()

from h2o_wave import Q, ui, on
from movx import core, WAVE_DATA_PATH
from movx.gui import setup_page
from movx.core.db import Location, DCP, Tags
from movx.gui.cards.dcp import add_infos_cards
from movx.gui.cards.dcps import dcps_table

@on("#loc/{id}")
async def show_loc(q: Q, id):

    location = Location.get(id)

    setup_page(q, "%s DCP's" % location.name)

    q.page["location_dcp_list"] = ui.form_card(
        box="content",
        items=[
            ui.inline(
                justify="between",
                items=[
                    ui.text_xl("%s DCP's" % location.name),
                    ui.inline(
                        items=[
                            ui.button(name="scan_location", label="", icon="refresh", value=str(location.id)),
                            # ui.button(name='show_flat_list', label='Flat', icon="BulletedTreeList"),
                            # ui.button(name='show_detail_list', label='Details', icon="LineStyle"),
                            # ui.button(name='show_manage_list', label='Management', icon="WaitlistConfirm"),
                            # ui.button(name='hide_locs_list' if q.user.show_loc else 'show_locs_list',
                            #          label='Hide Locations' if q.user.show_loc else 'Locations', icon="OfflineStorageSolid")
                        ]
                    ),
                ],
            ),
            dcps_table(location.dcps()),
        ],
    )

    await q.page.save()


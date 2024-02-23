from h2o_wave import Q, ui, on
from movx import core
from movx.gui import convert_size, setup_page
from movx.gui.cards.dcps import dcps_table
from movx.core.db import DCP, Location

"""
ffmpeg -ss 00:04:01 -i .\Persona_FTR-1_F-177_XX-EN_20_2K_SEED_20220531_JIN_IOP_OV\Persona_FTR-1_F-177_XX-EN_20_2K_SEED_20220531_JIN_IOP_OV_b44dc5eb-52ad-44_j2c.mxf -frames:v 1 -y  output.png
"""

@on("all_dcp_list")
async def on_row_clicked(q: Q):
   q.page["meta"] = ui.meta_card(box="", redirect="#dcp/" + q.args.all_dcp_list[0])
   await q.page.save()

# @on()
# async def dcp_parse_action(q):
#    core.dcps.parse( DCP.get( q.args.dcp_parse_action ) )
#    await main(q, q.args.dcp_parse_action )
#
# @on()
# async def dcp_check_action(q):
#    core.dcps.check( DCP.get( q.args.dcp_check_action ) )
#    await main( q, q.args.dcp_check_action )


@on("#dcps")
async def dcps_list(q: Q):
    setup_page(q, "DCP's")

    q.page["full_dcp_list"] = ui.form_card(
        box="content",
        items=[
            ui.inline(
                justify="between",
                items=[
                    ui.text_xl("All DCPs"),
                    ui.inline(
                        items=[
                            ui.button(name="refresh_dcps", label="", icon="refresh"),
                            ui.button(name="clear_all", label="clear_all"),
                            # ui.button(name='show_flat_list', label='Flat', icon="BulletedTreeList"),
                            # ui.button(name='show_detail_list', label='Details', icon="LineStyle"),
                            # ui.button(name='show_manage_list', label='Management', icon="WaitlistConfirm"),
                            # ui.button(name='hide_locs_list' if q.user.show_loc else 'show_locs_list',
                            #          label='Hide Locations' if q.user.show_loc else 'Locations', icon="OfflineStorageSolid")
                        ]
                    ),
                ],
            ),
            dcps_table(DCP.get_all()),
        ],
    )

    await q.page.save()


@on("#overview")
async def overview_items(q: Q):
    setup_page(q, "Overview")

    items = []

    stats = []
    total_size = 0

    colors = [
        "$red",
        "$pink",
        "$purple",
        "$tangerine",			
        "$teal",			
        "$violet",			
        "$yellow",
        "$page",
    ]

    for i, loc in enumerate(list(Location.get_all())):
        loc_size = 0
        for d in list(loc.dcps()):
            loc_size += d.size
            total_size += d.size
        if loc_size > 0:
            fraction = loc_size / total_size
        else:
            fraction = 0
        s = str(convert_size(loc_size, exact=False))

        stats.append(ui.pie(label=loc.name, value=loc.name, fraction=fraction, color=colors[i], aux_value=s))
    
    q.page['all_stat'] = ui.wide_pie_stat_card(
        box=ui.box('content', height="500px"),
        title='Total Size ' + convert_size(total_size, exact=False),
        pies=stats,
    )

    await q.page.save()
    


import concurrent.futures
import asyncio
import time

from h2o_wave import Q, ui, on
from movx.core import tasks
from movx.core import dcps as dcps
from movx.ui import setup_page, breadcrumbs
from movx.ui.cards.dcp import dcp_infos_card, check_card, pkl_infos, cpl_infos, assetmap_infos, all_dcps_table
from movx.core.db import DCP


@on()
async def dcp_parse_action(q):

    id = q.args.dcp_parse_action
    
    dcp = DCP.get(id)

    dcps.parse(dcp)

    await q.sleep(1)

    await dcp_layout(q, q.args["dcp_parse_action"])

@on()
async def dcp_check_action(q):
    print(q.args["dcp_check_action"])

    id = q.args["dcp_check_action"]
    
    dcp = DCP.get(id)

    dcps.check(dcp)

    await dcp_layout(q, q.args["dcp_check_action"])


@on('#dcp/{id}')
async def dcp_layout(q: Q, id):

    setup_page(q, "DCP " + id)

    
    dcp = DCP.get(id)

    if dcp:
            
        q.client.current_dcp = dcp
        
        last_report = tasks.get_last_result(dcp, "parse")

        last_check = tasks.get_last_result(dcp, "check")

        q.page["dcp_infos"] = dcp_infos_card(dcp)

        if last_check:
            q.page["dcp_check"] = check_card(last_check)
        
        for name, items in cpl_infos(last_report).items():
            q.page[name] = ui.form_card(box=ui.box('content', size=0), items=items)
        
        for name, items in pkl_infos(last_report).items():
            q.page[name] = ui.form_card(box=ui.box('content', size=0), items=items)
        
        for name, items in assetmap_infos(last_report).items():
            q.page[name] = ui.form_card(box=ui.box('content', size=0), items=items)
        
    else:
        q.page["not-found"] = ui.form_card(box="content", items=[
            ui.text("DCP with id %s not found" % id)
        ])

    await q.page.save()


@on('#dcps')
async def overview(q: Q):

    setup_page(q, "DCP's Overview")

    q.page['full_dcp_list'] = ui.form_card(box='content',
        items=[
            ui.inline(justify="between", items = [  ui.text_xl("Overview"), 
                                                    ui.inline(items = [   
                                                        ui.button(name='refresh_dcps', label='', icon="refresh"),
                                                        ui.button(name='clear_all', label='clear_all'),
                                                        #ui.button(name='show_flat_list', label='Flat', icon="BulletedTreeList"),
                                                        #ui.button(name='show_detail_list', label='Details', icon="LineStyle"),
                                                        #ui.button(name='show_manage_list', label='Management', icon="WaitlistConfirm"),
                                                        #ui.button(name='hide_locs_list' if q.user.show_loc else 'show_locs_list', 
                                                        #          label='Hide Locations' if q.user.show_loc else 'Locations', icon="OfflineStorageSolid")
                                                        ])
                                                    ]),
            all_dcps_table(DCP.get_all()),
        ]
    )

    '''
    stats = []
    total_size = 0

    
    for d in dcps.get_all():
        total_size += d.metadata.get("size_bytes", 0)
    for name, loc in movx.locations.items():
        loc_size = 0
        for d in movx.get_location_dcps(loc):
            loc_size += d.metadata.get("size_bytes", 0)
        if loc_size > 0:
            fraction = loc_size / total_size
        else:
            fraction = 0
        stats.append(ui.pie(label=name, value=convert_size(loc_size), fraction=fraction, color="$red", aux_value=convert_size(loc_size)))

    q.page['stat'] = ui.wide_pie_stat_card(
        box=ui.box('footer', size=3),
        title='Total Size ' + convert_size(total_size),
        pies=stats,
    )
    '''
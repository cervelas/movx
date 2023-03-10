import math
from movx.core.movx import movx
from movx.ui.list import make_flat_dcps_table, make_movie_dcps_table
from movx.ui import setup_page, breadcrumbs, locations
from h2o_wave import main, app, Q, ui, on, handle_on
from movx.ui.dcp import dcp_infos_card, cpl_infos_card, pkl_infos_card, assetmap_infos_card, dcp_parse, dcp_check


@on('movie_list')
async def on_row_clicked(q: Q):
    print("row clicked " + q.args.movie_list[0])
    q.page['meta'] = ui.meta_card(box='', redirect=q.args.movie_list[0])
    await q.page.save()

@on('full_list')
async def on_row_clicked(q: Q):
    print("row clicked " + q.args.full_list[0])
    q.page['meta'] = ui.meta_card(box='', redirect=q.args.full_list[0])
    await q.page.save()

async def display_homepage(q: Q):
    if q.args.show_locs_list:
        q.user.show_loc = True
    elif q.args.hide_locs_list:
        q.user.show_loc = False
    
    setup_page(q, "DCP List", "side" if q.user.show_loc else "full")

    breadcrumbs(q)

    if q.user.show_loc:
        locations.show_locs_list(q)

    q.page['full_dcp_list'] = ui.form_card(box='content',
        items=[
            ui.inline(justify="between", items = [  ui.text_xl(""), 
                                                    ui.inline(items = [   
                                                        ui.button(name='refresh_dcps', label='', icon="refresh"),
                                                        #ui.button(name='show_flat_list', label='Flat', icon="BulletedTreeList"),
                                                        #ui.button(name='show_detail_list', label='Details', icon="LineStyle"),
                                                        #ui.button(name='show_manage_list', label='Management', icon="WaitlistConfirm"),
                                                        ui.button(name='hide_locs_list' if q.user.show_loc else 'show_locs_list', 
                                                                  label='Hide Locations' if q.user.show_loc else 'Locations', icon="OfflineStorageSolid")
                                                        ])
                                                    ]),
            make_flat_dcps_table(movx.dcps),
        ]
    )

    def convert_size(size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    stats = []
    total_size = 0
    for d in movx.dcps:
        total_size += d.metadata.get("size_bytes", 0)
    for name, loc in movx.locations.items():
        loc_size = 0
        for d in movx.get_location_dcps(loc):
            print(d)
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

@on('#movie/{title}')
async def movie_layout(q: Q, title):
    setup_page(q, title)
    breadcrumbs(q, [ ("current", title) ])
    
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
    await q.page.save()


@app('/movx')
async def serve(q: Q):
    movx.load()

    if q.args["dcp_parse"]:
        dcp_parse(q)

    if q.args["dcp_check"]:
        await dcp_check(q)
        movx.save()

    if q.args['#'] is None:
        await display_homepage(q)

    await handle_on(q)


    '''
    q.page['sidebar-header'] = ui.header_card(
        box=ui.box(zone='sidebar', size='0'),
        title='Locations',
        subtitle="",
        #image='https://wave.h2o.ai/img/h2o-logo.svg',
        items=[
            ui.button(name='show_add_location', label='add')
        ],
        color='transparent'
    )

    for i,l in enumerate(locations_list()):
        q.page['loc%s' % i] = l'''


    '''
    def check_net_disk(d):
        lines = subprocess.check_output(['net', 'use', d]).split(b'\r\n')
        if "not found" not in lines[0]: 
            ret = {}
            for l in lines:
                kv = l.split(b'\t')
                ret.update( { kv[0]: kv[1] } )
            return ret

    for d in get_drives():
        # check network usage
        is_net = check_net_disk(d[0])
        if is_net is not None and is_net["Status"] != "Disconnected":
            print("check %s" % d)
            try:
                print(os.stat(d))
                dirs = [f.path for f in os.scandir(d) if f.is_dir()]
                print(dirs)
            except Exception as e:
                print(e)

    '''
    await q.page.save()
import concurrent.futures
import asyncio
import time
import pprint

from h2o_wave import Q, ui, on
from movx.core.movx import movx
from movx.ui import setup_page, breadcrumbs


async def dcp_check(q):
    dcp = movx.get_dcp(q.args.dcp_check)
    dcp.dcp._parsed = False
    page = q.page.add('check_progress', ui.form_card(box="header", items = [
            ui.progress(
                label='Check',
                caption=f'progress',
                value=0,
            )]
        )
    )
    
    await q.page.save()
    loop = asyncio.get_event_loop()
    async def prog(value, file, elapsed):
        str_time = time.strftime("%H:%M:%S", time.gmtime(elapsed))
        page.items[0].progress.value = value
        page.items[0].progress.label = "Checking " + file
        page.items[0].progress.caption = "Elapsed %s" % str_time
        await q.page.save()

    def check_callback(file_path, file_processed, file_size, file_elapsed):
        percent = file_processed/file_size
        future = asyncio.run_coroutine_threadsafe(prog(percent, file_path, file_elapsed), loop)
        future.result()

    with concurrent.futures.ThreadPoolExecutor() as pool:
        report = await q.exec(pool, dcp.check, None, check_callback)
        page = q.page.add('result', 
                ui.template_card(box="header", title="Check Report Result", content="<pre>" + report.pretty_str() + "<pre>")
        )

def dcp_parse(q):
    dcp = movx.get_dcp(q.args.dcp_parse)
    if dcp:
        dcp.parse()
        print(dcp.metadata)

def dcp_infos_card(q: Q, dcp):
    infos = one_level_dict(dcp.metadata)

    if len(dcp.metadata.get("cpl_list", [])) > 0:
        namings = dcp.metadata["cpl_list"][0]["Info"]["CompositionPlaylist"]["NamingConvention"]
        infos.update({ k: v.get("Value") for k, v in namings.items() })
    
    infos.pop("path", None)
    infos.pop("package_type", None)
    infos.pop("PackageType", None)

    q.page['dcp_infos_' + str(dcp.uid)] = ui.form_card(box=ui.box('header', size=0),
        items=[
            ui.inline(justify="between", items = [  
                ui.text_xl(dcp.full_title),
                ui.button(name="dcp_parse", label="Refresh", value=str(dcp.uid)),
            ] ),
            ui.text_s(dcp.metadata.get("path", "")),
            ui.text(make_markdown_table(infos.keys(), [ infos.values() ]))
        ]
    )

def dcp_check_card(q: Q, dcp):
    
    if len(dcp.report) > 0:
        columns = [
            ui.table_column(name='name', label='Name', searchable=True, min_width="400px"),
            ui.table_column(name='bypass', label='bypass', filterable=True, max_width="70px"),
            ui.table_column(name='errors_count', label='errors', searchable=True, filterable=True, max_width="60px"),
            ui.table_column(name='sec_elapsed', label='Time', max_width="40px"),
            ui.table_column(name='errors', label='Error', cell_type=ui.markdown_table_cell_type(target='_blank'), min_width="300px"),
            ui.table_column(name='doc', label='Doc', cell_type=ui.markdown_table_cell_type(target='_blank'),  min_width="800px"),
        ]
        
        check_form = [  ]
        if dcp.package_type != "OV":
            if len(movx.get_ov_dcps(dcp.title)) > 1:
                check_form.append(
                    ui.dropdown(name='dropdown', label='Dropdown', required=True, placeholder="Select OV DCP",
                                choices=[ ui.choice(name=str(dcp.uid), label=dcp.path.absolute()) for dcp in movx.get_ov_dcps(dcp.title)
                    ])
                )
            else:
                dcp.ov_path = movx.get_ov_dcps(dcp.title)[0]
        check_form.append(ui.button(name="dcp_check", label="Check DCP", value=str(dcp.uid)))

        q.page['check_result_' + str(dcp.uid)] = ui.form_card(box=ui.box('header', size=0),
                items=[ 
                        ui.inline(justify="between", items = [  
                                ui.text_xl("Last Check %s @ %s" % ("PASS" if dcp.report["valid"] else "FAIL", dcp.report["date"]))
                            ] + check_form),
                        ui.expander(name="expander", label="Check Summary", items=[
                            ui.markup(name='markup', content="<pre>%s</pre>" % dcp.report["message"]),
                        ]),
                        ui.expander(name="expander", label="Checks List", items=[
                            ui.table(
                                name='check_result_list',
                                columns=columns,
                                rows=[ 
                                        ui.table_row(name=check["name"], cells=[check["pretty_name"], 
                                                                                str(check["bypass"]), 
                                                                                str(len(check["errors"])), 
                                                                                str(check["seconds_elapsed"]),
                                                                                "\r\n".join([ err["criticality"] + ": " + err["message"] for err in check["errors"] ]), 
                                                                                check["doc"]]) for check in dcp.report["checks"]
                                    ],
                                downloadable=True,
                                height="600px"
                            )
                        ])
                ]
            )
    else:
        q.page['check_result_' + str(dcp.uid)] = ui.form_card(box=ui.box('header', size=0),
                items=[
                        ui.inline(justify="between", items = [  
                            ui.text_xl("No Check report"),
                            ui.button(name="dcp_check", label="Check DCP", value=str(dcp.uid)),
                        ]),
                ]
            )


def cpl_infos_card(q: Q, dcp):
    for cpl in dcp.metadata.get("cpl_list") or []:
        infos = cpl["Info"]["CompositionPlaylist"]
        
        namings = { k: v.get("Value") for k, v in infos["NamingConvention"].items() }
        
        for reellist in infos["ReelList"]:
            reels = [ ui.expander(name="expander", label=type, items=[
                        ui.text(dict_to_table(asset))  
                    ]) for type, asset in reellist["Assets"].items() ]
            q.page['reel_list_' + reellist["Id"]] = ui.form_card(box=ui.box('sidebar', size=0),
                items=[
                    ui.text_xl("Playlist Reels"),
                    ui.text_s(str(reellist["AnnotationText"])),
                ] + reels
            )    
        
        q.page['cpl_infos_' + cpl["FileName"]] = ui.form_card(box=ui.box('sidebar', size=0),
            items=[
                ui.text_xl("Composition Playlist"),
                ui.text_s(cpl["FilePath"]),
                #ui.text(make_markdown_table(namings.keys(), [ namings.values() ])),
                ui.expander(name="expander", label="Informations", items=[
                    ui.text(dict_to_table(infos))  
                ])
            ]
        )


def pkl_infos_card(q: Q, dcp):
    for pkl in dcp.metadata.get("pkl_list") or []:
        infos = pkl["Info"]["PackingList"]
        assets = []
        for a in infos["AssetList"]["Asset"]:
            assets.append(
                ui.expander(name="expander", label=a.get("Path", "Unkown"), items=[
                    ui.text(dict_to_table(a)) 
            ]))
            #assets.append(ui.text_l(a["OriginalFileName"]))
            #assets.append(ui.text_m(a.get("AnnotationText", "")))
            #assets.append(ui.separator(label=''))
        q.page['pkl_infos_' + pkl["FileName"]] = ui.form_card(box=ui.box('content', size=0),
            items=[
                ui.text_xl("Packing List"),
                #ui.text_xl(pkl["FileName"]),
                ui.text_s(pkl["FilePath"]),
            ] + assets
        )

def assetmap_infos_card(q: Q, dcp):
    for assetmap in dcp.metadata.get("assetmap_list") or []:
        infos = assetmap["Info"]["AssetMap"]
        assets = [ (asset["Id"], asset["ChunkList"]["Chunk"]["Path"]) for asset in infos["AssetList"]["Asset"] ]
        
        q.page['assetmap_infos_' + assetmap["FileName"]] = ui.form_card(box=ui.box('content', size=0),
            items=[
                ui.text_xl("Asset Map"),
                #ui.text_xl(pkl["FileName"]),
                ui.text_s(assetmap["FilePath"]),
                ui.text(make_markdown_table(fields=["Id", "Path"], rows=assets) )
            ]
        )


@on('#dcp/{uid}')
async def dcp_layout(q: Q, uid):
    setup_page(q, "DCP " + uid, layout="2cols")
    
    dcp = movx.get_dcp(uid)

    if dcp:

        breadcrumbs(q, [ ("#movie/" + dcp.title, dcp.title),
                        ('current', dcp.full_title) ])
        
        dcp_infos_card(q, dcp)
        dcp_check_card(q, dcp)
        cpl_infos_card(q, dcp)
        pkl_infos_card(q, dcp)
        assetmap_infos_card(q, dcp)

    else:

        q.page["not-found"] = ui.form_card(box="header", items=[
            ui.text(uid + " DCP not found")
        ])

    await q.page.save()

def one_level_dict(dic):
    ret = {}
    for k, v in dic.items():
        if not isinstance(v, dict) and not isinstance(v, list):
            ret.update( {k: v} )
    return ret


def dict_to_table(dic):
    rows = []
    for k, v in dic.items():
        if not isinstance(v, dict) and not isinstance(v, list):
            rows.append([k, v])
    return make_markdown_table(["Name", "Value"], rows)

def make_markdown_row(values):
    return f"| {' | '.join([str(x) for x in values])} |"


def make_markdown_table(fields, rows):
    return '\n'.join([
        make_markdown_row(fields),
        make_markdown_row('-' * len(fields)),
        '\n'.join([make_markdown_row(row) for row in rows]),
    ])

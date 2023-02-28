import concurrent.futures
import asyncio
import time

from h2o_wave import app, Q, ui, main, on
from movx.core.movx import movx
from movx.ui import setup_page


@on()
async def parse_dcp(q):
    dcp = movx.get(q.args.parse_dcp)
    dcp.dcp._parsed = False
    dcp.parse()
    await q.page.save()

@on()
async def check_dcp(q):
    dcp = movx.get(q.args.check_dcp)
    dcp.dcp._parsed = False
    page = q.page.add('check', ui.form_card(box="header", items = [
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

        #page.save()
    # Execute our long-running function in the background
    with concurrent.futures.ThreadPoolExecutor() as pool:
        report = await q.exec(pool, dcp.check, None, check_callback)
        del q.page["check"]
        page = q.page.add('result', 
                ui.template_card(box="header", title="Check Report Result", content="<pre>" + report.pretty_str() + "<pre>")
        )

def dcp_infos_card(q: Q, dcp):
    dcp.parse()
    infos = one_level_dict(dcp.dcp_metadata)
    if infos.get("path"):
        del infos["path"]
    
    namings = dcp.dcp_metadata["cpl_list"][0]["Info"]["CompositionPlaylist"]["NamingConvention"]

    namings = { k: v.get("Value") for k, v in namings.items() }

    q.page['title_' + str(dcp.uri)] = ui.form_card(box='header',
        items=[
            ui.inline(justify="between", items = [  
                ui.text_xl(dcp.full_title),
                ui.button(name="parse_dcp", label="Parse", value=str(dcp.uri)),
                ui.button(name="check_dcp", label="Check", value=str(dcp.uri)),
            ],  ),
            ui.text_s(dcp.dcp_metadata.get("path", "")),
            ui.text(make_markdown_table(namings.keys(), [ namings.values() ])),
            ui.text(make_markdown_table(infos.keys(), [ infos.values() ]))
        ]
    )

def cpl_infos_card(q: Q, dcp):
    for cpl in dcp.dcp_metadata.get("cpl_list") or []:
        infos = cpl["Info"]["CompositionPlaylist"]
        
        namings = { k: v.get("Value") for k, v in infos["NamingConvention"].items() }
        
        for reellist in infos["ReelList"]:
            reels = [ ui.expander(name="expander", label=type, items=[
                        ui.text(dict_to_table(asset))  
                    ]) for type, asset in reellist["Assets"].items() ]
            q.page['reel_list_' + reellist["Id"]] = ui.form_card(box='sidebar',
                items=[
                    ui.text_xl("Reels"),
                    ui.text_s(reellist["AnnotationText"]),
                ] + reels
            )    
        
        q.page['cpl_infos_' + cpl["FileName"]] = ui.form_card(box='sidebar',
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
    for pkl in dcp.dcp_metadata.get("pkl_list") or []:
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
        q.page['pkl_infos_' + pkl["FileName"]] = ui.form_card(box='content',
            items=[
                ui.text_xl("Packing List"),
                #ui.text_xl(pkl["FileName"]),
                ui.text_s(pkl["FilePath"]),
            ] + assets
        )

def assetmap_infos_card(q: Q, dcp):
    for assetmap in dcp.dcp_metadata.get("assetmap_list") or []:
        infos = assetmap["Info"]["AssetMap"]
        assets = [ (asset["Id"], asset["ChunkList"]["Chunk"]["Path"]) for asset in infos["AssetList"]["Asset"] ]
        
        q.page['assetmap_infos_' + assetmap["FileName"]] = ui.form_card(box='content',
            items=[
                ui.text_xl("Asset Map"),
                #ui.text_xl(pkl["FileName"]),
                ui.text_s(assetmap["FilePath"]),
                ui.text(make_markdown_table(fields=["Id", "Path"], rows=assets) )
            ]
        )


def layout_dcp(q: Q, dcp):

    dcps = [] 

    
    if dcp is not None:
        #dcp.parse()
        
        q.page['title_list'] = ui.form_card(box='content',
            items=[
                ui.inline(justify="between", items = [  ui.text_xl("DCP " + dcp.full_title)] ),
                
            ]
        )

        q.page['asset_list'] = ui.form_card(box='content',
            items=[
                ui.text_xl("Asset List"),
                ui.text(make_markdown_table(
                    fields=["Id", "File"],
                    rows=[ [ id, f ] for id, f in dcp.dcp_metadata["asset_list"].items() ],
                )),
            ]
        )

        assetmap = dcp.dcp_metadata["assetmap_list"][0]["Info"]["AssetMap"]
        assets_from_assetmap = []
        for asset in assetmap["AssetList"]["Asset"]:
            assets_from_assetmap.append([ asset["Id"], asset["ChunkList"]["Chunk"]["Path"]])
        
        q.page['asset_Map'] = ui.form_card(box='content',
            items=[
                ui.text_xl("AssetMap"),
                ui.text(assetmap["Id"]),
                ui.text(assetmap["Creator"]),
                ui.text(assetmap["IssueDate"]),
                ui.text(assetmap["Issuer"]),
                ui.text(assetmap["Schema"]),
                ui.text(make_markdown_table(
                    fields=["Id", "Path"],
                    rows=assets_from_assetmap,
                )),
            ]
        )
        print("map ok")

        playlist = dcp.dcp_metadata["cpl_list"][0]["Info"]["CompositionPlaylist"]
        reels = []
        for name, reel in playlist["ReelList"][0]["Assets"].items():
            reels.append([ name, reel["AbsolutePath"]])
        
        q.page['PlayList'] = ui.form_card(box='content',
            items=[
                ui.text_xl("PlayList"),
                ui.text(playlist["Id"]),
                ui.text(playlist["Creator"]),
                ui.text(playlist["IssueDate"]),
                ui.text(playlist["Issuer"]),
                ui.text(str(playlist["FrameRate"])),
                ui.text(make_markdown_table(
                    fields=["Type", "Path"],
                    rows=reels,
                )),
            ]
        )
        print("cpl ok")
    else:
        print("NO DCP")
        q.page["info"] = ui.form_card(box="content", items=[
            ui.text(f"no DCP foud ({uri})")
        ])


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

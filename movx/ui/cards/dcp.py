import pprint
import random
from h2o_wave import ui
from movx.ui import convert_size, dict_to_table, make_markdown_table, flatten_dict, dict_to_searchable_table
from movx.core.db import Status


def all_dcps_table(dcps):
    
    commands = [
        ui.command(name='details', label='Details', icon='Info'),
        ui.command(name='dcp_parse_action', label='Parse', icon='Info'),
    ]

    columns = [
            ui.table_column(name='actions', label='', max_width="25px",
                            cell_type=ui.menu_table_cell_type(name='commands', commands=commands)),
        ui.table_column(name='Title', label='Title', searchable=True, filterable=True, min_width="500px", link=True),
        ui.table_column(name='Movie', label='Movie', searchable=True, filterable=True, min_width="250px"),
        ui.table_column(name='Location', label='Location', filterable=True,  max_width="80px" ),
        ui.table_column(name='Type', label='Type', filterable=True, max_width="70px"),
        ui.table_column(name='Size', label='Size', max_width="80px"),

        ui.table_column(name='Status', label='Status', filterable=True, cell_type=ui.tag_table_cell_type(name='tags', tags=[
            ui.tag(label=status.name, color=status.color) for status in Status.get_all()
        ] + [ ui.tag(label='N/A', color='$CCCCCC') ])),

        ui.table_column(name='Kind', label='Kind', filterable=True),

        ui.table_column(name='Checks', label='Checks', filterable=True, cell_type=ui.tag_table_cell_type(name='tags', tags=[
                ui.tag(label="scanned", color='$white'),
                ui.tag(label="check ok", color='$red'),
                ui.tag(label="ok", color='$mint'),
            ]
        )),
    ]

    rows = []
    for dcp in dcps:
        check = "?"
        #if dcp.report.get("valid") == True:
        #    check = "ok" 
        #elif dcp.report.get("valid") == False:
        #    check = "fail"
        loc = "Unknown"
        movie = "Unknown"
        if dcp.movie is not None:
            movie = dcp.movie.title
        if dcp.location is not None:
            loc = dcp.location.name
        rows.append(ui.table_row(name=str(dcp.id), cells=['', dcp.title, movie,
                                                str(loc),
                                                dcp.package_type,
                                                str(dcp.size),
                                                dcp.status.name if dcp.status else 'N/A',
                                                str(dcp.kind),
                                                check
                    ]))

    return ui.table(
        name='all_dcp_list',
        columns=columns,
        rows=rows,
        groupable=True,
        downloadable=True,
        resettable=True,
        height="calc(100vh - 50px)"
    )


def movie_dcps_table(dcps):
        
    commands = [
        ui.command(name='details', label='Details', icon='Info'),
        ui.command(name='dcp_check_action', label='Check', icon='VerifiedBrandSolid'),
    ]

    columns = [
            ui.table_column(name='actions', label='', max_width="25px",
                            cell_type=ui.menu_table_cell_type(name='commands', commands=commands)),
        ui.table_column(name='Title', label='Title', searchable=True, filterable=True, min_width="500px", link=True),
        ui.table_column(name='Location', label='Location', filterable=True,  max_width="80px" ),
        ui.table_column(name='Size', label='Size', max_width="80px"),
        ui.table_column(name='Status', label='Status', filterable=True, cell_type=ui.tag_table_cell_type(name='tags', tags=[
            ui.tag(label=status.name, color=status.color) for status in Status.get_all()
        ] + [ ui.tag(label='N/A', color='$CCCCCC') ])),
        ui.table_column(name='Check', label='Check', filterable=True, cell_type=ui.tag_table_cell_type(name='tags', tags=[
                ui.tag(label="?", color='$white'),
                ui.tag(label="fail", color='$red'),
                ui.tag(label="ok", color='$mint'),
            ]
        )),
    ]

    rows = []
    for dcp in dcps:
        check = "?"
        #if dcp.report.get("valid") == True:
        #    check = "ok" 
        #elif dcp.report.get("valid") == False:
        #    check = "fail"
        loc = "Unknown"
        if dcp.location is not None:
            loc = dcp.location.name
        rows.append(ui.table_row(name=str(dcp.id), cells=['', dcp.title,
                                                str(loc),
                                                str(dcp.size),
                                                dcp.status.name if dcp.status else 'N/A',
                                                check,
                    ]))

    return ui.table(
        name='movie_dcp_list',
        columns=columns,
        rows=rows,
        downloadable=True,
        resettable=True,
    )

def dcp_infos_card(dcp):

    return ui.form_card(box=ui.box('content', size=0),
        items=[
            ui.inline(items = [
                ui.text_xl(dcp.title),
                ui.button(name="dcp_parse_action", label="Refresh", value=str(dcp.id)),
                ui.button(name="dcp_check_action", label="Check", value=str(dcp.id)),
                ui.dropdown(name='status_dropdown', label='Pick one', value='B', required=True, choices=[
                    ui.choice(status.name, status.name) for status in Status.get_all()
                ]),
            ] ),
            ui.text_s(dcp.path),
            #ui.text(make_markdown_table(infos.keys(), [ infos.values() ]))
        ]
    )

def check_card(report):

    columns = [
        ui.table_column(name='name', label='Name', searchable=True, min_width="400px"),
        ui.table_column(name='bypass', label='bypass', filterable=True, max_width="70px"),
        ui.table_column(name='errors_count', label='errors', searchable=True, filterable=True, max_width="60px"),
        ui.table_column(name='sec_elapsed', label='Time', max_width="40px"),
        ui.table_column(name='errors', label='Error', cell_type=ui.markdown_table_cell_type(target='_blank'), min_width="300px"),
        ui.table_column(name='doc', label='Doc', cell_type=ui.markdown_table_cell_type(target='_blank'),  min_width="800px"),
    ]

    check_form = [  ]
    
    '''if dcp.package_type != "OV":
        #if len(movx.get_ov_dcps(dcp.title)) > 1:
        check_form.append(
            ui.dropdown(name='dropdown', label='OV', required=True, width="500px",
                        choices=[ ui.choice(name=str(dcp.id), label=dcp.path) for dcp in movx.get_ov_dcps(dcp.title)
            ])
        )
    else:
        dcp.ov_path = movx.get_ov_dcps(dcp.title)[0]'''

    #check_form.append(ui.button(name="dcp_check", label="Check DCP", value=str(dcp.uid)))
    
    return ui.form_card(box=ui.box('content', size=0),
            items=[
                    ui.inline(justify="between", items = [
                            ui.text_xl("Last Check %s @ %s" % ("PASS" if report.get("valid") else "FAIL", report.get("date")))
                        ] + check_form),
                    ui.expander(name="expander", label="Check Summary", items=[
                        ui.markup(name='markup', content="<pre>%s</pre>" % report.get("message")),
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
                                                                            check["doc"]]) for check in report.get("checks", {})
                                ],
                            downloadable=True,
                            height="600px"
                        )
                    ])
            ]
        )


def pkl_infos(metadata):
    items = {}
    for pkl in metadata.get("pkl_list", []):
        infos = pkl["Info"]["PackingList"]
        assets = []
        for a in infos["AssetList"]["Asset"]:
            a["Human Size"] = convert_size(a["Size"])
            assets.append(
                ui.expander(name="expander", label=a.get("Path", "Unkown"), items=[
                    ui.text(dict_to_table(a))
            ]))
            #assets.append(ui.text_l(a["OriginalFileName"]))
            #assets.append(ui.text_m(a.get("AnnotationText", "")))
            #assets.append(ui.separator(label=''))
        items['pkl_infos_' + pkl["FileName"]] = [
                ui.text_xl("Packing List"),
                #ui.text_xl(pkl["FileName"]),
                ui.text_s(pkl["FilePath"]),
            ] + assets + [
                ui.expander(name="expander", label="Raw PKL Data", items=[
                    dict_to_searchable_table(infos)
                ])
            ]

    return items


def cpl_infos(metadata):
    items = {}

    for cpl in metadata.get("cpl_list", []):
        infos = cpl["Info"]["CompositionPlaylist"]

        namings = { k: v.get("Value") for k, v in infos["NamingConvention"].items() }

        reels = []
        for reellist in infos["ReelList"]:
            reels += [
                    ui.text_l("Reel List %s: %s" % (reellist["Position"], reellist["Id"])),
                    ui.text_s("%s" % (reellist["AnnotationText"])),
                ] + [ ui.expander(name="expander%s" % reellist["AnnotationText"], label=type, items=[
                        ui.text(dict_to_table(flatten_dict(asset)))
                ]) for type, asset in reellist["Assets"].items() ]


        items['cpl_infos_' + cpl["FileName"]] = [
                ui.text_xl("Composition Playlist"),
                ui.text_s(cpl["FilePath"]),
                ui.text(make_markdown_table(namings.keys(), [ namings.values() ])),
                ui.expander(name="cpl_expander", label="CPL Informations", items=[
                    ui.text(dict_to_table(infos)),
                ]),
            ] + reels + [
                ui.expander(name="raw_cpl_data", label="Raw CPL Data", items=[
                    dict_to_searchable_table(infos)
                ])
            ]

    return items


def assetmap_infos(metadata):
    items = {}
    for assetmap in metadata.get("assetmap_list", []):
        infos = assetmap["Info"]["AssetMap"]
        assets = [ (asset["Id"], asset["ChunkList"]["Chunk"]["Path"]) for asset in infos["AssetList"]["Asset"] ]

        items['assetmap_infos_' + assetmap["FileName"]] = [
                ui.text_xl("Asset Map"),
                #ui.text_xl(pkl["FileName"]),
                ui.text_s(assetmap["FilePath"]),
                ui.text(make_markdown_table(fields=["Id", "Path"], rows=assets) ),
                ui.expander(name="raw_assetmap_data", label="Raw CPL Data", items=[
                    dict_to_searchable_table(infos)
                ])
            ]
    return items
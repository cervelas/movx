
from h2o_wave import ui, on, Q

commands = [
    ui.command(name='details', label='Details', icon='Info'),
]

'''
groups_title = {}
for dcp in dcps:
    if dcp.title not in groups_title:
        groups_title.update( { dcp.title: [] } )

    groups_title[dcp.title].append( dcp )
'''

'''
    groups=[ 
    ui.table_group(n,
        [ ui.table_row(name="dcp-" + dcp.uid, cells=[dcp.title, dcp.full_title, dcp.location, dcp.package_type]) for dcp in dcps ],
        collapsed=False
    ) for n, dcps in groups_title.items()
],
'''

def make_flat_dcps_table(dcps):
    columns = [
        ui.table_column(name='Movie', label='Movie', searchable=True, filterable=True, min_width="150px", link=False),
        ui.table_column(name='Title', label='Title', searchable=True, filterable=True, min_width="500px"),
        ui.table_column(name='Location', label='Location', filterable=True,  max_width="50px" ),
        ui.table_column(name='Type', label='Type', filterable=True),
        ui.table_column(name='Size', label='Size'),
        ui.table_column(name='Status', label='Status', filterable=True),
        ui.table_column(name='Check', label='Check', filterable=True, cell_type=ui.icon_table_cell_type()),
        ui.table_column(name='Path', label='Path'),
    ]

    rows = []
    for dcp in dcps:
        check = "StatusCircleQuestionMark"
        if dcp.report.get("valid") == True:
            check = "CompletedSolid" 
        elif dcp.report.get("valid") == False:
            check = "StatusErrorFull"
        rows.append(ui.table_row(name='#dcp/' + str(dcp.uid)  , cells=[dcp.title, dcp.full_title,
                                                str(dcp.location.name),
                                                str(dcp.package_type),
                                                str(dcp.size),
                                                str(dcp.status),
                                                check,
                                                str(dcp.path.absolute())
                    ])) 
    return ui.table(
        name='full_list',
        columns=columns,
        rows=rows,
        groupable=True,
        downloadable=True,
        resettable=True,
        height="100vh"
    )


def make_movie_dcps_table(dcps):
    columns = [
        ui.table_column(name='actions', label='', align='center', max_width="10px",
                        cell_type=ui.menu_table_cell_type(name='commands', commands=commands)),
        ui.table_column(name='Title', label='Title', searchable=True, filterable=True, min_width="500px", link=True),
        ui.table_column(name='Location', label='Location', searchable=True, filterable=True,  min_width="100px" ),
        ui.table_column(name='Type', label='Type', searchable=True, filterable=True),
    ]

    import pprint
    pprint.pprint(dcps)

    return ui.table(
        name='movie_list',
        columns=columns,
        rows=[ 
                ui.table_row(name='#dcp/' + str(dcp.uid), cells=['', dcp.full_title, str(dcp.location.path), dcp.package_type]) for dcp in dcps
            ],
        groupable=True,
        downloadable=True,
        resettable=True,
        height="100vh"
    )

from h2o_wave import ui, on, Q
import random

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

status = [
    "Bloqué",
    "La merde!",
    "Blague",
]

# cell_type=ui.icon_table_cell_type()

def make_flat_dcps_table(dcps):
    columns = [
        ui.table_column(name='Movie', label='Movie', searchable=True, filterable=True, min_width="250px", link=False),
        ui.table_column(name='Title', label='Title', searchable=True, filterable=True, min_width="500px"),
        ui.table_column(name='Location', label='Location', filterable=True,  max_width="80px" ),
        ui.table_column(name='Type', label='Type', filterable=True, max_width="70px"),
        ui.table_column(name='Size', label='Size', max_width="80px"),
        ui.table_column(name='Status', label='Status', filterable=True, cell_type=ui.tag_table_cell_type(name='tags', tags=[
                ui.tag(label=status[0], color='#D2E3F8'),
                ui.tag(label=status[1], color='$red'),
                ui.tag(label=status[2], color='$mint'),
            ]
        )),
        ui.table_column(name='Kind', label='Kind', filterable=True),
        ui.table_column(name='Check', label='Check', filterable=True, cell_type=ui.tag_table_cell_type(name='tags', tags=[
                ui.tag(label="?", color='$white'),
                ui.tag(label="fail", color='$red'),
                ui.tag(label="ok", color='$mint'),
            ]
        )),
        ui.table_column(name='Date', label='date', filterable=True),
        ui.table_column(name='Path', label='Path'),
    ]

    rows = []
    for dcp in dcps:
        check = "?"
        if dcp.report.get("valid") == True:
            check = "ok" 
        elif dcp.report.get("valid") == False:
            check = "fail"
        rows.append(ui.table_row(name='#dcp/' + str(dcp.uid)  , cells=[dcp.title, dcp.full_title,
                                                str(dcp.location.name),
                                                str(dcp.package_type),
                                                str(dcp.size),
                                                random.choice(status),
                                                str(dcp.kind),
                                                check,
                                                str(dcp.namings.get("Date", {}).get("Value")),
                                                str(dcp.path.absolute())
                    ])) 
    return ui.table(
        name='full_list',
        columns=columns,
        rows=rows,
        groupable=True,
        downloadable=True,
        resettable=True,
        height="calc(100vh - 150px)"
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
from h2o_wave import Q, ui, on
from movx import core
from movx.gui import setup_page
from movx.core.db import DCP, Tags
from movx.gui.cards.dcp import add_infos_cards

@on()
async def dcp_tags_picker(q):
    if q.client.current_dcp:
        with q.client.current_dcp.fresh() as dcp:
            names = [ t.name for t in dcp.tags]
            new_tags = [ t for t in q.args.dcp_tags_picker if t not in names ]
            tags = [ Tags.filter(Tags.name == tag).first() for tag in new_tags ]
            print(tags)
            for t in tags:
                dcp.tags.append(t)

@on()
async def dcp_parse_action(q):
    core.dcps.parse( DCP.get( q.args.dcp_parse_action ) )
    await show_dcp(q, q.args.dcp_parse_action )

@on()
async def dcp_probe_action(q):
    core.dcps.probe( DCP.get( q.args.dcp_probe_action ) )
    await show_dcp(q, q.args.dcp_probe_action )

@on()
async def dcp_check_action(q):
    core.dcps.check( DCP.get( q.args.dcp_check_action ) )
    await show_dcp( q, q.args.dcp_check_action )


@on("#dcp/{id}")
async def show_dcp(q: Q, id):

    dcp = DCP.get(id)
    

    if dcp:
        setup_page(q, "DCP " + dcp.title)

        q.client.current_dcp = dcp

        add_infos_cards(q, dcp)

        q.client.parse_report_id = q.args.parse_report_id or 0

        q.client.check_report_id = q.args.check_report_id or 0

        #add_parse_cards(q, dcp, q.client.parse_report_id)

        #add_check_cards(q, dcp, q.client.check_report_id)

        '''
        if dcp.jobs("parse"):
            q.client.last_report = dcp.jobs("parse")[0]
        
        if dcp.jobs("check"):
            q.client.last_check = dcp.jobs("check")

        
        q.page["dcp_infos"] = dcp_infos_card(q, dcp)

        if last_check:
            q.page["dcp_check"] = check_card(last_check.result)

        for name, items in cpl_card(last_report.result).items():
            q.page[name] = ui.form_card(box=ui.box("content", size=0), items=items)

        for name, items in pkl_card(last_report.result).items():
            q.page[name] = ui.form_card(box=ui.box("content", size=0), items=items)

        for name, items in assetmap_infos(last_report.result).items():
            q.page[name] = ui.form_card(box=ui.box("content", size=0), items=items)
        '''

    await q.page.save()


from h2o_wave import ui

layouts = {
     "full": [
        ui.layout(
            breakpoint='xl',
            width='100%',
            height='100%',
            zones=[
                ui.zone('header'),
                ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('content', size='100%'),
                ]),
                ui.zone('footer'),
            ]
        ),
    ],
    "2cols": [
        ui.layout(
            breakpoint='xl',
            width='100%',
            height='100%',
            zones=[
                ui.zone('header'),
                ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('content', size='50%'),
                    ui.zone('sidebar', size='50%'),
                ]),
                ui.zone('footer'),
            ]
        ),
    ],
    "side": [
        ui.layout(
            breakpoint='xl',
            width='100%',
            height='100%',
            zones=[
                ui.zone('header'),
                ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('content', size='80%'),
                    ui.zone('sidebar', size='20%'),
                ]),
                ui.zone('footer'),
            ]
        ),
    ]
}
     

def setup_page(q, title=None, layout="full"):
    q.page.drop()
    
    q.page['meta'] = ui.meta_card(box='', 
        title=title, 
        theme="default", 
        layouts=layouts[layout]
    )
    
def breadcrumbs(q, breads=[]):

    breads = [ ("#", "Digital Cinema Packages") ] + breads

    q.page['breadcrumbs'] = ui.breadcrumbs_card(box='header', 
                            items=[ ui.breadcrumb(name=b[0], label=b[1]) for b in breads])

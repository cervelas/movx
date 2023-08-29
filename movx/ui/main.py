import logging
from h2o_wave import main, app, Q, ui, on, handle_on, copy_expando

from movx.ui import setup_page, breadcrumbs, crash_report, dcps


# Set up logging
logging.basicConfig(
    format="%(levelname)s:\t[%(asctime)s]\t%(message)s", level=logging.INFO
)


@on("movie_list")
async def on_movie_row_clicked(q: Q):
    q.page["meta"] = ui.meta_card(box="", redirect=q.args.movie_list[0])
    await q.page.save()


@on("all_dcp_list")
async def on_row_clicked(q: Q):
    q.page["meta"] = ui.meta_card(box="", redirect="#dcp/" + q.args.all_dcp_list[0])
    await q.page.save()


@on("#movies")
async def movies_layout(q: Q):
    pass


@on("#movie/{title}")
async def movie_layout(q: Q, title):
    setup_page(q, title)
    breadcrumbs(q, [("current", title)])

    """
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
    """

    await q.page.save()


@app("/")
async def serve(q: Q):
    try:
        # Initialize the app if not already
        if not q.app.initialized:
            await initialize_app(q)

        # Initialize the client if not already
        if not q.client.initialized:
            await initialize_client(q)

        # Update theme if toggled
        elif q.args.theme_dark is not None and q.args.theme_dark != q.client.theme_dark:
            await update_theme(q)

        """# Update table if query is edited
        elif q.args.query is not None and q.args.query != q.client.query:
            await apply_query(q)

        # Update dataset if changed
        elif q.args.dataset is not None and q.args.dataset != q.client.dataset:
            await update_dataset(q)"""
        # Delegate query to query handlers
        if await handle_on(q):
            pass

        # Adding this condition to help in identifying bugs
        else:
            await dcps.overview(q)

    except Exception as error:
        await show_error(q, error=str(error))

    """
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
        q.page['loc%s' % i] = l"""

    """
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
    """

    await q.page.save()


async def initialize_app(q: Q):
    """
    Initialize the app.
    """

    logging.info("Initializing app")

    # Set initial argument values
    # q.app.cards = ['main', 'error']

    q.app.initialized = True


async def initialize_client(q: Q):
    """
    Initialize the client (browser tab).
    """

    logging.info("Initializing client")

    # Set initial argument values
    """q.client.theme_dark = True
    q.client.datasets = ['waveton_sample.csv']
    q.client.dataset = 'waveton_sample.csv'
    q.client.data = q.app.default_data
    q.client.data_query = q.client.data
    q.client.query = ''

    # Add layouts, header and footer
    q.page['meta'] = cards.meta
    q.page['header'] = cards.header
    q.page['footer'] = cards.footer

    # Add cards for the main page
    q.page['main'] = cards.main"""

    q.client.initialized = True


async def update_theme(q: Q):
    """
    Update theme of app.
    """

    # Copying argument values to client
    copy_expando(q.args, q.client)

    if q.client.theme_dark:
        logging.info("Updating theme to dark mode")

        # Update theme from light to dark mode
        q.page["meta"].theme = "h2o-dark"
        q.page["header"].icon_color = "black"
    else:
        logging.info("Updating theme to light mode")

        # Update theme from dark to light mode
        q.page["meta"].theme = "light"
        q.page["header"].icon_color = "#FEC924"

    await q.page.save()


async def show_error(q: Q, error: str):
    """
    Displays errors.
    """

    logging.error(error)

    # Format and display the error
    q.page["error"] = crash_report(q)

    await q.page.save()


async def handle_fallback(q: Q):
    """
    Handle fallback cases.
    """

    logging.info("Adding fallback page")

    # q.page['fallback'] = cards.fallback

    await q.page.save()

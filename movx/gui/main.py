import logging

from h2o_wave import main, app, Q, ui, on, run_on, copy_expando, handle_on

from movx.gui import (
    notif,
    setup_page,
    dcps,
    dcp,
    jobs,
    job,
    movies,
    movie,
    settings,
    location,
    locations,
    meta,
    nav,
    autoroute,
)

from movx.gui.cards import crash_report


@app("/")
async def serve(q: Q):
    try:
        init_app(q)

        await init_client(q)

        if len(q.client.__loc_hash) == 0:
            #await dcps.overview_items(q)
            # await show_error(q, error="homepage")
            await dcps.dcps_list(q, md=True)

        elif not await autoroute(q, False):
            # setup_page(q, "Error")
            # await show_error(q, "Autoroute Fail")
            await dcps.dcps_list(q, md=True)

        await q.page.save()

    except Exception as error:
        notif(q, str(error), "error")
        await show_error(q, error=str(error))


def init_app(q: Q):
    """
    Initialize the app.
    """

    if not q.app.initialized:
        # Set initial argument values
        # q.app.cards = ['main', 'error']
        q.app.initialized = True


async def init_client(q: Q):
    """
    Initialize the client (browser tab).
    """

    q.client.__loc_hash = "#" + q.args["#"] if q.args["#"] else ""

    if not q.client.initialized:
        # logging.info("Initializing client")

        # Set initial argument values
        q.client.user = None
        q.client.current_dcp = None
        q.client.settings = None

        """
        q.page['footer'] = cards.footer

        # Add cards for the main page
        q.page['main'] = cards.main
        """

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

@on()
async def ask_for_login(q: Q):
    pass

async def show_error(q: Q, error: str):
    """
    Displays errors.
    """
    import traceback

    logging.error(error)
    logging.error(traceback.format_exc())

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


@on()
async def goto_movie(q: Q):
    q.page["meta"].redirect = "#mov/%s" % q.args.goto_movie
    await q.page.save()


@on()
async def goto_location(q: Q):
    q.page["meta"].redirect = "#loc/%s" % q.args.goto_location
    await q.page.save()

import uvicorn
import webview

from movx import start_waved, UvicornServer, ENTRY_POINT, LOCAL_URL, UvicornServer, start_waved

if __name__ == "__main__":
    start_waved()
    print("Starting application in app mode")

    config = uvicorn.Config(
        "movx.ui.main:main", port=8000, log_level="warning", reload=True
    )
    instance = UvicornServer(config=config)
    instance.start()

    window = webview.create_window("MOVX", "http://127.0.0.1:10101/")
    webview.start(debug=True)


def start_app(debug=False, reload=False):
    print("Starting Movx Application")
    start_waved()

    config = uvicorn.Config(ENTRY_POINT, port=8000, log_level="warning", reload=reload)
    instance = UvicornServer(config=config)
    instance.start()

    webview.create_window("MOVX", LOCAL_URL)
    webview.start(debug=debug)

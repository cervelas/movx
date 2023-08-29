import uvicorn
import webview

from movx import start_waved
from movx import UvicornServer

if __name__ == "__main__":
    start_waved()
    print("Starting application in app mode")

    config = uvicorn.Config("movx.ui.main:main", port=8000, log_level="warning", reload=True)
    instance = UvicornServer(config=config)
    instance.start()

    window = webview.create_window('MOVX', "http://127.0.0.1:10101/")
    webview.start(debug=True)
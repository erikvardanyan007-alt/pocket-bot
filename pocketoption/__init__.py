import time
import json
import logging
from websocket import WebSocketApp

logger = logging.getLogger(__name__)

class PocketOption:
    def __init__(self, ssid: str):
        self.ssid = ssid
        self.ws = None
        self.is_connected = False

    def connect(self):
        url = "wss://api2.pocketoption.com/socket.io/?EIO=4&transport=websocket"
        self.ws = WebSocketApp(
            url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        import threading
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def _on_open(self, ws):
        self.is_connected = True
        logger.info("WebSocket connected. Authenticating...")
        auth_msg = f'42["auth", {{"session": "{self.ssid}", "isDemo": 1}}]'
        ws.send(auth_msg)

    def _on_message(self, ws, message):
        if message == "2":
            ws.send("3")

    def _on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        self.is_connected = False
        logger.info("WebSocket connection closed")

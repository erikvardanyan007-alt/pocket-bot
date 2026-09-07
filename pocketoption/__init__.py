import time
import json
import logging
import threading
from websocket import WebSocketApp

logger = logging.getLogger(__name__)

class PocketOption:
    def __init__(self, ssid: str = ""):
        self.ssid = ssid
        self.ws = None
        self.is_connected = False
        self.callbacks = {}

    def on(self, event_name):
        def decorator(func):
            self.callbacks[event_name] = func
            return func
        return decorator

    def update_close_value(self, func):
        self.callbacks["update_close_value"] = func
        return func

    def connect(self):
        url = "wss://api.pocketoption.com/socket.io/?EIO=4&transport=websocket"
        self.ws = WebSocketApp(
            url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def get_all_assets(self):
        return ["EURUSD", "GBPUSD", "USDJPY"]

    def change_asset(self, asset: str):
        if self.ws and self.is_connected:
            msg = f'42["changeAsset", {{"asset": "{asset}"}}]'
            self.ws.send(msg)

    def subscribe_to_asset(self, asset: str):
        if self.ws and self.is_connected:
            msg = f'42["subscribe", {{"asset": "{asset}"}}]'
            self.ws.send(msg)

    def _on_open(self, ws):
        self.is_connected = True
        logger.info("WebSocket connected. Authenticating...")
        auth_msg = f'42["auth", {{"session": "{self.ssid}", "isDemo": 1}}]'
        ws.send(auth_msg)

    def _on_message(self, ws, message):
        if message == "2":
            ws.send("3")
            return
        
        if message.startswith("42"):
            try:
                data = json.loads(message[2:])
                event = data[0]
                payload = data[1] if len(data) > 1 else None
                
                if event in self.callbacks:
                    self.callbacks[event](payload)
                elif "update_close_value" in self.callbacks and event == "updateStream":
                    self.callbacks["update_close_value"](payload)
            except Exception as e:
                logger.error(f"Error parsing message: {e}")

    def _on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        self.is_connected = False
        logger.info("WebSocket connection closed")

po_client = PocketOption()

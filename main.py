import asyncio
import os
import threading
import requests
from flask import Flask
from pocketoption import PocketOption

app = Flask(__name__)

@app.route('/')
def home():
    return "Pocket Option Bridge is Running!"

APP_SERVER_URL = "https://remix-remix-trading-signals-telegram-mini-app-950378129316.europe-west2.run.app/api/quotes/feed"
PO_SSID = '42["auth",{"session":"6h7fgmvcd6rcm1db9ebknaubag","platform":4,"isFastHistory":true,"isOptimized":true}]'

async def run_bridge():
    print("[INFO] Starting PocketOption client...")
    po_client = PocketOption(ssid=PO_SSID)

    @po_client.update_close_value
    def on_price(data):
        asset = data.get("asset")
        price = data.get("close")
        timestamp = data.get("time")

        if asset and price:
            try:
                requests.post(
                    APP_SERVER_URL,
                    json={
                        "asset": asset,
                        "price": price,
                        "timestamp": timestamp
                    },
                    timeout=0.3
                )
                print(f"[SENT] {asset}: {price}")
            except Exception as e:
                print(f"[ERROR] Request failed: {e}")

    try:
        po_client.connect()
        print("[INFO] Connect method called.")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

    await asyncio.sleep(3)

    try:
        all_assets = po_client.get_all_assets()
        print(f"[INFO] Subscribing to assets: {all_assets}")
        for asset in all_assets:
            try:
                po_client.change_asset(asset)
                po_client.subscribe_to_asset(asset)
            except Exception as e:
                print(f"[ERROR] Asset {asset} subscription error: {e}")
    except Exception as e:
        print(f"[ERROR] Assets error: {e}")

    while True:
        await asyncio.sleep(1)

def start_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bridge())

if __name__ == "__main__":
    threading.Thread(target=start_async_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

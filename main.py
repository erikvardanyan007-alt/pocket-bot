import asyncio
import threading
import os
import requests
from flask import Flask
from pocketoption import PocketOption

# Flask-сервер для предотвращения ошибок деплоя на Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Pocket Option Bridge is Running!"

# Настройки подключения
APP_SERVER_URL = "https://remix-remix-trading-signals-telegram-mini-app-950378129316.europe-west2.run.app/api/quotes/feed"
PO_SSID = '42["auth",{"session":"1.1788734313.1788734570.G-E6RB4FHY15.k4AbRpEE_l7wxkidhaWWwA","isDemo":1,"uid":128693934,"platform":1}]'

async def run_bridge():
    po_client = PocketOption(ssid=PO_SSID)

    @po_client.on.update_close_value
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
                print(f"[ОТПРАВЛЕНО] {asset}: {price}")
            except Exception:
                pass

    await po_client.connect()

    all_assets = await po_client.get_all_assets()

    for asset in all_assets:
        try:
            await po_client.emit.change_asset(asset)
            await po_client.emit.subscribe_to_asset(asset)
        except Exception:
            continue

    while True:
        await asyncio.sleep(1)

def start_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bridge())

if __name__ == "__main__":
    # Запуск логики WebSocket в отдельном потоке
    threading.Thread(target=start_async_loop, daemon=True).start()
    
    # Запуск веб-сервера на порту Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

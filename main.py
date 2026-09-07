import os
from flask import Flask
from pocketoption.client import PocketOption

app = Flask(__name__)

@app.route('/')
def home():
    return "Pocket Option Bridge is Running!"

APP_SERVER_URL = "https://remix-remix-trading-signals-telegram-mini-app-950378129316.europe-west2.run.app"
PO_SSID = '42["auth",{"session":"a:4:{s:10:\\"session_id\\";s:32:\\"39eda7c1e645489b5460d3df42d50834\\";s:10:\\"ip_address\\";s:11:\\"80.86.229.5\\";s:10:\\"user_agent\\";s:111:\\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36\\";s:13:\\"last_activity\\";i:1788742474;}583b62b3410425257d3c1eba1019fabe","isDemo":0,"uid":128693934,"platform":2,"isFastHistory":True,"isOptimized":True}]'

async def run_bridge():
    print("[INFO] Starting PocketOption client...")
    po_client = PocketOption(ssid=PO_SSID)

    @po_client.update_close_value
    def on_price(data):
        asset = data.get("asset")
        price = data.get("close")
        timestamp = data.get("time")
        
        # Вывод в логи Render для проверки тиков
        print(f"[TICK] Asset: {asset} | Price: {price} | Time: {timestamp}")

    await po_client.connect()

if __name__ == '__main__':
    import threading
    import asyncio

    # Запуск WebSocket-клиента в отдельном потоке
    def start_background_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_bridge())

    new_loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_background_loop, args=(new_loop,), daemon=True)
    t.start()

    # Запуск Flask-сервера для Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

import asyncio
import requests
from pocketoption import PocketOption

APP_SERVER_URL = https://remix-remix-trading-signals-telegram-mini-app-950378129316.europe-west2.run.app/api/quotes/feed"
PO_SSID = 42["chat_room_list_update",{"message":{"room_id":14906,"user_id":115981790,"date":1788732671,"message_id":639053084,"message":" Hola necesito ayuda para retirar mi dinero por que...","message_hidden":0,"message_secret":false,"message_content":null}}]

async def main():
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

if __name__ == "__main__":
    asyncio.run(main())

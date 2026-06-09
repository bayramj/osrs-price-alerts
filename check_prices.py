import json
import os
import urllib.request

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

TARGETS = {
    "Raw dark crab": 1100,
    "Amethyst arrowtips": 250,
}

HEADERS = {
    "User-Agent": "Julian OSRS price alert - contact via GitHub"
}

def get_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

mapping = get_json("https://prices.runescape.wiki/api/v1/osrs/mapping")
latest = get_json("https://prices.runescape.wiki/api/v1/osrs/latest")["data"]

name_to_id = {item["name"].lower(): item["id"] for item in mapping}

alerts = []

for item_name, target_price in TARGETS.items():
    item_id = str(name_to_id[item_name.lower()])
    price_data = latest[item_id]

    high = price_data.get("high")
    low = price_data.get("low")
    current_price = low or high

    if current_price and current_price >= target_price:
        alerts.append(f"🚨 **{item_name}** is {current_price:,} gp — target is {target_price:,} gp")

if alerts:
    message = "\n".join(alerts)
    payload = json.dumps({"content": message}).encode("utf-8")

    req = urllib.request.Request(
        DISCORD_WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    urllib.request.urlopen(req)
else:
    print("No alerts triggered.")

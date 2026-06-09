import json
import os
import urllib.request
from pathlib import Path

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
STATE_FILE = Path("alert_state.json")

TARGETS = {
    "Raw dark crab": 1100,
    "Amethyst arrowtips": 240,
}

HEADERS = {
    "User-Agent": "Julian OSRS price alert - contact via GitHub"
}


def get_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())


def send_discord(message):
    payload = json.dumps({"content": message}).encode("utf-8")

    req = urllib.request.Request(
        DISCORD_WEBHOOK_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "osrs-price-alert-bot/1.0",
        },
        method="POST",
    )

    urllib.request.urlopen(req)


state = {}
if STATE_FILE.exists():
    state = json.loads(STATE_FILE.read_text())

mapping = get_json("https://prices.runescape.wiki/api/v1/osrs/mapping")
latest = get_json("https://prices.runescape.wiki/api/v1/osrs/latest")["data"]

name_to_id = {item["name"].lower(): item["id"] for item in mapping}

alerts = []

for item_name, target_price in TARGETS.items():
    item_id = str(name_to_id[item_name.lower()])
    price_data = latest[item_id]

    sell_price = price_data.get("low") or price_data.get("high")
    was_above = state.get(item_name, False)
    is_above = sell_price is not None and sell_price >= target_price

    print(f"{item_name}: sell price {sell_price}, target {target_price}")

    if is_above and not was_above:
        alerts.append(
            f"🚨 **{item_name}** sell price is **{sell_price:,} gp** — target is **{target_price:,} gp**"
        )

    state[item_name] = is_above

STATE_FILE.write_text(json.dumps(state, indent=2))

if alerts:
    send_discord("\n".join(alerts))
else:
    print("No new alerts triggered.")

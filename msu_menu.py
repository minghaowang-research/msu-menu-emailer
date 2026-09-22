#!/usr/bin/env python3
"""
MSU Dining Hall Daily Menu Emailer.
Fetches menus from msu.nutrislice.com API and emails a daily digest.
"""

import requests
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os
import sys
import logging

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
EMAILS_PATH = os.path.join(SCRIPT_DIR, "emails.txt")
LOG_PATH = os.path.join(SCRIPT_DIR, "msu_menu.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
)
log = logging.getLogger(__name__)

HALLS = {
    "Brody Square": {"slug": "brody-square", "id": 71013},
    "The Edge at Akers": {"slug": "the-edge-at-akers", "id": 71018},
    "The Gallery at Snyder Phillips": {"slug": "the-gallery-at-synderphillips", "id": 71781},
    "South Pointe at Case": {"slug": "south-pointe-at-case", "id": 71015},
    "The State Room at Kellogg": {"slug": "the-state-room-at-kellogg", "id": 71022},
}

MEAL_TYPES = {"Breakfast": 40254, "Lunch": 40255, "Dinner": 42074}

API_BASE = "https://msu.api.nutrislice.com"

HIGHLIGHT_KEYWORDS = [
    "beef", "steak", "sirloin", "ribeye", "filet", "strip steak", "flank",
    "tenderloin", "prime rib", "short rib", "spare rib", "brisket", "tri-tip", "pot roast", "lamb",
    "salmon", "fish", "tilapia", "cod", "shrimp", "seafood", "tuna", "mahi",
    "swordfish", "trout", "catfish", "walleye", "crab", "lobster",
    "scallop", "calamari", "pollock", "halibut", "perch", "crawfish",
    "snapper", "grouper", "bass", "haddock", "flounder", "sole", "anchovy",
    "sardine", "mackerel", "whitefish",
]

CEREAL_KEYWORDS = [
    "apple jacks", "cheerios", "rice chex", "cinnamon toast crunch",
    "cocoa pebbles", "cocoa puffs", "frosted flakes", "fruit pebbles",
    "froot loops", "golden grahams", "kashi go lean", "life cereal",
    "lucky charms", "nature valley", "raisin bran", "reeses puffs",
    "special k with red berries",
]

SKIP_CATEGORIES = {"other", "beverage", "grain"}

# Stations left out of the full menu. Comment out a line to show that station again.
HIDDEN_STATIONS = {
    "SALAD BAR": "cold/pre-made, same every day",
    "DELI": "cold sandwich fillings, same every day",
    "NOOK": "yogurt, granola, cookies, ice cream, same every day",
    "DOLCE": "Brody desserts and ice cream",
    "ALLERGEN CONSCIOUS": "packaged gluten-free/vegan muffins, cookies, soy yogurt",
}

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "MSU-Menu-Emailer/1.0"})

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def load_emails():
    if os.path.exists(EMAILS_PATH):
        with open(EMAILS_PATH) as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []


def load_config():
    file_emails = load_emails()
    if os.environ.get("SENDER_EMAIL"):
        secret_raw = os.environ.get("RECIPIENT_EMAILS", "")
        secret_emails = [e.strip() for e in secret_raw.split(",") if e.strip()]
        all_emails = list(dict.fromkeys(file_emails + secret_emails))
        return {
            "sender_email": os.environ["SENDER_EMAIL"],
            "recipient_emails": all_emails,
            "app_password": os.environ["APP_PASSWORD"],
        }
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    all_emails = list(dict.fromkeys(file_emails + config.get("recipient_emails", [])))
    config["recipient_emails"] = all_emails
    return config


def _is_cereal(name):
    low = name.lower()
    if any(kw in low for kw in CEREAL_KEYWORDS):
        return True
    return low in ("captain crunch", "captain crunch berries")


def _parse_day_menu(day_data):
    """Parse one day's menu_items into {physical_station: [item_names]} using menu_info."""
    menu_info = day_data.get("menu_info") or {}
    menu_id_to_station = {}
    station_positions = {}
    for mid, info in menu_info.items():
        name = info.get("section_options", {}).get("display_name", "")
        if name:
            menu_id_to_station[int(mid)] = name
            station_positions[name] = info.get("position", 999)

    stations = {}
    seen = set()
    for item in day_data.get("menu_items", []):
        if item.get("is_station_header") or item.get("is_section_title"):
            continue
        food = item.get("food")
        if not food or not food.get("name"):
            continue
        name = food["name"]
        cat = item.get("category", "other")
        if name in seen or _is_cereal(name) or cat in SKIP_CATEGORIES:
            continue
        mid = item.get("menu_id")
        station = menu_id_to_station.get(mid, "Other")
        stations.setdefault(station, []).append(name)
        seen.add(name)

    sorted_stations = dict(sorted(stations.items(), key=lambda x: station_positions.get(x[0], 999)))
    return sorted_stations


def fetch_menu(hall_id, date):
    date_str = date.strftime("%Y-%m-%d")
    meals = {}
    for meal_name, meal_id in MEAL_TYPES.items():
        url = (f"{API_BASE}/menu/api/weeks/school/{hall_id}"
               f"/menu-type/{meal_id}/{date.year}/{date.month:02d}/{date.day:02d}")
        try:
            resp = SESSION.get(url, timeout=30)
            if resp.status_code != 200:
                continue
            data = resp.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            log.warning("  Failed to fetch %s (meal %s): %s", hall_id, meal_name, e)
            continue

        for day in data.get("days", []):
            if day["date"] == date_str:
                stations = _parse_day_menu(day)
                if stations:
                    meals[meal_name] = stations
                break

    if not meals:
        return {"closed": True}
    return {"meals": meals}


def is_highlight(item_name, station_name):
    name_lower = item_name.lower()
    if "burger" in name_lower:
        return False
    if "taco" in name_lower:
        return False
    if "gravy" in name_lower:
        return False
    if "battered pollock" in name_lower:
        return False
    if "salad" in name_lower:
        return False
    if station_name in ("S2", "SALAD BAR"):
        return False
    if station_name == "STACKS" and "roast beef" in name_lower:
        return False
    return any(kw in name_lower for kw in HIGHLIGHT_KEYWORDS)


def build_html(today, today_data):
    day_name = DAY_NAMES[today.weekday()]

    hl_by_hall = {}
    for hall_name in sorted(today_data.keys()):
        data = today_data[hall_name]
        for meal, stations in data.get("meals", {}).items():
            for station, items in stations.items():
                for item_name in items:
                    if is_highlight(item_name, station):
                        key = (hall_name, station, item_name)
                        hl_by_hall.setdefault(key, []).append(meal)
    hall_stations = {}
    for (hall, station, name), meals in hl_by_hall.items():
        hall_stations.setdefault(hall, {}).setdefault(station, []).append(
            f"{name} ({', '.join(meals)})")

    parts = [f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body {{ font-family: -apple-system, Helvetica, Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; color: #333; }}
h1 {{ color: #18453B; border-bottom: 3px solid #18453B; padding-bottom: 8px; font-size: 1.4em; }}
.hall {{ margin-bottom: 18px; }}
.hall-name {{ color: #fff; background: #18453B; padding: 6px 10px; font-weight: bold; font-size: 1.05em; border-radius: 4px 4px 0 0; }}
.hall-body {{ background: #f9f9f9; border: 1px solid #ddd; border-top: none; border-radius: 0 0 4px 4px; padding: 4px 10px; }}
.meal-row td {{ vertical-align: top; padding: 6px 0; border-bottom: 1px solid #e5e5e5; font-size: 0.88em; color: #555; line-height: 1.45; }}
.meal-row:last-child td {{ border-bottom: none; }}
.meal-label {{ font-weight: bold; color: #18453B; width: 80px; padding-right: 8px !important; }}
.station {{ font-weight: bold; color: #444; font-size: 0.85em; }}
.station-line {{ margin: 0 0 4px 0; }}
.sep {{ color: #ccc; padding: 0 3px; }}
.item-hl {{ font-weight: bold; color: #b71c1c; }}
.closed {{ color: #999; font-style: italic; }}
.hl-box {{ background: #fff3e0; border: 2px solid #e65100; border-radius: 8px; padding: 12px; margin-bottom: 18px; }}
.hl-box h2 {{ color: #e65100; margin: 0 0 6px 0; font-size: 1.05em; border: none; }}
.hl-item {{ margin: 3px 0; font-size: 0.93em; }}
.closed-halls {{ background: #f5f5f5; border: 1px solid #ddd; border-radius: 8px; padding: 12px 16px; margin-bottom: 18px; }}
.closed-halls h2 {{ color: #999; margin: 0 0 8px 0; font-size: 1.05em; border: none; }}
.closed-hall-entry {{ margin: 4px 0; font-size: 0.93em; color: #666; }}
.closed-hall-name {{ font-weight: bold; color: #555; }}
.notes {{ font-size: 0.82em; color: #888; margin-top: 24px; border-top: 1px solid #ddd; padding-top: 10px; }}
.notes div {{ margin: 4px 0; }}
.note {{ color: #888; font-size: 0.8em; margin-top: 24px; }}
</style></head><body>
<h1>[MSU Menu] {day_name}, {today.strftime('%B %d')}</h1>
"""]

    if hall_stations:
        parts.append('<div class="hl-box">')
        parts.append('<h2>Beef / Lamb / Fish / Shellfish Today</h2>')
        for hall in hall_stations:
            parts.append(f'<div style="font-weight:bold;margin-top:6px;font-size:0.93em;">{hall}</div>')
            for station, items in hall_stations[hall].items():
                parts.append(f'<div class="hl-item">{station}: {", ".join(items)}</div>')
        parts.append('</div>')

    unavailable_halls = [h for h in HALLS if h not in today_data or "meals" not in today_data.get(h, {})]
    if unavailable_halls:
        parts.append('<div class="closed-halls">')
        parts.append(f'<h2>Closed / No Menu ({len(unavailable_halls)})</h2>')
        for h in unavailable_halls:
            parts.append(f'<div class="closed-hall-entry"><span class="closed-hall-name">{h}</span>'
                         ' <span style="color:#888;font-size:0.85em;">-- No menu available today</span></div>')
        parts.append('</div>')

    halls_with_menus = sorted(h for h in HALLS if h in today_data and "meals" in today_data.get(h, {}))
    if not halls_with_menus:
        parts.append('<p class="closed">No menu data available for any dining hall today.</p>')
    for hall_name in halls_with_menus:
        meals = today_data[hall_name]["meals"]
        parts.append('<div class="hall">')
        parts.append(f'<div class="hall-name">{hall_name}</div>')
        parts.append('<div class="hall-body"><table width="100%" cellpadding="0" cellspacing="0">')
        for meal_time in MEAL_TYPES:
            stations = meals.get(meal_time)
            if not stations:
                continue
            chunks = []
            for station, items in stations.items():
                if station in HIDDEN_STATIONS:
                    continue
                foods = ' <span class="sep">|</span> '.join(
                    f'<span class="item-hl">{i}</span>' if is_highlight(i, station) else i
                    for i in items)
                chunks.append(f'<div class="station-line"><span class="station">{station}:</span> {foods}</div>')
            if not chunks:
                continue
            row = "".join(chunks)
            parts.append(f'<tr class="meal-row"><td class="meal-label">{meal_time}</td>'
                         f'<td>{row}</td></tr>')
        parts.append('</table></div></div>')

    hidden = ", ".join(f"{st.title()} ({why})" for st, why in HIDDEN_STATIONS.items())
    parts.append('<div class="notes"><b>Notes</b>'
                 '<div>- Not highlighted: Burger (everyday), Taco (everyday), Gravy (side dish), Salad (not a meat), '
                 'S2 sushi station (always has fish/shellfish), Salad bar (cold/pre-made), '
                 'Stacks roast beef (deli meat everyday), Battered Pollock (everyday)</div>'
                 f'<div>- Hidden stations: {hidden}. To show one again, remove it from HIDDEN_STATIONS in the script.</div></div>')
    parts.append('<p class="note">Auto-generated from msu.nutrislice.com</p></body></html>')
    return "\n".join(parts)


def send_email(html, config, today):
    recipients = config.get("recipient_emails", [])
    day_name = DAY_NAMES[today.weekday()]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[MSU Menu] {day_name}, {today.strftime('%B %-d')}"
    msg["From"] = config["sender_email"]
    msg["To"] = config["sender_email"]
    msg["Bcc"] = ", ".join(recipients)
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(config["sender_email"], config["app_password"])
        server.sendmail(config["sender_email"], recipients, msg.as_string())


def main():
    log.info("=== MSU Menu Emailer starting ===")
    config = load_config()
    today = datetime.now()

    log.info("Date: %s", today.strftime("%Y-%m-%d"))
    today_data = {}
    for hall_name, info in HALLS.items():
        log.info("  Fetching %s", hall_name)
        today_data[hall_name] = fetch_menu(info["id"], today)

    log.info("Building email...")
    html = build_html(today, today_data)

    out_path = os.path.join(SCRIPT_DIR, "latest_menu.html")
    with open(out_path, "w") as f:
        f.write(html)
    log.info("Saved local copy: %s", out_path)

    log.info("Sending email...")
    try:
        send_email(html, config, today)
        log.info("Email sent to %s", ", ".join(config.get("recipient_emails", [])))
    except Exception as e:
        log.error("Failed to send email: %s", e)
        sys.exit(1)

    log.info("Done.")


if __name__ == "__main__":
    main()

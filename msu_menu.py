#!/usr/bin/env python3
"""
MSU Dining Hall Daily Menu Emailer.
Scrapes eatatstate.msu.edu, checks which halls are open, and emails today's menu.
"""

import requests
from bs4 import BeautifulSoup
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
    "Brody Square": "Brody%20Square",
    "The Edge at Akers": "The%20Edge%20at%20Akers",
    "The Gallery at Snyder Phillips": "The%20Gallery%20at%20Snyder%20Phillips",
    "The State Room at Kellogg": "The%20State%20Room%20at%20Kellogg",
    # "Heritage Commons at Landon": "Heritage%20Commons%20at%20Landon",
    "South Pointe at Case": "South%20Pointe%20at%20Case",
    # "The Vista at Shaw": "The%20Vista%20at%20Shaw",
    # "Thrive at Owen": "Thrive%20at%20Owen",
}

MENU_URL = "https://eatatstate.msu.edu/menu/{hall}/all/{date}"
HOURS_URL = "https://eatatstate.msu.edu/dining-hall-hours"

HIGHLIGHT_KEYWORDS = [
    "beef", "steak", "sirloin", "ribeye", "filet", "strip steak", "flank",
    "tenderloin", "prime rib", "short rib", "spare rib", "brisket", "tri-tip", "pot roast",
    "salmon", "fish", "tilapia", "cod", "shrimp", "seafood", "tuna", "mahi",
    "swordfish", "trout", "catfish", "walleye", "crab", "lobster",
    "scallop", "calamari", "pollock", "halibut", "perch", "crawfish",
    "snapper", "grouper", "bass", "haddock", "flounder", "sole", "anchovy",
    "sardine", "mackerel", "whitefish",
]

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


def check_open_halls():
    try:
        resp = SESSION.get(HOURS_URL, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        log.warning("Could not fetch hours page (%s), will try all halls", e)
        return set(HALLS.keys()), {}

    soup = BeautifulSoup(resp.text, "html.parser")
    open_halls = set()
    hall_info = {}

    for est in soup.find_all("div", class_="eas-establishment"):
        h3 = est.find("h3")
        if not h3:
            continue
        page_name = h3.get_text(strip=True)
        name = None
        for hall in HALLS:
            if page_name.startswith(hall):
                name = hall
                break
        if not name:
            continue

        has_time_slots = bool(est.find("span", class_="office-hours__item-slots"))
        is_open = has_time_slots or bool(est.find("div", class_="office-hours-status--open"))

        date_range = ""
        valid_div = est.find("div", attrs={"data-valid-dates": True})
        if valid_div:
            date_range = valid_div["data-valid-dates"].strip()

        season_title = ""
        title_span = est.find("span", class_="field-content")
        if title_span:
            season_title = title_span.get_text(strip=True)

        hours_parts = []
        for item in est.find_all("div", class_="office-hours__item"):
            label = item.find("span", class_="office-hours__item-label")
            slots = item.find("span", class_="office-hours__item-slots")
            comment = item.find("span", class_="office-hours__item-comments")
            line = ""
            if label:
                line = label.get_text(strip=True)
            if slots:
                line += " " + slots.get_text(strip=True)
            if comment:
                line += " (" + comment.get_text(strip=True) + ")"
            if line:
                hours_parts.append(line.strip())

        info = {
            "status": "open" if is_open else "closed",
            "hours": hours_parts,
            "date_range": date_range,
            "season": season_title,
        }
        hall_info[name] = info

        if is_open:
            open_halls.add(name)
            log.info("  %s: OPEN [%s] %s", name, date_range, "; ".join(hours_parts))
        else:
            log.info("  %s: closed [%s]", name, date_range)

    return open_halls, hall_info


def scrape_menu(hall_url_name, date_str):
    url = MENU_URL.format(hall=hall_url_name, date=date_str)
    try:
        resp = SESSION.get(url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e)}

    soup = BeautifulSoup(resp.text, "html.parser")
    groups = soup.find_all("div", class_="eas-view-group")
    if not groups:
        return {"closed": True}

    stations = {}
    for group in groups:
        title_tag = group.find("h3", class_="venue-title")
        if not title_tag:
            continue
        station_name = title_tag.get_text(strip=True)

        meals = {}
        for eas_list in group.find_all("div", class_="eas-list"):
            meal_tag = eas_list.find("div", class_="meal-time")
            if not meal_tag:
                continue
            meal_time = meal_tag.get_text(strip=True)

            items = []
            for li in eas_list.find_all("li", class_="menu-item"):
                title_div = li.find("div", class_="meal-title")
                if not title_div:
                    continue
                item_name = title_div.get_text(strip=True)

                prefs = []
                pref_div = li.find("div", class_="dining-prefs")
                if pref_div:
                    for span in pref_div.find_all("span"):
                        prefs.append(span.get_text(strip=True))

                items.append({"name": item_name, "prefs": prefs})

            if items:
                meals[meal_time] = items

        if meals:
            stations[station_name] = meals

    if not stations:
        return {"closed": True}
    return {"stations": stations}


def is_highlight(item_name, station_name):
    name_lower = item_name.lower()
    if "burger" in name_lower:
        return False
    if "taco" in name_lower:
        return False
    if station_name == "S2" and ("roll" in name_lower or "smoked" in name_lower):
        return False
    if station_name == "Stacks" and "roast beef" in name_lower:
        return False
    return any(kw in name_lower for kw in HIGHLIGHT_KEYWORDS)


def build_html(today, today_data, open_halls, hall_info=None):
    day_name = DAY_NAMES[today.weekday()]

    highlights = []
    for hall_name in sorted(today_data.keys()):
        data = today_data.get(hall_name, {})
        for station, meals in data.get("stations", {}).items():
            for meal_time, items in meals.items():
                for item in items:
                    if is_highlight(item["name"], station):
                        highlights.append((hall_name, station, meal_time, item["name"]))

    parts = [f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body {{ font-family: -apple-system, Helvetica, Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; color: #333; }}
h1 {{ color: #18453B; border-bottom: 3px solid #18453B; padding-bottom: 8px; font-size: 1.4em; }}
h2 {{ color: #18453B; margin-top: 24px; font-size: 1.2em; border-bottom: 1px solid #ccc; padding-bottom: 4px; }}
.hall-col {{ vertical-align: top; padding: 0 12px 12px 0; }}
.hall-name {{ color: #fff; background: #18453B; padding: 6px 10px; font-weight: bold; font-size: 1.0em; border-radius: 4px 4px 0 0; margin: 0; }}
.hall-body {{ background: #f9f9f9; border: 1px solid #ddd; border-top: none; border-radius: 0 0 4px 4px; padding: 8px 10px; }}
.station-name {{ font-weight: bold; color: #444; font-size: 0.9em; margin: 8px 0 2px 0; }}
.station-name:first-child {{ margin-top: 0; }}
.item {{ margin: 1px 0; font-size: 0.88em; color: #555; }}
.item-hl {{ margin: 1px 0; font-size: 0.88em; font-weight: bold; color: #b71c1c; }}
.prefs {{ color: #2e7d32; font-size: 0.78em; }}
.closed {{ color: #999; font-style: italic; }}
.hl-box {{ background: #fff3e0; border: 2px solid #e65100; border-radius: 8px; padding: 12px; margin-bottom: 18px; }}
.hl-box h2 {{ color: #e65100; margin: 0 0 6px 0; font-size: 1.05em; border: none; }}
.hl-item {{ margin: 3px 0; font-size: 0.93em; }}
.closed-halls {{ background: #f5f5f5; border: 1px solid #ddd; border-radius: 8px; padding: 12px 16px; margin-bottom: 18px; }}
.closed-halls h2 {{ color: #999; margin: 0 0 8px 0; font-size: 1.05em; border: none; }}
.closed-hall-entry {{ margin: 4px 0; font-size: 0.93em; color: #666; }}
.closed-hall-name {{ font-weight: bold; color: #555; }}
.closed-hall-detail {{ color: #888; font-size: 0.85em; }}
.note {{ color: #888; font-size: 0.8em; margin-top: 24px; }}
</style></head><body>
<h1>[MSU Menu] {day_name}, {today.strftime('%B %d')}</h1>
"""]

    if highlights:
        parts.append('<div class="hl-box">')
        parts.append('<h2>Beef / Fish / Shellfish Today (except Burger and Roll)</h2>')
        for hall, station, meal, name in highlights:
            parts.append(f'<div class="hl-item">{meal} at {hall} ({station}): <b>{name}</b></div>')
        parts.append('</div>')

    if not hall_info:
        hall_info = {}
    unavailable_halls = []
    for h in HALLS:
        has_menu = h in today_data and "stations" in today_data[h]
        if not has_menu:
            unavailable_halls.append(h)

    if unavailable_halls:
        parts.append('<div class="closed-halls">')
        parts.append(f'<h2>Closed / No Menu ({len(unavailable_halls)})</h2>')
        for h in unavailable_halls:
            info = hall_info.get(h, {})
            date_range = info.get("date_range", "")
            if date_range:
                detail = f' <span class="closed-hall-detail">-- Closed {date_range}</span>'
            else:
                detail = ' <span class="closed-hall-detail">-- No menu available today</span>'
            parts.append(f'<div class="closed-hall-entry"><span class="closed-hall-name">{h}</span>{detail}</div>')
        parts.append('</div>')

    halls_with_menus = sorted(h for h in HALLS if h in today_data and "stations" in today_data[h])
    if not halls_with_menus:
        parts.append('<p class="closed">No menu data available for any dining hall today.</p>')
    else:
        for meal_time in ["Breakfast", "Lunch", "Dinner"]:
            hall_columns = []
            for hall_name in halls_with_menus:
                data = today_data[hall_name]
                col_parts = []
                for station, meals in data.get("stations", {}).items():
                    items = meals.get(meal_time)
                    if not items:
                        continue
                    col_parts.append(f'<div class="station-name">{station}</div>')
                    for item in items:
                        pref = ""
                        if item["prefs"]:
                            pref = f' <span class="prefs">({", ".join(item["prefs"])})</span>'
                        cls = "item-hl" if is_highlight(item["name"], station) else "item"
                        col_parts.append(f'<div class="{cls}">{item["name"]}{pref}</div>')
                if col_parts:
                    hall_columns.append((hall_name, "\n".join(col_parts)))

            if hall_columns:
                parts.append(f'<h2>{meal_time}</h2>')
                parts.append('<table width="100%" cellpadding="0" cellspacing="0"><tr>')
                col_width = 100 // len(hall_columns)
                for hall_name, content in hall_columns:
                    parts.append(f'<td class="hall-col" width="{col_width}%">')
                    parts.append(f'<div class="hall-name">{hall_name}</div>')
                    parts.append(f'<div class="hall-body">{content}</div>')
                    parts.append('</td>')
                parts.append('</tr></table>')

    parts.append('<p class="note">Auto-generated from eatatstate.msu.edu</p></body></html>')
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
    date_str = today.strftime("%Y-%m-%d")

    log.info("Date: %s", date_str)
    log.info("Checking which halls are open...")
    open_halls, hall_info = check_open_halls()

    today_data = {}
    for hall_name in HALLS:
        if hall_name not in open_halls:
            log.info("  Skipping %s (closed per hours page)", hall_name)
            continue
        log.info("  Scraping %s", hall_name)
        today_data[hall_name] = scrape_menu(HALLS[hall_name], date_str)

    log.info("Building email...")
    html = build_html(today, today_data, open_halls, hall_info)

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

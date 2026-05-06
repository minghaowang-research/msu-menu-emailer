# MSU Menu Emailer - How This Works

Reference for future Claude sessions. Read this before making changes.

## What It Does

A Python script (`msu_menu.py`) that runs daily at 7 AM via macOS launchd. It:
1. Checks which dining halls are open (scrapes the hours page)
2. Scrapes today's menu for each open hall
3. Builds an HTML email grouped by meal (Lunch, then Dinner), with steak/fish items highlighted
4. Sends the email via Gmail SMTP
5. Saves a local copy as `latest_menu.html`

## Architecture

```
eatatstate.msu.edu/dining-hall-hours  -->  check_open_halls()  -->  set of open hall names
eatatstate.msu.edu/menu/{hall}/all/{date}  -->  scrape_menu()  -->  dict of stations/meals/items
                                               build_html()  -->  HTML string
                                               send_email()  -->  Gmail SMTP
```

### URL Pattern

Menu pages follow: `https://eatatstate.msu.edu/menu/{hall_name_url_encoded}/all/{YYYY-MM-DD}`

### HTML Parsing

The site is Drupal. Key CSS selectors:
- Hours page: `div.eas-establishment` > `h3` (hall name), `div.office-hours-status--open` or `--closed`
- Menu page: `div.eas-view-group` > `h3.venue-title` (station name)
- Within each group: `div.eas-list` > `div.meal-time` (Breakfast/Lunch/Dinner)
- Items: `li.menu-item` > `div.meal-title` (item name), `div.dining-prefs` > `span` (vegetarian/vegan)

## How to Change Things

### Add or remove a dining hall

Edit the `HALLS` dict in `msu_menu.py`. Keys are the display name (must match the `h3` text on the hours page exactly). Values are the URL-encoded name used in menu URLs.

```python
HALLS = {
    "Brody Square": "Brody%20Square",
    "The Edge at Akers": "The%20Edge%20at%20Akers",
    "The Gallery at Snyder Phillips": "The%20Gallery%20at%20Snyder%20Phillips",
}
```

To find a new hall's URL name: go to https://eatatstate.msu.edu, click a dining hall, and look at the URL.

### Change highlight keywords (steak, fish, etc.)

Edit the `HIGHLIGHT_KEYWORDS` list in `msu_menu.py`. All matching is lowercase substring matching.

```python
HIGHLIGHT_KEYWORDS = [
    "steak", "sirloin", "ribeye", ...
]
```

### Change the schedule (time of day, frequency)

Edit `com.msu.menu-emailer.plist` and reload:

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>7</integer>     <!-- 0-23, change this for different time -->
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

To run only on weekdays, add: `<key>Weekday</key><integer>1</integer>` through 5 (Mon-Fri). To run only on Mondays: `<integer>1</integer>`.

After editing, reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.msu.menu-emailer.plist
cp com.msu.menu-emailer.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.msu.menu-emailer.plist
```

### Change or add recipient emails

Edit the `recipient_emails` list in `config.json`:
```json
{
    "sender_email": "minghaowang.chinese@gmail.com",
    "recipient_emails": [
        "minghaowang.chinese@gmail.com",
        "friend@example.com"
    ],
    "app_password": "xxxx xxxx xxxx xxxx"
}
```

Add or remove emails from the list. Sender must match the Gmail account that owns the app password.

### Change email subject prefix (for Gmail filtering)

Search for `[MSU Menu]` in the `send_email()` function in `msu_menu.py`. The current Gmail filter rule is `subject:[MSU Menu]`.

### Change email layout (meal order, what's shown)

The `build_html()` function controls all layout. Current structure:
1. Title with date
2. Highlights box (steak/fish) - only shown if matches exist
3. Closed halls note
4. Meals in order: Breakfast, Lunch, Dinner (controlled by the list `["Breakfast", "Lunch", "Dinner"]`)
5. Under each meal: halls sorted alphabetically, then stations with items

### Switch back to weekly digest

The archived weekly version is documented in `_CHANGELOG.md` (2026-05-05 entries). To go back: change `main()` to loop over 7 dates instead of just today, and update `build_html()` to accept a week of data. Also change the plist `Weekday` back to `1` (Monday only).

## Files

| File | Editable? | Notes |
|---|---|---|
| `msu_menu.py` | Yes | All logic lives here |
| `config.json` | Yes | Email credentials. NEVER commit to public repo. |
| `com.msu.menu-emailer.plist` | Yes | Must reload after editing (see above) |
| `latest_menu.html` | No | Auto-generated each run, overwritten daily |
| `msu_menu.log` | No | Append-only log, useful for debugging |

## Dependencies

- Python 3.11+ (`/opt/homebrew/bin/python3`)
- `requests` (pip)
- `beautifulsoup4` (pip)
- Standard library: `smtplib`, `email`, `json`, `logging`

## Quick Commands

### First-time install

```bash
cp "/Users/minghaosmacminim4/Documents/All About Tech/Claude-Zotero-Obsidian/msu-menu-emailer/com.msu.menu-emailer.plist" ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.msu.menu-emailer.plist
```

### Check if it's running

```bash
launchctl list | grep msu
```

### Reload after editing the plist (changed time, etc.)

```bash
launchctl unload ~/Library/LaunchAgents/com.msu.menu-emailer.plist
cp "/Users/minghaosmacminim4/Documents/All About Tech/Claude-Zotero-Obsidian/msu-menu-emailer/com.msu.menu-emailer.plist" ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.msu.menu-emailer.plist
```

### Stop it completely (unload and remove)

```bash
launchctl unload ~/Library/LaunchAgents/com.msu.menu-emailer.plist
rm ~/Library/LaunchAgents/com.msu.menu-emailer.plist
```

### Run manually (test)

```bash
cd "/Users/minghaosmacminim4/Documents/All About Tech/Claude-Zotero-Obsidian/msu-menu-emailer"
python3 msu_menu.py
```

### Change time to 6:30 AM

Edit `com.msu.menu-emailer.plist`, change Hour to `6` and Minute to `30`, then reload (see above).

### Add a dining hall

Edit `HALLS` dict in `msu_menu.py`. Find the URL name by visiting the hall's page on eatatstate.msu.edu. Example to add The Vista at Shaw:

```python
HALLS = {
    "Brody Square": "Brody%20Square",
    "The Edge at Akers": "The%20Edge%20at%20Akers",
    "The Gallery at Snyder Phillips": "The%20Gallery%20at%20Snyder%20Phillips",
    "The Vista at Shaw": "The%20Vista%20at%20Shaw",
}
```

No plist reload needed - script changes take effect on next run.

### Remove a dining hall

Delete the line from the `HALLS` dict in `msu_menu.py`. No plist reload needed.

## Troubleshooting

- **Email not sending**: Check `msu_menu.log`. Usually an auth issue - regenerate app password at https://myaccount.google.com/apppasswords
- **No menu data**: The hall might be closed (summer, holidays). Check `latest_menu.html` for "Closed" messages.
- **launchd not running**: `launchctl list | grep msu` to check if loaded. Check `launchd_stdout.log` and `launchd_stderr.log`.
- **Script blocked by macOS permissions (launchd runs but no email)**: Python needs Full Disk Access to read files in `Documents/`. Fix: System Settings > Privacy & Security > Full Disk Access > click + > Cmd+Shift+G > paste `/opt/homebrew/bin/python3` > Open > toggle ON. Without this, launchd silently fails when you're away.
- **Wrong items highlighted**: Edit `HIGHLIGHT_KEYWORDS` in `msu_menu.py`.

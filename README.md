# MSU Menu Emailer

Daily email with MSU dining hall menus. Highlights steak and fish items.

## How to Edit (all on GitHub, no code needed)

### Add/remove email recipients

1. Click **emails.txt** above
2. Click pencil icon (edit)
3. Add or remove emails -- one per line
4. Lines starting with `#` are ignored
5. Click **Commit changes**

### Add/remove dining halls

1. Click **msu_menu.py** above
2. Click pencil icon (edit)
3. Find the `HALLS = {` section near the top
4. Uncomment a hall (remove the `#`) to add it, or comment it out (add `#`) to remove
5. Click **Commit changes**

### Run it now (test)

1. Go to **Actions** tab
2. Click **Daily MSU Menu Email**
3. Click **Run workflow** > **Run workflow**

### Change highlight keywords (steak, fish, etc.)

1. Edit **msu_menu.py** on GitHub
2. Find `HIGHLIGHT_KEYWORDS = [` near the top
3. Add or remove keywords, commit

## Schedule

Runs daily at 7:00 AM Eastern via GitHub Actions.

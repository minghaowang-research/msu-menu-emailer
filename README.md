# MSU Menu Emailer

Daily email with MSU dining hall menus. Highlights steak and fish items.

## How to Edit (all on GitHub, no code needed)

### Add/remove email recipients

1. Go to **Settings** tab (top of this page)
2. Left sidebar: **Secrets and variables** > **Actions**
3. Click pencil icon next to **RECIPIENT_EMAILS**
4. Enter ALL emails comma-separated: `you@gmail.com, friend@gmail.com`
5. Click **Update secret**

Note: GitHub never shows the current value (security feature). You always replace the entire list. To remove someone, paste the full list without them.

Current list: `minghaowang.chinese@gmail.com`

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

# MSU Menu Emailer

Daily email with MSU dining hall menus. Highlights steak and fish items. All recipients are BCC'd (no one sees each other's email).

## Setup (first time)

### 1. Fork this repo

Click **Fork** in the top right. This creates your own copy.

### 2. Create a Gmail app password

1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. You need 2-Step Verification enabled first ([myaccount.google.com/signinoptions/two-step-verification](https://myaccount.google.com/signinoptions/two-step-verification))
3. Under App passwords, enter a name (e.g. "MSU Menu") and click **Create**
4. Copy the 16-character password (spaces don't matter)

### 3. Add GitHub Secrets

In your forked repo:

1. Go to **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret** and add these:

| Name | Value |
|---|---|
| `SENDER_EMAIL` | Your Gmail address (e.g. `you@gmail.com`) |
| `APP_PASSWORD` | The 16-character app password from step 2 |
| `RECIPIENT_EMAILS` | (Optional) Comma-separated emails you want to keep private (e.g. `me@gmail.com,friend@gmail.com`) |

### 4. Add your email

1. Click **emails.txt** in your repo
2. Click pencil icon (edit)
3. Replace `# your-email@gmail.com` with your real email (remove the `#`)
4. Add more emails on separate lines if you want
5. Click **Commit changes**

Or use the `RECIPIENT_EMAILS` secret (Settings > Secrets > Actions, comma-separated) to keep emails private. Both methods work together -- duplicates are automatically removed.

### 5. Test it

1. Go to **Actions** tab
2. Click **Daily MSU Menu Email**
3. Click **Run workflow** > **Run workflow**
4. Check your inbox in a minute or two

That's it! The email will now arrive daily at 7:00 AM Eastern.

---

## How to Customize (all on GitHub, no code needed)

### Add/remove email recipients

1. Click **emails.txt** above
2. Click pencil icon (edit)
3. Add or remove emails -- one per line
4. Lines starting with `#` are ignored
5. Click **Commit changes**

Or use the `RECIPIENT_EMAILS` secret for private emails (see step 3 above).

### Add/remove dining halls

1. Click **msu_menu.py** above
2. Click pencil icon (edit)
3. Find the `HALLS = {` section near the top
4. Uncomment a hall (remove the `#`) to add it, or comment it out (add `#`) to remove
5. Click **Commit changes**

Currently active: Brody, Akers, Gallery (Snyder Phillips), Kellogg.
Available to uncomment: Landon, Case, Shaw, Owen.

### Change highlight keywords (steak, fish, etc.)

Items matching these keywords show up in a special box at the top of the email and are bolded in red in the menu.

1. Edit **msu_menu.py** on GitHub
2. Find `HIGHLIGHT_KEYWORDS = [` near the top
3. Add or remove keywords (lowercase, one per line inside the list)
4. Click **Commit changes**

Current keywords: steak, sirloin, ribeye, filet, strip steak, flank, tenderloin, prime rib, brisket, salmon, fish, tilapia, cod, shrimp, seafood, tuna, mahi, swordfish, trout, catfish, walleye, crab, lobster, scallop, calamari, pollock, halibut, perch, crawfish.

### Change the schedule

1. Edit **.github/workflows/daily-menu.yml**
2. Find the `cron:` line
3. Change the time using [crontab.guru](https://crontab.guru/) for help
4. Default: `0 11 * * *` = 7:00 AM Eastern (11:00 UTC)

### Run it now (test)

1. Go to **Actions** tab
2. Click **Daily MSU Menu Email**
3. Click **Run workflow** > **Run workflow**

## Schedule

Runs daily at 7:00 AM Eastern via GitHub Actions.

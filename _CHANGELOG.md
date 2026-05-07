# Changelog

Newest first. Prepend new rows below this line.

| Date | File | Action | Archive name | Note |
|---|---|---|---|---|
| 2026-05-06 | `emails.txt` | CREATED | - | Email recipient list, one per line. Script reads this instead of secrets/config for recipients. |
| 2026-05-06 | `msu_menu.py` | MODIFIED | - | load_emails() reads emails.txt; load_config() uses it for recipient list |
| 2026-05-06 | `README.md` | CREATED | - | GitHub repo main page: how to edit email list, halls, keywords, and run manually |
| 2026-05-06 | `msu_menu.py` | MODIFIED | - | Updated HIGHLIGHT_KEYWORDS: removed t-bone, added tenderloin, prime rib, brisket, scallop, calamari, pollock, halibut, perch, crawfish |
| 2026-05-06 | `msu_menu.py` | MODIFIED | - | Table layout: halls as side-by-side columns per meal. Green banner hall names. Compact card style for Gmail. |
| 2026-05-06 | `msu_menu.py` | MODIFIED | - | Added Kellogg (active) + 4 commented-out halls (Landon, Case, Shaw, Owen). Halls not on hours page get scraped anyway; "No menu available" shown if empty. |
| 2026-05-06 | `.github/workflows/daily-menu.yml` | CREATED | - | GitHub Actions workflow: runs daily at 11:00 UTC (7 AM EDT), reads secrets for email creds |
| 2026-05-06 | `.gitignore`, `requirements.txt` | CREATED | - | Git config: excludes config.json/logs/cache; pip deps for CI |
| 2026-05-06 | `msu_menu.py` | MODIFIED | - | load_config() now supports env vars (GitHub Actions) with fallback to config.json (local) |
| 2026-05-06 | repo | NOTE | - | Pushed to private GitHub repo minghaowang-research/msu-menu-emailer. Secrets set: SENDER_EMAIL, RECIPIENT_EMAILS, APP_PASSWORD. Test workflow run succeeded. |
| 2026-05-06 | `config.json`, `msu_menu.py`, `HOW_THIS_WORKS.md` | MODIFIED | - | Changed recipient_email (string) to recipient_emails (list) to support multiple recipients. Backward-compatible fallback to old key. |
| 2026-05-06 | `CLAUDE.md` | MODIFIED | - | Updated to match main CLAUDE.md rules: newest-first tracking rule (#7), daily not weekly description, Full Disk Access note, fixed session resume to read first 30 lines, removed stale dry-run command |
| 2026-05-06 | `_CHANGELOG.md`, `_DECISIONS.md` | MODIFIED | - | Reversed to newest-first order per main CLAUDE.md rule #13 |
| 2026-05-06 | `msu_menu.py` | MODIFIED | - | Upgraded closed halls display: bigger styled box with date ranges scraped from data-valid-dates attribute. Fixed hours scraping to use precise CSS selectors (office-hours__item-label/slots/comments) instead of broad li search that was pulling in nav elements. |
| 2026-05-06 | `HOW_THIS_WORKS.md` | MODIFIED | - | Added Full Disk Access troubleshooting tip for launchd permission issue |
| 2026-05-06 | `_Archive/` | NOTE | - | User decided no archive needed for this project. User will manually remove the folder later. |
| 2026-05-06 | `HOW_THIS_WORKS.md` | CREATED | - | Configuration guide for future Claude sessions: how to change halls, keywords, schedule, layout, etc. |
| 2026-05-06 | `msu_menu.py` | MODIFIED | - | Reorganized email: grouped by meal (Breakfast/Lunch/Dinner) then hall then station, instead of hall then station then meal |
| 2026-05-05 | `com.msu.menu-emailer.plist` | MODIFIED | - | Changed from Monday-only to daily (removed Weekday key) |
| 2026-05-05 | `msu_menu.py` | MODIFIED | - | Rewrote from weekly to daily: scrapes today only, subject `[MSU Menu] Day, Date` for Gmail filtering |
| 2026-05-05 | `config.json` | MODIFIED | - | Fixed sender/recipient email to minghaowang.chinese@gmail.com |
| 2026-05-05 | `com.msu.menu-emailer.plist` | MODIFIED | - | Updated paths after folder move |
| 2026-05-05 | `config.json` | MODIFIED | - | Added Gmail app password |
| 2026-05-05 | `CLAUDE.md` | CREATED | - | Project-specific CLAUDE.md with setup docs |
| 2026-05-05 | project | MOVED | - | Moved from `All About Tech/msu-menu-emailer/` to `Claude-Zotero-Obsidian/msu-menu-emailer/` |
| 2026-05-05 | `msu_menu.py` | MODIFIED | - | Added steak/fish highlight feature: orange summary box at top of email, red bold items in menu |
| 2026-05-05 | `com.msu.menu-emailer.plist` | CREATED | - | launchd plist, runs every Monday 7 AM |
| 2026-05-05 | `config.json` | CREATED | - | Gmail SMTP credentials (app password) |
| 2026-05-05 | `msu_menu.py` | CREATED | - | Main script: scrapes 3 MSU dining halls, checks hours page for open/closed, builds weekly HTML email |

**Handoff note (2026-05-06 session 2):** Project on GitHub (private repo minghaowang-research/msu-menu-emailer). GitHub Actions runs daily at 7 AM EDT. Secrets: SENDER_EMAIL, APP_PASSWORD. Email recipients now in `emails.txt` (one per line, editable on GitHub). Active halls: Brody, Akers, Gallery, Kellogg. 4 more commented out in HALLS dict. Email uses table layout (halls as side-by-side columns). README.md on repo has all instructions. Local launchd also works if Mac has Full Disk Access for Python.

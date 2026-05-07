# Decisions

Newest first. Prepend new rows below this line.

| Date | Decision | Why |
|---|---|---|
| 2026-05-06 | Email list in emails.txt instead of GitHub Secrets | Secrets are write-only (can't see current value). A plain text file is visible and editable on GitHub. Repo is private so emails aren't exposed. |
| 2026-05-06 | Table layout (halls as columns) over vertical list | Cuts email length in half; works in Gmail app and desktop. Columns auto-size by hall count. |
| 2026-05-06 | Scrape halls not on hours page instead of skipping | Kellogg (State Room) not listed on hours page under same name. Scrape anyway; show "No menu available" if empty. |
| 2026-05-06 | GitHub Actions over local-only launchd | Runs even when Mac is off/asleep. No Full Disk Access issues. Secrets stored encrypted. |
| 2026-05-06 | No archive workflow for this project | Simple utility script; user prefers no archiving overhead. Will manually remove `_Archive/` folder. |
| 2026-05-05 | Highlight keywords hardcoded in script, not config | Simple list, rarely changes; avoids config complexity |
| 2026-05-05 | Scrape full week (Mon-Sun) in one run | Single email digest is easier to scan than daily emails |
| 2026-05-05 | Gmail SMTP with app password over free email APIs | User already has Gmail; no third-party signup needed; smtplib is stdlib |
| 2026-05-05 | Check hours page before scraping menus | Avoids 7 wasted HTTP requests per closed hall (e.g., summer when only Brody is open) |

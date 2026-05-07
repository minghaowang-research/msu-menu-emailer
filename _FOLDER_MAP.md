# Folder Map

Last updated: 2026-05-06 (session 2)

## Root
| Item | Type | Purpose |
|---|---|---|
| msu_menu.py | file | Main script - scrape, highlight, email |
| config.json | file | Gmail credentials (app password). Sensitive. Git-ignored. |
| com.msu.menu-emailer.plist | file | launchd job definition (local Mac only) |
| latest_menu.html | file | Last generated menu (auto-overwritten). Git-ignored. |
| msu_menu.log | file | Runtime log (auto-appended). Git-ignored. |
| requirements.txt | file | Python pip dependencies for GitHub Actions |
| .gitignore | file | Excludes config.json, logs, cache from repo |
| emails.txt | file | Recipient email list, one per line. Editable on GitHub. |
| README.md | file | GitHub repo main page with how-to instructions |
| CLAUDE.md | file | Project docs and setup reference |
| HOW_THIS_WORKS.md | file | Configuration guide for future Claude sessions |
| _CHANGELOG.md | file | Change tracking (newest first) |
| _FOLDER_MAP.md | file | This file |
| _DECISIONS.md | file | Non-obvious design choices (newest first) |
| _Archive/ | folder | Snapshots before substantive edits |

## .github/workflows/
| Item | Type | Purpose |
|---|---|---|
| daily-menu.yml | file | GitHub Actions workflow - daily cron at 11:00 UTC (7 AM EDT) |

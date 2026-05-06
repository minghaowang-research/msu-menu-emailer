# CLAUDE.md - MSU Menu Emailer

Casual multi-session project. Part 2 tracking applies.
Skip the Session Start Protocol interview - this section already defines the project.
On session start, read `_CHANGELOG.md` (first 30 lines) and proceed.

## What This Is

A standalone Python script that scrapes MSU dining hall menus from eatatstate.msu.edu, highlights steak/fish items, and emails a daily menu digest. Runs automatically every day at 7 AM via macOS launchd plist. Closed halls show date ranges scraped from the hours page.

## Key Files

| File | Purpose |
|---|---|
| `msu_menu.py` | Main script - scrapes, highlights, builds HTML, sends email |
| `config.json` | Gmail credentials (app password). DO NOT commit to any public repo. |
| `com.msu.menu-emailer.plist` | launchd job definition (installed to ~/Library/LaunchAgents/) |
| `latest_menu.html` | Last generated menu (auto-saved each run) |
| `msu_menu.log` | Runtime log |

## Dining Halls Tracked

- Brody Square
- The Edge at Akers
- The Gallery at Snyder Phillips

The script auto-checks which halls are open via the hours page and skips closed ones.

## Highlight Keywords

Steak, sirloin, ribeye, filet, salmon, fish, shrimp, seafood, tuna, cod, tilapia, mahi, swordfish, trout, catfish, walleye, crab, lobster. Edit `HIGHLIGHT_KEYWORDS` in `msu_menu.py` to change.

## Email Setup

- Sender/recipient: minghaowang.chinese@gmail.com
- Auth: Gmail app password stored in config.json
- SMTP: Gmail SSL on port 465

## launchd Setup

```bash
cp com.msu.menu-emailer.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.msu.menu-emailer.plist
```

## Important: macOS Permissions

Python needs Full Disk Access to run via launchd (script is in Documents/). System Settings > Privacy & Security > Full Disk Access > add `/opt/homebrew/bin/python3`.

## Testing

```bash
python3 msu_menu.py
```

---

## Universal Rules (adapted from main CLAUDE.md)

### Session Resume Protocol

When returning to this project:
1. Read `_CHANGELOG.md` (first 30 lines) and `_DECISIONS.md` (first 20 lines). Newest entries are at the top.
2. Say: "Last session: [brief summary]. Want to continue from there or start something new?"

### Core Principles

- Think before acting. Read existing files before writing code.
- State assumptions explicitly. If uncertain, ask.
- Be concise. Deliver exactly what was requested. No extras.
- No sycophantic openers or closing fluff.

### Surgical Changes

- Read the file before modifying it. Never edit blind.
- Prefer editing over rewriting whole files.
- Don't "improve" adjacent code, comments, or formatting.
- Match existing style.
- Every changed line should trace directly to the user's request.

### Simplicity

- Minimum code that solves the problem. Nothing speculative.
- No abstractions for single-use operations.
- No error handling for impossible scenarios.

### Formatting

- No em dashes, smart quotes, or decorative Unicode symbols.
- Plain hyphens and straight quotes only.

### Tracking (Part 2 - MANDATORY)

1. MUST read `_CHANGELOG.md` before modifying any file.
2. NEVER delete a file without archiving to `_Archive/` first.
3. MUST archive before substantive edits (structural changes, logic rewrites).
4. MUST update `_CHANGELOG.md` after every change. Immediately.
5. MUST update `_FOLDER_MAP.md` when files are added, moved, renamed, or archived.
6. Log non-obvious choices in `_DECISIONS.md`.
7. **All tracking files use reverse-chronological order (newest first).** Prepend new entries after the header, before previous entries.

### User Commands

- **"Update tracker"**: Update all tracking docs with everything done this session.
- **"Wrap up"**: Update tracker, summarize session, add handoff note.
- **"Status"**: Read trackers, give 5-bullet overview.
- **"Pick up"**: Run Session Resume Protocol.

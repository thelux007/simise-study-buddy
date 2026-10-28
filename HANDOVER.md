# Handover — thelux007/simise-study-buddy

Scope: personal
Updated (date, time, timezone): 2026-10-28 10:31 SAST (08:31 UTC)
Device and AI tool/account: Unreal 1 (Windows), Claude (personal account)
Branch: docs/handover-setup
Base commit before this session's handover commit: 729ac5b (main, "Add files via upload")
Checkpoint: use the pushed commit containing this document.

## Goal and current state
Flask study app for a Grade 8 learner: homework, tests, streak, textbook upload,
guided AI chat and a weekly email report. The code is the original two-commit upload;
no code has been changed. This session is step 1 of the Project Hub two-device,
two-AI acceptance exercise (device A = Unreal 1 + Claude, device B = Home PC + Codex).

## Changes and reasons
- Added README.md: what the app does, layout, run commands, manual checks and
  known limitations, so the next AI does not have to rediscover them.
- Added .gitignore: keeps `HANDOFF.local.txt`, `server-data/` (personal study data),
  bytecode and `.env` out of this public repository.
- Added shared context files from Project Hub (AGENTS, CLAUDE, GEMINI, HANDOVER,
  TASKS, DECISIONS) and filled in AGENTS.md project details.
- Documentation only. `app.py`, `index.html`, `templates/index.html` are unchanged.

## Checks actually run and results
- `git status` on fresh clone of main at 729ac5b: clean, up to date with origin.
- `python -c "import ast; ast.parse(...app.py...)"`: parses (Python 3.12.10).
- Flask 3.1.3 test client `GET /`: 200, 35627 bytes. `GET /sw.js`: 404 (no static/ folder).
  `server-data/` was not created.
- `cmp index.html templates/index.html`: identical.
- Not run: the live server, chat, upload, report email (all need network/credentials or Poppler).

## Next unfinished task
Fix the weekly report so it lists upcoming tests, and add the project's first automated test.
- Cause: `add_test` saves `testDate` (app.py ~line 77); `send_weekly_report` filters and
  sorts on `date` (app.py ~lines 237 and 241), so upcoming tests are never included.
- Change: make the report read `testDate`. Do not rename stored fields (existing data uses `testDate`).
- Add `tests/test_app.py` (standard `unittest`) that points `DATA_DIR` at a temp folder,
  saves one future test via `POST /api/tests`, patches `urllib.request.urlopen` so no
  email is sent, calls `POST /api/report/send`, and asserts the request body contains the topic.
- Acceptance: `python -m unittest discover -s tests -v` passes; no real network call;
  no `server-data/` created in the repo; README "Known limitations" and "Checks" updated.

## Known issues, blockers and decisions needed
- Decision needed (owner): the GitHub repository is public. Decide whether it should be private.
- See README.md "Known limitations": chat and email send no API keys; upload is Linux-only.

## Reproduce / run locally
- Python 3.10+, `python -m pip install -r requirements.txt`, `python app.py`, open http://localhost:8080.
- Secrets: none are configured. Do not commit keys; use environment variables when this is fixed.

## Transfer state
- Uncommitted changes: all files above, pending the owner's review (update after commit).
- Unpushed commits: branch docs/handover-setup not yet pushed (update after push).
- Large files / external assets and approved location: none.
- Anything the next device cannot access: nothing in `server-data/` (none exists).

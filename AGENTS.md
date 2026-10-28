# Project instructions

Boundary: personal. Repository: thelux007/simise-study-buddy.

Read HANDOVER.md, TASKS.md, DECISIONS.md and README.md before changing code.
Verify these notes against the current branch and actual files. Flag stale notes.
Stay inside this repository. Do not copy code, notes, assets or secrets between personal and company projects.
Use only approved devices, storage and AI accounts. Approval is recorded in the relevant hub's hub.json.
Never include credentials, customer data or private chat history in context files.
Do not push, deploy or create resources unless the user has authorised that action.

## Project-specific details to fill in
- Goal and architecture: Flask study app for a Grade 8 learner. `app.py` (API + server),
  `templates/index.html` (front end). See README.md.
- Install command: `python -m pip install -r requirements.txt`
- Run command: `python app.py` (http://localhost:8080)
- Test command: none yet; use the manual checks in README.md.
- Formatting/lint command: none configured.
- Sensitive or generated paths to avoid: `server-data/` (personal study data), `HANDOFF.local.txt`.
- This repository is PUBLIC on GitHub. Everything committed is world-readable:
  never add the learner's personal details, school data, email addresses or keys.

## End every session
Update HANDOVER.md with what changed, why, checks and remaining work.
Update TASKS.md and record material decisions in DECISIONS.md.
Record the current branch and base commit. After the handover commit is pushed,
the commit containing HANDOVER.md is the authoritative checkpoint.
Tell the user about uncommitted files and unpushed commits; do not imply another computer has them.

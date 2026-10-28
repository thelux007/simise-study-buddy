# Simise Study Buddy

A small Flask web app that helps a Grade 8 (CAPS) learner organise study work:
homework list, upcoming tests, a daily check-in streak, textbook PDF upload,
an AI study chat that guides rather than gives answers, and a weekly email report.

## Layout

- `app.py` — Flask server and JSON API (`/api/homework`, `/api/tests`, `/api/streak`,
  `/api/books`, `/api/chat`, `/api/report/send`).
- `templates/index.html` — the single-page front end served at `/`.
- `index.html` — an identical copy of `templates/index.html` (not used by Flask).
- `requirements.txt` — Python dependencies (Flask only).
- `server-data/` — created at runtime for JSON data and extracted textbook text.
  It holds personal study data and must not be committed.

## Run locally

Requires Python 3.10+.

```text
python -m pip install -r requirements.txt
python app.py
```

Open http://localhost:8080 (set the `PORT` environment variable to change it).

## Checks

There is no automated test suite yet. Current manual checks:

```text
python -c "import ast; ast.parse(open('app.py', encoding='utf-8').read())"
python -c "import app; print(app.app.test_client().get('/').status_code)"
```

The second command should print `200`. It renders the page without creating `server-data/`.

## Known limitations (not yet fixed)

- **AI chat:** the OpenAI request sends no API key, so it always returns the
  "AI service not configured" message unless a hosting platform injects credentials.
- **Weekly report:** the SendGrid request also sends no API key, and the recipient
  address is hard-coded in `app.py`.
- **Upcoming tests in the report:** tests are saved with `testDate`, but the report
  reads `date`, so the report never lists upcoming tests.
- **Textbook upload:** needs `pdftotext`/`pdfinfo` (Poppler) and writes to `/tmp`.
  It tries `apt-get install` if missing, which only works on Debian-style Linux
  with root. It is not expected to work on Windows or macOS as-is.
- **Service worker:** `/sw.js` and other `/static` paths return 404 because no
  `static/` folder exists.

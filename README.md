# Shows

A small Flask app that searches a database of TV shows by title. Requests and
errors are logged as structured JSON using [structlog](https://www.structlog.org/).

## Requirements

- Python 3.9+
- A SQLite database named `shows.db` (see below)

## Setup

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt
```

## Database

`shows.db` is **not** included in this repository (it is large). Place your own
copy in the project root, next to `app.py`. The search uses the `shows` table:

```sql
CREATE TABLE shows (
    id INTEGER,
    title TEXT NOT NULL,
    year NUMERIC,
    episodes INTEGER,
    PRIMARY KEY(id)
);
```

## Run

```bash
flask --app app run
```

Then open http://127.0.0.1:5000 in your browser.

Add `--debug` for auto-reload while developing, or `--port 5055` to change the port.

## Endpoints

| Route | Description |
|---|---|
| `/` | Search page |
| `/search?q=<text>` | JSON list of up to 50 shows whose title contains `<text>`. Returns `[]` if `q` is missing or nothing matches, and HTTP 500 with `[]` if the database query fails. |

Example:

```bash
curl "http://127.0.0.1:5000/search?q=office"
```

## Logging

Logging is configured once at startup by `setup_logging()` in `logging_config.py`.

- **File:** `logs/app.log`, one JSON object per line. The file rotates at 5 MB
  and keeps 3 backups (`app.log.1` to `app.log.3`).
- **Console:** the same events in readable, colored text.
- **Created automatically:** the `logs/` folder is created on first run and is
  ignored by git.

Example lines:

```json
{"event": "search", "query": "office", "results": 50, "level": "info", "logger": "app", "timestamp": "2026-11-25T16:38:26.258581Z"}
{"event": "request", "method": "GET", "path": "/search", "status": 200, "level": "info", "logger": "app", "timestamp": "2026-11-25T16:38:26.259841Z"}
```

Failed searches are logged at `error` level with the query and full traceback
in an `exception` field.

To filter the log for errors, use [`jq`](https://jqlang.github.io/jq/):

```bash
jq 'select(.level=="error")' logs/app.log
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests build a small temporary `shows.db`, so they don't need the real
database. They run automatically on every push and pull request through GitHub
Actions (`.github/workflows/tests.yml`) on Python 3.11, 3.12 and 3.13.

## Project layout

```
app.py              Flask app and routes
logging_config.py   structlog setup (JSON file + console)
wsgi.py             Minimal hello-world app (not used by app.py)
templates/          HTML templates
requirements.txt    Python dependencies
requirements-dev.txt  Test dependencies (pytest)
tests/              Test suite
.github/workflows/  CI workflow
```

## License

MIT. See [LICENSE](LICENSE).

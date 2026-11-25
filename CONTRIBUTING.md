# Contributing

Thanks for your interest in improving Shows! This guide covers how to set up the
project, make a change, and get it merged.

## Reporting bugs and requesting features

Open an issue and pick the matching form:
[bug report](https://github.com/hassan-kowa/shows/issues/new/choose) or feature
request. Please include steps to reproduce and any relevant lines from
`logs/app.log` (remove anything private).

## Development setup

```bash
git clone https://github.com/hassan-kowa/shows.git
cd shows

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements-dev.txt
```

The app needs a `shows.db` SQLite database to run (see the [README](README.md)).
The tests do not: they build a small temporary one.

## Running the tests

```bash
pytest
```

All tests must pass before a change can be merged. CI runs them on Python 3.11,
3.12 and 3.13.

## Making a change

The `main` branch is protected. You can't push to it directly, and every change
needs a pull request with passing tests.

1. Create a branch from `main`:
   ```bash
   git checkout -b short-description-of-change
   ```
2. Make your change. Add or update tests for new behavior.
3. Run `pytest`.
4. Commit with a clear message that says what changed and why.
5. Push the branch and open a pull request. The description is pre-filled from
   the [pull request template](.github/pull_request_template.md), so fill in each section.
6. Wait for the `test` checks to go green, then merge.

## Code guidelines

- Keep changes focused. One pull request should do one thing.
- Log with structlog, not `print`. Use short snake_case event names and put
  variable data in key/value pairs, for example
  `log.info("search", query=query, results=len(shows))`.
- Use `log.exception(...)` inside `except` blocks so tracebacks are recorded.
- Don't log secrets or personal data.
- Update the README if you change setup, usage or logging behavior.

## Changing dependencies

`requirements.txt` and `requirements-dev.txt` are generated lock files. Do not
edit them by hand. Edit `requirements.in` or `requirements-dev.in`, then
regenerate (see "Updating dependencies" in the [README](README.md)) and commit
both the `.in` and `.txt` files.

Dependabot opens a monthly pull request for dependency and GitHub Actions
updates. Merge it once the tests pass.

## License

By contributing, you agree that your contributions will be licensed under the
[MIT License](LICENSE).

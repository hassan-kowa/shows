import logging

from logging_config import _WerkzeugFilter


def make_record(message, level=logging.INFO):
    return logging.LogRecord("werkzeug", level, __file__, 1, message, (), None)


def test_startup_address_line_is_kept_and_cleaned():
    record = make_record(
        "\x1b[31m\x1b[1mWARNING: This is a development server.\x1b[0m\n"
        " * Running on http://127.0.0.1:5000"
    )
    assert _WerkzeugFilter().filter(record)
    assert "\x1b" not in record.getMessage()
    assert "Running on http://127.0.0.1:5000" in record.getMessage()


def test_access_log_lines_are_dropped():
    record = make_record('127.0.0.1 - - [25/Nov/2026] "GET / HTTP/1.1" 200 -')
    assert not _WerkzeugFilter().filter(record)


def test_other_info_lines_are_dropped():
    assert not _WerkzeugFilter().filter(make_record("Press CTRL+C to quit"))


def test_warnings_and_errors_always_pass():
    assert _WerkzeugFilter().filter(make_record("something odd", logging.WARNING))
    assert _WerkzeugFilter().filter(make_record("it broke", logging.ERROR))

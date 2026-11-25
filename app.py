from cs50 import SQL
from flask import Flask, render_template, session, request, redirect, jsonify
from flask_session import Session
import structlog

from logging_config import setup_logging

setup_logging()
log = structlog.get_logger()

app = Flask(__name__)
log.info("app_started")


@app.after_request
def log_request(response):
    log.info(
        "request",
        method=request.method,
        path=request.path,
        status=response.status_code,
    )
    return response

db = SQL("sqlite:///shows.db")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():

    query = request.args.get("q")
    try:
        if query:
            shows = db.execute(
                "SELECT * FROM shows WHERE title Like ? LIMIT 50", "%" + query + "%")
        else:
            shows = []
    except Exception:
        log.exception("search_failed", query=query)
        return jsonify([]), 500

    log.info("search", query=query, results=len(shows))
    return jsonify(shows)

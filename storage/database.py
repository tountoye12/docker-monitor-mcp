import sqlite3
import logging

from config.settings import DATABASE_PATH
from contextlib import closing
import json


logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True, exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    return connection

def initialize_database() -> None:
    """
    Initialize the monitoring database tables.
    """

    with closing(get_connection()) as connection:

        # Enable concurrent reading and writing
        connection.execute("PRAGMA journal_mode=WAL")

        with connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS monitoring_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    completed_at TEXT NOT NULL,
                    duration_seconds REAL NOT NULL,
                    report_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS active_incidents (
                    incident_id TEXT PRIMARY KEY,
                    container_id TEXT NOT NULL,
                    container_name TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    incident_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS incident_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id TEXT NOT NULL,
                    event TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    incident_data TEXT NOT NULL
                );
            """)

    logger.info("Monitoring database initialized.")


def save_monitoring_report(report: dict) -> int:
    """
    Save an infrastructure monitoring report.
    """

    with closing(get_connection()) as connection:

        with connection:
            cursor = connection.execute(
                """
                INSERT INTO monitoring_reports (
                    started_at,
                    completed_at,
                    duration_seconds,
                    report_data
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    report["started_at"],
                    report["completed_at"],
                    report["duration_seconds"],
                    json.dumps(report)
                )
            )

            report_id = cursor.lastrowid

    logger.info("Monitoring report saved: %s", report_id)

    return report_id

def get_latest_report() -> dict | None:
    """
    Retrieve the most recent infrastructure monitoring report.
    """

    with closing(get_connection()) as connection:

        row = connection.execute(
            """
            SELECT report_data
            FROM monitoring_reports
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

        if row is None:
            return None

        report = json.loads(row["report_data"])

        return report
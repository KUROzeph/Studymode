import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path(__file__).parent / "sm.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            color TEXT NOT NULL DEFAULT '#ffffff',
            created_at TEXT NOT NULL,
            deleted_at TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            started_at TEXT NOT NULL,
            ended_at TEXT NOT NULL,
            duration INTEGER NOT NULL,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # For databases created before deleted_at existed
    columns = connection.execute(
        "PRAGMA table_info(subjects)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    if "deleted_at" not in column_names:
        connection.execute(
            "ALTER TABLE subjects ADD COLUMN deleted_at TEXT"
        )

    connection.commit()
    connection.close()


def add_subject(name, color="#ffffff"):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO subjects
        (name, color, created_at, deleted_at)
        VALUES (?, ?, ?, NULL)
        """,
        (
            name,
            color,
            datetime.now().isoformat()
        )
    )

    connection.commit()

    subject_id = cursor.lastrowid

    connection.close()

    return subject_id


def get_subjects():
    connection = get_connection()

    subjects = connection.execute(
        """
        SELECT id, name, color, created_at
        FROM subjects
        WHERE deleted_at IS NULL
        ORDER BY name
        """
    ).fetchall()

    connection.close()

    return subjects


def rename_subject(subject_id, new_name):
    connection = get_connection()

    connection.execute(
        """
        UPDATE subjects
        SET name = ?
        WHERE id = ?
        AND deleted_at IS NULL
        """,
        (
            new_name,
            subject_id
        )
    )

    connection.commit()
    connection.close()


def delete_subject(subject_id):
    connection = get_connection()

    connection.execute(
        """
        UPDATE subjects
        SET deleted_at = ?
        WHERE id = ?
        AND deleted_at IS NULL
        """,
        (
            datetime.now().isoformat(),
            subject_id
        )
    )

    connection.commit()
    connection.close()


def restore_subject(subject_id):
    connection = get_connection()

    connection.execute(
        """
        UPDATE subjects
        SET deleted_at = NULL
        WHERE id = ?
        """,
        (subject_id,)
    )

    connection.commit()
    connection.close()


def save_study_session(
    subject_id,
    started_at,
    ended_at,
    duration
):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO study_sessions
        (subject_id, started_at, ended_at, duration)
        VALUES (?, ?, ?, ?)
        """,
        (
            subject_id,
            started_at.isoformat(),
            ended_at.isoformat(),
            duration
        )
    )

def get_study_sessions():
    connection = get_connection()

    sessions = connection.execute(
        """
        SELECT
            study_sessions.id,
            study_sessions.subject_id,
            subjects.name AS subject_name,
            study_sessions.started_at,
            study_sessions.ended_at,
            study_sessions.duration
        FROM study_sessions
        JOIN subjects
            ON study_sessions.subject_id = subjects.id
        ORDER BY study_sessions.started_at DESC
        """
    ).fetchall()

    connection.close()

    return sessions

    connection.commit()
    connection.close()
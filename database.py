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
            created_at TEXT NOT NULL
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

    connection.commit()
    connection.close()


def add_subject(name, color="#ffffff"):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO subjects (name, color, created_at)
        VALUES (?, ?, ?)
        """,
        (name, color, datetime.now().isoformat())
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
        ORDER BY name
        """
    ).fetchall()

    connection.close()

    return subjects


def save_study_session(subject_id, started_at, ended_at, duration):
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

    connection.commit()
    connection.close()
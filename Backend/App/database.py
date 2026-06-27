import sqlite3
from datetime import datetime
from pathlib import Path
from memory import trim_memory


# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure data folder exists
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "chatbot.db"

# Database connection
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    sender TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
)
""")

conn.commit()


def info(message):
    print(message)


def success(message):
    print(message)


def get_sessions(persona_name):
    cursor.execute("""
        SELECT id, persona, created_at, updated_at
        FROM sessions
        WHERE persona = ?
        ORDER BY updated_at DESC
        LIMIT 5
    """, (persona_name,))

    return [
        {
            "id": row["id"],
            "persona": row["persona"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
        for row in cursor.fetchall()
    ]


def get_session_by_index(persona_name, index: int):
    cursor.execute("""
        SELECT id, persona, created_at, updated_at
        FROM sessions
        WHERE persona=?
        ORDER BY updated_at DESC
        LIMIT 1 OFFSET ?
    """, (persona_name, index))

    row = cursor.fetchone()

    if not row:
        return None

    return {
        "id": row["id"],
        "persona": row["persona"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"]
    }


def load_session(persona, system_message, session=None):
    if session:
        session_id = session["id"]

        cursor.execute("""
            SELECT id, sender, content
            FROM messages
            WHERE session_id = ?
            ORDER BY id ASC
        """, (session_id,))

        rows = cursor.fetchall()
        messages = [system_message]

        for row in rows:
            if row["sender"] == "system":   # ← was row[1] / role[1], both wrong
                continue
            messages.append({
                "id": row["id"],
                "role": row["sender"],      # ← column is "sender" not "role"
                "content": row["content"]
            })
    else:
        first_msg = persona.get(
            "opening_prompt",
            "Introduce yourself and start the conversation."
        )
        messages = [
            system_message,
            {"role": "assistant", "content": first_msg}
        ]

    full_messages = messages.copy()

    if len(messages) > 15:
        messages = trim_memory(messages, system_message)

    return messages, full_messages


def save_session(persona_name, messages, session_id=None):
    if not messages:
        info("No messages to save.")
        return None

    now = datetime.now().isoformat()

    if session_id:
        cursor.execute("""
            UPDATE sessions SET persona=?, updated_at=? WHERE id=?
        """, (persona_name, now, session_id))
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    else:
        cursor.execute("""
            INSERT INTO sessions(persona, created_at, updated_at) VALUES (?, ?, ?)
        """, (persona_name, now, now))
        session_id = cursor.lastrowid

    for msg in messages:
        if msg.get("role") == "system":
            continue
        cursor.execute("""
            INSERT INTO messages(session_id, sender, content) VALUES (?, ?, ?)
        """, (session_id, msg["role"], msg["content"]))

    conn.commit()
    return session_id


def delete_session(session_id):
    if not session_id:
        return False

    cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    return True


def prompt_input(prompt):
    return input(prompt)


def print_sessions(sessions):
    if not sessions:
        print("No previous sessions found.")
        return

    print("Previous sessions:")
    for index, session in enumerate(sessions, start=1):
        print(f"{index}. Session {session['id']} ({session['updated_at']})")


def pick_session(persona_name):
    sessions = get_sessions(persona_name)
    if not sessions:
        return None

    print_sessions(sessions)
    choice = prompt_input("Choose session (or N for new): ").strip().lower()

    if choice in {"", "n"}:
        return None
    if choice == "exit":
        raise SystemExit(0)

    try:
        index = int(choice)
    except ValueError:
        return None

    if 1 <= index <= len(sessions):
        return sessions[index - 1]
    return None

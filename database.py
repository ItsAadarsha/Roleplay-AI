# Handles all MongoDB operations for sessions
from pymongo import MongoClient
from datetime import datetime
from config import MONGO_URI
from bson import ObjectId
from cli import prompt_input, print_sessions, success, info

# Module-level connection — shared across all DB calls
client = MongoClient(MONGO_URI)
db = client["chatbot"]
sessions_col = db["sessions"]

def save_session(persona_name, messages, session_id=None):
    """Save a new session or update an existing one.

    If `session_id` is provided, update that document instead of inserting.
    """
    now = datetime.now()
    if session_id:
        # Accept either ObjectId or raw string
        try:
            _id = ObjectId(session_id)
        except Exception:
            _id = session_id
        result = sessions_col.update_one(
            {"_id": _id},
            {"$set": {"persona": persona_name, "messages": messages, "updated_at": now}}
        )
        if result.matched_count:
            success("Session updated.")
            return

    # No matching document found — insert a new one
    sessions_col.insert_one({
        "persona": persona_name,
        "messages": messages,
        "created_at": now,
        "updated_at": now
    })
    success("Session saved.")

def get_sessions(persona_name):
    # Return the 5 most recent sessions for this persona
    results = sessions_col.find(
        {"persona": persona_name},
        {"_id": 1, "created_at": 1, "messages": 1}
    ).sort("created_at", -1).limit(5)
    return list(results)

def pick_session(persona_name):
    # Show existing sessions and let the user choose one, or start fresh
    sessions = get_sessions(persona_name)

    if not sessions:
        return None

    print_sessions(sessions)
    choice = prompt_input("Enter number or N:").strip().lower()

    if choice == "n":
        return None

    try:
        index = int(choice) - 1
        if 0 <= index < len(sessions):
            return sessions[index]
    except ValueError:
        pass

    info("Invalid choice, starting new session.")
    return None

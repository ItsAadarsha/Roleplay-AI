# Loads a session from the DB (or starts a new one) and returns the message list
from database import pick_session
from cli import print_message
from memory import trim_memory

def load_session(persona, system_message):
    # Try to resume an existing session; fall back to a fresh one
    existing_session = pick_session(persona["name"]) if persona and persona.get("name") else None

    if existing_session:
        # Rebuild the message list: system message first, then user/assistant turns only
        # (skip system and summary messages that were stored from previous trims)
        messages = [system_message] + [
            msg for msg in existing_session["messages"]
            if not msg["role"] == "system" and not msg.get("is_summary")
        ]
        print(f"Resuming session from {existing_session['created_at'].strftime('%Y-%m-%d %H:%M')}.\n")

        # Replay the conversation to the terminal so the user has context
        for msg in messages:
            if msg.get("role") == "system":
                continue
            print_message(msg["role"], persona["name"], msg["content"])
            if msg.get("role") == "assistant":
                print()
    else:
        # Fresh session — start with just the system message and the persona's opening line
        messages = [system_message]
        first_msg = persona.get("opening_prompt", "Introduce yourself and start the conversation.")
        print_message("assistant", persona["name"], first_msg)
        print()
        messages.append({"role": "assistant", "content": first_msg})

    # Keep a full copy before trimming (used for saving to DB)
    full_messages = messages

    # Pre-trim if the loaded history is already long
    messages = trim_memory(messages, system_message) if len(messages) > 15 else messages

    return messages, existing_session, full_messages

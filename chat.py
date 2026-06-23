import ollama
from config import MODEL
from memory import trim_memory
from personalities import pick_personality
from config import textPrompt
from database import save_session, pick_session
from cli import header, print_message, prompt_input, info
from response import get_response
def run():
    
    persona = pick_personality()
    header(f"Now chatting with {persona['name']}")
    print("Type 'Exit' to quit.\n")

    user_name = prompt_input("Your name (optional): ")

    def render_template(template):
        return template.replace("{{char}}", persona.get("name", "")).replace("{{user}}", user_name or "You")

    template = f"{persona.get('system','')}\n\n{textPrompt}\n\nScenario: {persona.get('Scenario','')}"
    system_message = {
        "role": "system",
        "content": render_template(template)
    }

    existing_session = pick_session(persona["name"])

    if existing_session:
        # Restore messages, replacing the base system prompt but keeping summary system messages
        messages = [system_message] + [
            msg for msg in existing_session["messages"]
            if not (msg["role"] == "system" and not msg.get("is_summary"))
        ]
        print(f"Resuming session from {existing_session['created_at'].strftime('%Y-%m-%d %H:%M')}.\n")

        for msg in messages:
            print_message(msg["role"], persona["name"], msg["content"])
            if msg.get("role") == "assistant":
                print()
    else:
        messages = [system_message]

        first_msg = persona.get("opening_prompt", "Introduce yourself and start the conversation.")
        print_message("assistant", persona["name"], first_msg)
        print()
        messages.append({"role": "assistant", "content": first_msg})

    initial_user_count = sum(1 for m in messages if m.get("role") == "user")
    # Only trim after this many new messages have been added in this run
    TRIM_INTERVAL = 5
    messages_since_trim = 0
    # runtime flag: becomes True when the user sends a message during this run
    user_sent = False

    while True:
        user_input = prompt_input("You:")
        if user_input == 'Exit':
            # If we received any user messages during this run, save the session.
            # Fall back to the original count-based check for safety.
            if user_sent or sum(1 for m in messages if m.get("role") == "user") > initial_user_count:
                if existing_session:
                    save_session(persona["name"], messages, existing_session.get("_id"))
                else:
                    save_session(persona["name"], messages)
            else:
                info("No new user messages — session not saved.")
            print("Exiting...")
            return

        messages.append({
            "role": "user",
            "content": user_input
        })
        user_sent = True
        messages_since_trim += 1


        assistant_msg = get_response(messages)
        print_message("assistant", persona["name"], assistant_msg)
        print()

        messages.append({
            "role": "assistant",
            "content": assistant_msg
        })
        messages_since_trim += 1

        # Trim only once every TRIM_INTERVAL messages to reduce calls
        if messages_since_trim >= TRIM_INTERVAL:
            messages = trim_memory(messages, system_message)
            messages_since_trim = 0
# Main chat loop — orchestrates persona, session, message flow, and memory trimming
from memory import trim_memory
from personalities import pick_personality
from config import textPrompt
from database import save_session
from session_manager import load_session
from cli import header, print_message, prompt_input, info
from response import get_response

def run():
    # Pick or create a persona, then greet the user
    persona = pick_personality()
    header(f"Now chatting with {persona['name']}")
    print("Type 'Exit' to quit.\n")

    # Build the system message from the persona's config + global style prompt
    template = f"{persona.get('system','')}\n\n{textPrompt}\n\nScenario: {persona.get('Scenario','')}"
    system_message = {
        "role": "system",
        "content": template
    }

    # Load an existing session or start fresh
    messages, existing_session, full_messages = load_session(persona, system_message)

    # Track how many user messages existed before this run (for save-on-exit logic)
    initial_user_count = sum(1 for m in messages if m.get("role") == "user")
    TRIM_INTERVAL = 5       # trigger memory trim every N new messages
    messages_since_trim = 0
    user_sent = False       # becomes True once the user sends their first message

    # full_messages is the complete untruncated history used for saving to DB
    actual_messages = full_messages

    while True:
        user_input = prompt_input("You:")

        if user_input == 'Exit':
            # Only save if the user actually sent something new this run
            if user_sent or sum(1 for m in messages if m.get("role") == "user") > initial_user_count:
                if existing_session:
                    save_session(persona["name"], actual_messages, existing_session.get("_id"))
                else:
                    save_session(persona["name"], actual_messages)
            else:
                info("No new user messages — session not saved.")
            print("Exiting...")
            return

        messages.append({"role": "user", "content": user_input})
        user_sent = True
        messages_since_trim += 1

        # Call the LLM; on failure let the user retry rather than crashing
        assistant_msg = None
        try:
            assistant_msg = get_response(messages)
        except RuntimeError as e:
            print(f"[Error] Could not get a response: {e}")
            print("You can try again or type 'Exit' to quit.\n")
            continue

        print_message("assistant", persona["name"], assistant_msg)
        print()

        messages.append({"role": "assistant", "content": assistant_msg})
        messages_since_trim += 1

        # Summarise and compress history once the trim interval is reached
        if messages_since_trim >= TRIM_INTERVAL:
            actual_messages.extend(messages)
            messages = trim_memory(messages, system_message)
            messages_since_trim = 0

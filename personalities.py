# Manages persona selection and creation
from database import db
from cli import header, prompt_input, info
from config import textPrompt

personalities_col = db["personalities"]

def get_personalities():
    # Return all personas as a dict keyed by their "key" field
    results = personalities_col.find({}, {"_id": 0})
    return {p["key"]: p for p in results}


def create_personality():
    # Prompt the user to fill in a new persona and persist it to the DB
    header("Create a new persona")
    name = prompt_input("Name:").strip()
    system = prompt_input("System prompt (describe the personality):").strip()
    scenario = prompt_input("Scenario (describe the situation):").strip()
    firstMessage = prompt_input("First Message: ").strip()

    personalities = get_personalities()
    keys = [int(p["key"]) for p in personalities.values()]
    next_key = str(max(keys) + 1) if keys else "1"  # auto-increment key

    new_persona = {
        "key": next_key,
        "name": name,
        "system": system,
        "Scenario": scenario,
        "opening_prompt": firstMessage
    }

    personalities_col.insert_one(new_persona)
    info(f"Persona '{name}' created!")
    return new_persona


def pick_personality():
    # List available personas and let the user choose or create a new one
    personalities = get_personalities()

    header("Pick a personality")
    for key, val in personalities.items():
        print(f"  {key}. {val['name']}")
    print("  N. Create new persona")

    choice = prompt_input("Enter number or N:").strip().lower()

    if choice == "n":
        return create_personality()

    if choice not in personalities:
        info("Invalid choice, defaulting to first persona.")

    return personalities.get(choice, list(personalities.values())[0])

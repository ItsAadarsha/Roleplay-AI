# Manages persona selection and creation
from database import conn
from config import textPrompt

cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS personalities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    system TEXT,
    scenario TEXT,
    opening_prompt TEXT
)
""")

conn.commit()



def get_personalities():
    cursor = conn.cursor()
    cursor.execute("""
        SELECT key, name, system, scenario, opening_prompt
        FROM personalities
    """)
    results = cursor.fetchall()

    return {
        row["key"]: {
            "key": row["key"],
            "name": row["name"],
            "system": row["system"],
            "Scenario": row["scenario"],
            "opening_prompt": row["opening_prompt"]
        }
        for row in results
    }


def create_personality(name: str, system: str, scenario: str, opening_prompt: str):
    cursor = conn.cursor()
    personalities = get_personalities()
    keys = [int(p["key"]) for p in personalities.values()]
    next_key = str(max(keys) + 1) if keys else "1"  # auto-increment key

    new_persona = {
        "key": next_key,
        "name": name,
        "system": system,
        "Scenario": scenario,
        "opening_prompt": opening_prompt
    }

    cursor.execute("""
        INSERT INTO personalities
        (key, name, system, scenario, opening_prompt)
        VALUES (?, ?, ?, ?, ?)
    """, (
        new_persona["key"],
        new_persona["name"],
        new_persona["system"],
        new_persona["Scenario"],
        new_persona["opening_prompt"]
    ))
    conn.commit()
    return new_persona


def pick_personality(choice: str):
    # List available personas and let the user choose or create a new one
    personalities = get_personalities()
    
    if not personalities:
        return None

    if choice.lower() == "n":
        return None
    
    normalized = {str(k): v for k, v in personalities.items()}


    if choice not in personalities:
        return list(personalities.values())[0]


    return normalized[choice] 
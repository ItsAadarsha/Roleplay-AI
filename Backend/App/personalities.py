from database import get_db
from sqlalchemy import Column, Integer, Text
import re
from models import Personality, Session   # <-- Session added

def init_personalities_db():
    # Handled by Base.metadata.create_all()
    pass


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def get_personalities():
    with get_db() as db:
        results = db.query(Personality).all()

        return {
            p.key: {
                "key": p.key,
                "name": p.name,
                "description": p.description or "",
                "system": p.system,
                "scenario": p.scenario,
                "opening_prompt": p.opening_prompt,
                "avatar": p.avatar or "",
            }
            for p in results
        }


def create_personality(
    name,
    description,
    system,
    scenario,
    opening_prompt,
    avatar=None
):
    with get_db() as db:

        base_key = slugify(name)
        key = base_key
        suffix = 1

        while db.query(Personality).filter(
            Personality.key == key
        ).first():
            key = f"{base_key}_{suffix}"
            suffix += 1

        personality = Personality(
            key=key,
            name=name,
            description=description or "",
            system=system,
            scenario=scenario,
            opening_prompt=opening_prompt,
            avatar=avatar or ""
        )

        db.add(personality)
        db.flush()

        return {
            "key": personality.key,
            "name": personality.name,
            "description": personality.description,
            "system": personality.system,
            "Scenario": personality.scenario,
            "opening_prompt": personality.opening_prompt,
            "avatar": personality.avatar,
        }


def update_personality(
    key,
    name,
    description,
    system,
    scenario,
    opening_prompt,
    avatar=None
):
    with get_db() as db:
        personality = (
            db.query(Personality)
            .filter(Personality.key == key)
            .first()
        )

        if not personality:
            return None

        personality.name = name
        personality.description = description or ""
        personality.system = system
        personality.scenario = scenario
        personality.opening_prompt = opening_prompt
        personality.avatar = avatar or ""

        db.flush()

        return {
            "key": personality.key,
            "name": personality.name,
            "description": personality.description,
            "system": personality.system,
            "Scenario": personality.scenario,
            "opening_prompt": personality.opening_prompt,
            "avatar": personality.avatar,
        }


def delete_personality(key: str):
    with get_db() as db:
        # Delete all sessions belonging to this personality
        # (cascade will remove their messages and context automatically)
        sessions = db.query(Session).filter(Session.persona_key == key).all()
        for session in sessions:
            db.delete(session)

        # Now delete the personality itselff
        rows = db.query(Personality).filter(Personality.key == key).delete()
        return rows > 0


def pick_personality(key: str):
    with get_db() as db:
        personality = (
            db.query(Personality)
            .filter(Personality.key == key)
            .first()
        )

        if not personality:
            return None

        return {
            "key": personality.key,
            "name": personality.name,
            "description": personality.description,
            "system": personality.system,
            "Scenario": personality.scenario,
            "opening_prompt": personality.opening_prompt,
            "avatar": personality.avatar,
        }
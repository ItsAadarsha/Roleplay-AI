from fastapi import (
    APIRouter,
    HTTPException,
    Form,
    File,
    UploadFile,
    FastAPI
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from personalities import (
    get_personalities,
    create_personality,
    update_personality,
    delete_personality,
    pick_personality,
)
from database import save_session, load_session, get_session_by_index, get_sessions, delete_session, DATA_DIR 
from response import get_response
from memory import trim_memory
from config import textPrompt
import os
import shutil
from uuid import uuid4
from pathlib import Path


app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
AVATAR_DIR = Path(DATA_DIR) / "images"

os.makedirs(AVATAR_DIR, exist_ok=True)

# Mount static files to serve images
app.mount("/data/images", StaticFiles(directory=str(AVATAR_DIR)), name="images")

#------------------PERSONALITIES----------------------


@app.get("/personalities")
def list_personalities():
    return get_personalities()


@app.post("/personalities", status_code=201)
async def create_persona(
    name: str = Form(...),
    description: str = Form(None),
    system: str = Form(...),
    scenario: str = Form(...),
    opening_prompt: str = Form(...),
    avatar: UploadFile = File(None)
):
    avatar_rel_path = None

    if avatar:
        # Keep unique filename
        extension = avatar.filename.split(".")[-1]
        filename = f"{uuid4()}.{extension}"

        # Store file in Data/images/
        file_path = AVATAR_DIR / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)
        
        # Return URL path for frontend to access
        avatar_rel_path = f"/data/images/{filename}"

    return create_personality(
        name=name,
        description=description,
        system=system,
        scenario=scenario,
        opening_prompt=opening_prompt,
        avatar=avatar_rel_path
    )


@app.put("/personalities/{persona_key}")
async def update_persona(
    persona_key: str,
    name: str = Form(...),
    description: str = Form(None),
    system: str = Form(...),
    scenario: str = Form(...),
    opening_prompt: str = Form(...),
    avatar: UploadFile = File(None)
):
    avatar_rel_path = None

    if avatar:
        extension = avatar.filename.split(".")[-1]
        filename = f"{uuid4()}.{extension}"

        # Store file in Data/images/
        file_path = AVATAR_DIR / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)
        
        # Return URL path for frontend to access
        avatar_rel_path = f"/data/images/{filename}"

    updated = update_personality(
        persona_key,
        name,
        description,
        system,
        scenario,
        opening_prompt,
        avatar_rel_path,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Persona not found."
        )

    return updated

@app.delete("/personalities/{persona_key}")
def delete_persona(persona_key: str):
    deleted = delete_personality(persona_key)
    if not deleted:
        raise HTTPException(status_code=404, detail="Persona not found.")
    return {"deleted": True}

class PickPersonaRequest(BaseModel):
    choice: str

@app.post("/personalities/pick")
def pick_persona(body: PickPersonaRequest):
    result = pick_personality(body.choice)
    if result is None:
        raise HTTPException(
            status_code=400,
            detail="No personalities exist or choice was 'n'. POST /personalities to create one."
        )
    return result


#------------------SESSIONS----------------------
@app.get("/sessions/{persona_name}")
def list_sessions(persona_name: str):
    """Get the last 5 sessions for a persona."""
    sessions = get_sessions(persona_name)
    if not sessions:
        return {"sessions": [], "message": "No previous sessions found."}
    return {"sessions": sessions}


@app.delete("/sessions/{persona_name}/{session_id}")
def delete_session_endpoint(persona_name: str, session_id: int):
    deleted = delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"deleted": True}


class PickSessionRequest(BaseModel):
    persona_name: str
    index: int | None = None  # None = start new session

@app.post("/sessions/pick")
def pick_session_endpoint(body: PickSessionRequest):
    """Pick a session by index, or pass null index to start a new one."""
    if body.index is None:
        return {"session": None, "new": True}

    session = get_session_by_index(body.persona_name, body.index - 1)  # 1-based
    if not session:
        return {"session": None, "new": True, "warning": "Index out of range, starting new session."}

    return {"session": session, "new": False}

class SessionData(BaseModel):
    id: int
    persona: str
    created_at: str
    updated_at: str

class LoadSessionRequest(BaseModel):
    persona_key: str
    session: SessionData | None = None  # pass null to start fresh
    

@app.post("/sessions/load")
def load(body: LoadSessionRequest):
    personalities = get_personalities()
    persona = personalities.get(body.persona_key)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found.")

    template = f"{persona.get('system','')}\n\n{textPrompt}\n\nScenario: {persona.get('Scenario','')}"
    system_message = {"role": "system", "content": template}

    # Convert Pydantic model to dict if session exists
    session_dict = body.session.model_dump() if body.session else None
    messages, full_messages = load_session(persona, system_message, session_dict)
    
    # Remove id field from messages for clean response
    clean = [{k: v for k, v in m.items() if k != "id"} for m in messages]

    return {
        "session": session_dict,
        "messages": clean,
        "full_messages": full_messages,
        "resumed": body.session is not None
    }

class SaveSessionRequest(BaseModel):
    persona_key: str
    full_messages: list[dict]
    session_id: int | None = None

@app.post("/sessions/save")
def save(body: SaveSessionRequest):
    personalities = get_personalities()
    persona = personalities.get(body.persona_key)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found.")
    session_id = save_session(persona["name"], body.full_messages, body.session_id)
    return {"saved": True, "session_id": session_id}

    
# ── Chat ───────────────────────────────────────────────────

class ChatRequest(BaseModel):
    persona_key: str
    messages: list[dict]        
    full_messages: list[dict]   
    session_id: int | None = None
    user_input: str

@app.post("/chat")
def chat(body: ChatRequest):
    personalities = get_personalities()
    persona = personalities.get(body.persona_key)
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found.")
    
    template = f"{persona.get('system','')}\n\n{textPrompt}\n\nScenario: {persona.get('Scenario','')}"
    system_message = {"role": "system", "content": template}

    messages = body.messages + [{"role": "user", "content": body.user_input}]

    try:
        assistant_msg = get_response(messages)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    
    messages.append({"role": "assistant", "content": assistant_msg})
    messages = trim_memory(messages, system_message)

    # Update full history
    msg_id = max((m.get("id", 0) for m in body.full_messages), default=0)
    full_messages = body.full_messages + [
        {"id": msg_id + 1, "role": "user",      "content": body.user_input},
        {"id": msg_id + 2, "role": "assistant",  "content": assistant_msg},
    ]

    return {
        "assistant_message": assistant_msg,
        "messages": messages,
        "full_messages": full_messages,
    }

**Roleplay Chat — Local AI Conversational App**

- **Purpose:**: Small CLI app for roleplay conversations with configurable personalities and a chat backend (OpenAI / Ollama / Claude).
- **Language:**: Python 3.11+ (tested on 3.13) with a virtual environment.

**Quick Start**

- **Create env:**: 

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- **Environment:**: Set these env vars before running.
  - **API_KEY:**: Your provider API key.
  - **PROVIDER:**: `openai` | `ollama` | `claude` (choose matching provider).
  - **MODEL:**: Model identifier used by your provider (e.g. `gpt-4o-mini`, `llama2`, etc.).

- **Run:**:

```powershell
python main.py
```

**Important Files**

- **`main.py`:**: CLI entrypoint that launches the chat loop.
- **`chat.py`:**:: Handles runtime chat loop, input/output, and session saving.
- **`response.py`:**:: Wraps the provider client and sends chat requests.
- **`session_manager.py`:**: Loads/resumes sessions from the database and trims messages.
- **`database.py`:**:: Persistence helpers (sessions storage).
- **`memory.py`:**:: Conversation summarization and trimming helpers.
- **`personalities.py`:**:: Personality definitions and selection logic.
- **`config.py`:**: Project configuration (MODEL, PROVIDER, API_KEY, textPrompt).

**Notes & Troubleshooting**

- If you see a JSON "Circular reference detected" error when calling the provider, ensure the `messages` you pass to `response.get_response()` is a flat list of message dicts (no nested lists or objects).
- The app uses a simple summarization + trimming strategy. If sessions grow unexpectedly large, increase trimming frequency or shorten saved history.

**Contributing**

- Open a PR with focused changes. Run the app locally and include any test instructions in the PR description.



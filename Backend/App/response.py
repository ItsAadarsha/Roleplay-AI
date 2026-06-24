# Handles all LLM API calls via aisuite, with retry logic
import aisuite as ai
import time
from config import AISUITE_MODEL, PROVIDER, API_KEY           

def get_client():
    provider_configs = {}
    if PROVIDER == "ollama":
        provider_configs["ollama"] = {"api_url": "http://localhost:11434/api"}
    elif PROVIDER == "deepseek":
        provider_configs["openai"] = {
            "api_key": API_KEY,
            "base_url": "https://api.deepseek.com"
        }
    return ai.Client(provider_configs=provider_configs if provider_configs else None)

def get_response(messages, retries=3, backoff=2):
    client = get_client()
    last_error = None

    TRANSIENT_KEYWORDS = ("rate limit", "429", "500", "502", "503", "connection")
    TIMEOUT_KEYWORDS = ("timeout", "timed out")

    for attempt in range(1, retries + 1):
        try:
            response = client.chat.completions.create(model=AISUITE_MODEL, messages=messages)
            choices = response.choices
            if not choices or choices[0].message.content is None:
                raise ValueError("Empty or malformed response from API")
            return choices[0].message.content

        except ValueError:
            raise

        except Exception as e:
            last_error = e
            err_str = str(e).lower()

            is_timeout = any(k in err_str for k in TIMEOUT_KEYWORDS)
            is_transient = any(k in err_str for k in TRANSIENT_KEYWORDS)

            if is_timeout or is_transient:
                wait = backoff * attempt * (3 if is_timeout else 1)
                print(f"[Attempt {attempt}/{retries}] {'Timeout' if is_timeout else 'Transient error'} — retrying in {wait}s: {e}")
                time.sleep(wait)
            else:
                raise

    raise RuntimeError(f"API call failed after {retries} attempts: {last_error}")

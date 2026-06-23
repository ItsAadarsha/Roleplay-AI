# Handles conversation summarization and memory trimming
from response import get_response

def summarize(messages):
    # Sends the raw message list to the LLM and returns a plain-text summary
    summary_prompt = [
        {
            "role": "system",
            "content": "You are a summarization assistant. Summarize the conversation clearly and in detail."
        },
        {
            "role": "user",
            "content": f"Summarize this chat:\n\n{messages}"
        }
    ]
    return get_response(summary_prompt)


def trim_memory(messages, system_message):
    # Strip all system messages first so slicing only operates on user/assistant turns.
    # This prevents system message duplication across multiple trim cycles.
    non_system = [m for m in messages if m.get("role") != "system"]

    # Summarize everything except the 10 most recent exchanges
    old = non_system[:-10]
    new = non_system[-10:]
    summary = summarize(old)

    # Rebuild: fresh system message → summary → recent turns
    return [
        system_message,
        {"role": "system", "content": f"Conversation summary: {summary}"}
    ] + new

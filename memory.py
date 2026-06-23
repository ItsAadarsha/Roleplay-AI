from response import get_response

def summarize(messages):
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
    
    non_system = [m for m in messages if m.get("role") != "system"]
    old = non_system[:-10]
    new = non_system[-10:]
    summary = summarize(old)
    return [
        system_message,
        {"role": "system", "content": f"Conversation summary: {summary}"}
    ] + new
    
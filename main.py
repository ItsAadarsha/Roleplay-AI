import ollama
from dotenv import load_dotenv
import os

load_dotenv()
MODEL = os.getenv("MODEL_NAME")

PERSONALITIES = {
    "1": {
        "name": "Alex",
        "system": """You are Alex, a 20 year old college student chatting on Discord.
                    You're chill, funny, a bit sarcastic. You play games, watch anime, broke 24/7.
                    Talk casually, use slang, keep replies short. Never break character."""
    },
    "2": {
        "name": "Luna",
        "system": """You are Luna, a mysterious girl who's into dark academia and philosophy.
                    You speak thoughtfully but still casual. You ask deep questions and enjoy debates.
                    Never break character."""
    },
    "3": {
        "name": "Kai",
        "system": """You are Kai, an overconfident street-smart guy who thinks he knows everything.
                      You're funny without trying to be. Competitive, loud, but secretly caring.
                      Never break character."""
    },
}

def pick_personality():
    print("Pick a personality:")
    for key, val in PERSONALITIES.items():
        print(f"  {key}. {val['name']}")
    
    choice = input("Enter number: ").strip()
    return PERSONALITIES.get(choice, PERSONALITIES["1"])  # default to Alex
  

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
  response = ollama.chat(
        model=MODEL,
        messages=summary_prompt,
    )

  return response["message"]["content"]


def main():
    persona = pick_personality()
    prompt = """You are a real person chatting on Discord, not an AI assistant.
                          Talk like a normal person texting their friend — casual, relaxed, natural.

                          Rules:
                          - Keep messages short (1-3 sentences max unless explaining something)
                          - Use lowercase most of the time
                          - Use internet slang naturally (ngl, lowkey, fr, nah, bro, lol, etc.)
                          - Never say things like 'Certainly!', 'Of course!', 'As an AI...' or any AI speak
                          - React like a person would — agree, disagree, joke around, ask stuff back
                          - Don't over-explain. If someone says 'yo wsg' just say 'nm you?' or something
                          - Occasional typos or 'lol' are fine
                          - Match the vibe of whoever you're talking to"""

    messages = [
        {
            "role": "system",
            "content": persona["system"]
        }
    ]
    

    while True:
        user_input = input("You: ")
        if user_input == 'Exit':
          print("Exitting...")
          return

        messages.append({
            "role": "user",
            "content": user_input
        })

        response = ollama.chat(
            model=MODEL,
            messages=messages,
            
        )

        assistant_msg = response["message"]["content"]
        print("AI:", assistant_msg)

        messages.append({
            "role": "assistant",
            "content": assistant_msg
        })

        # memory limit
        if len(messages) >= 100:
            systemMessage = messages[0]
            old = messages[1:-10]
            new = messages[-10:]
            
            summary = summarize(old)
            
            messages = [
              systemMessage,
              {
                "role": "system",
                "content": f"Conversation summary = {summary}"
              } 
            ] + new

if __name__ == '__main__':
    main()
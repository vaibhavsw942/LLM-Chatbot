import os
import sys
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    sys.exit("GEMINI_API_KEY not found. Copy .env.example to .env and add your key.")

# Models are tried in order; if one is busy (503) or missing (404), the next is used.
# Names change over time; override with GEMINI_MODELS="model1,model2" in .env.
MODELS = [
    m.strip()
    for m in os.getenv(
        "GEMINI_MODELS",
        os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        + ",gemini-3.5-flash,gemini-flash-latest,gemini-flash-lite-latest",
    ).split(",")
    if m.strip()
]

# Context window management: only the last N messages are sent to the API.
MAX_MESSAGES = 10

SYSTEM_PROMPT = (
    "You are StudyBuddy, a friendly study assistant for college students. "
    "Explain concepts simply, with short examples. Keep answers under 150 words "
    "unless asked for more. If a question is not about studying, learning, or "
    "careers, politely steer back to those topics. Never invent facts; say "
    "'I'm not sure' when you don't know."
)

client = genai.Client(api_key=API_KEY)
history = []  # list of types.Content, alternating user / model


def recent_history():
    """Last MAX_MESSAGES messages, always starting with a user message."""
    recent = history[-MAX_MESSAGES:]
    while recent and recent[0].role != "user":
        recent = recent[1:]
    return recent


def ask(user_text):
    history.append(types.Content(role="user", parts=[types.Part(text=user_text)]))
    for model in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=recent_history(),
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        http_options=types.HttpOptions(timeout=30000),  # 30 seconds
                    ),
                )
                text = (response.text or "").strip()
                if not text:
                    raise ValueError("Empty response from the model")
                history.append(types.Content(role="model", parts=[types.Part(text=text)]))
                return text
            except Exception as exc:
                err = str(exc)
                if any(k in err for k in ("API_KEY_INVALID", "PERMISSION_DENIED", "UNAUTHENTICATED")):
                    history.pop()
                    return "Your API key looks invalid. Please check GEMINI_API_KEY in your .env file."
                if any(k in err for k in ("404", "NOT_FOUND", "429", "RESOURCE_EXHAUSTED")):
                    break  # model missing or quota over, try the next model
                if attempt == 0:
                    time.sleep(2)  # 503/504: wait once, then retry
    history.pop()  # all models failed: keep history valid
    return "Sorry, I couldn't reach the AI right now. Please try again in a moment."

def main():
    print("StudyBuddy ready. Type 'reset' to clear memory, 'quit' to exit.\n")
    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if not user_text:
            continue
        if user_text.lower() in ("quit", "exit"):
            print("Bye!")
            break
        if user_text.lower() == "reset":
            history.clear()
            print("Bot: Memory cleared.\n")
            continue
        print(f"Bot: {ask(user_text)}\n")


if __name__ == "__main__":
    main()

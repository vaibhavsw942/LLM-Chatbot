# LLM Chatbot (StudyBuddy)

A command-line chatbot backed by the Google Gemini API. It keeps multi-turn
conversation history, trims old messages to fit the context window, and uses a
system prompt that gives it a defined role.

## Features
- Multi-turn memory (the bot can refer to things said earlier)
- Context window management: only the last 10 messages are sent per request
- System prompt: friendly study assistant for college students
- Error handling: network failure, timeout, rate limit (429), invalid API key or
  empty response show a friendly message instead of crashing. Temporary errors
  (503/504) are retried, and the app falls back to other models.
- API key loaded from an environment variable, never committed

## Setup
1. Get a free API key from Google AI Studio (https://aistudio.google.com).
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and paste your key:
   ```
   copy .env.example .env
   ```
   ```
   GEMINI_API_KEY=your_key_here
   ```
5. Run:
   ```
   python app.py
   ```

Commands: `reset` clears memory, `quit` exits.

## Configuration
- `GEMINI_API_KEY`: your API key (required)
- `GEMINI_MODELS`: optional comma-separated list of models, tried in order

## How context management works
Every message is stored in a list. On each request only the last `MAX_MESSAGES`
(10) are sent, and the slice always starts with a user message so the API
accepts it. Change `MAX_MESSAGES` in `app.py` to tune it.
 what a list is in 2 lines
## Sample conversation
````
You: My name is Vaibhav and I study CSE.
Bot: Hi Vaibhav! It's great to meet you. Computer Science and Engineering is an exciting and fast-paced field!

I'm here to help you tackle your coursework-whether you need simple explanations of complex algorithms, help understanding data structures, or tips on how to prepare for exams and tech careers.

What are you currently studying or working on right now?

You: I like Python. Explain what a list is in 2 lines
Bot: Python is a great choice, Vaibhav!

A list is an ordered collection of items that can be changed (mutable) and can hold different data types. For example, `my_list = [1, "apple", 3.5]` stores multiple values in a single variable.

You: Give one small example.
Bot: Sure, Vaibhav!

Here is a quick example:
```python
fruits = ["apple", "banana", "cherry"]
print(fruits[0])  # Output: apple
```

You can easily grab items using their index position!

You: Now explain the same thing using a real-life analogy.
Bot: Think of a Python list like a shopping list written on a whiteboard, Vaibhav.

You can write down items in a specific order (like eggs, milk, and bread), cross things out, add new items to the bottom, or even erase an item and replace it with something else whenever you want!

You: What is my name and what do I study?
Bot: Your name is Vaibhav, and you study Computer Science and Engineering (CSE)!
````
## Possible improvements
- Summarise older messages into a running summary instead of dropping them
- Add a simple web UI with Flask
"""
agent.py
The orchestrator - your local LLM (via Ollama) decides which tool/agent
to call based on what you ask, then responds with the result.

Run with: python agent.py
"""

import ollama
import json
from tools import (
    get_weather,
    web_search,
    calculator,
    save_note,
    read_notes,
    scrape_page_title_and_text,
)

MODEL = "qwen2.5:7b"

# Map tool name -> actual python function
AVAILABLE_TOOLS = {
    "get_weather": get_weather,
    "web_search": web_search,
    "calculator": calculator,
    "save_note": save_note,
    "read_notes": read_notes,
    "scrape_page_title_and_text": scrape_page_title_and_text,
}

# Tool definitions the LLM sees - this is how it knows what each "agent" does
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "City name"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the internet for current information on any topic.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Search query"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a basic math expression like '12*4+1'.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_note",
            "description": "Save a short note/reminder to local storage.",
            "parameters": {
                "type": "object",
                "properties": {"note": {"type": "string"}},
                "required": ["note"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_notes",
            "description": "Read all previously saved notes.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "scrape_page_title_and_text",
            "description": "Fetch a webpage URL and return its title and a text preview.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
]


def run_agent(user_message: str, history: list) -> str:
    history.append({"role": "user", "content": user_message})

    response = ollama.chat(
        model=MODEL,
        messages=history,
        tools=TOOL_DEFINITIONS,
    )

    msg = response["message"]

    # If the model wants to call a tool
    if msg.get("tool_calls"):
        history.append(msg)
        for call in msg["tool_calls"]:
            name = call["function"]["name"]
            args = call["function"]["arguments"]
            if isinstance(args, str):
                args = json.loads(args)

            print(f"  [Calling agent: {name}({args})]")

            if name in AVAILABLE_TOOLS:
                result = AVAILABLE_TOOLS[name](**args)
            else:
                result = f"Unknown tool: {name}"

            history.append({"role": "tool", "content": str(result)})

        # Ask the model to give a final answer using the tool result
        followup = ollama.chat(model=MODEL, messages=history)
        final_text = followup["message"]["content"]
        history.append({"role": "assistant", "content": final_text})
        return final_text

    # No tool needed, just a normal reply
    history.append({"role": "assistant", "content": msg["content"]})
    return msg["content"]


def main():
    print("=== Local AI Voice Assistant ===")
    print("Type 'voice' to switch to voice mode, 'text' for typing mode, 'exit' to quit.")

    from voice import speak
    from listen import listen

    voice_mode = False

    history = [
        {
            "role": "system",
            "content": "You are a helpful assistant with access to tools for weather, "
            "web search, calculations, notes, webpage scraping, email (read/draft/send), "
            "calendar (view/create events), file reading (PDF/Excel/text), and Python code execution. "
            "Use tools when needed. For emails: always use draft_email first to show the user a "
            "preview, and only call send_email after the user explicitly confirms. "
            "Keep spoken responses concise and conversational since they may be read aloud.",
        }
    ]

    while True:
        if voice_mode:
            user_input = listen()
            if not user_input:
                continue
        else:
            user_input = input("\nYou: ").strip()

        if user_input.lower() in ("exit", "quit"):
            break
        if user_input.lower() == "voice":
            voice_mode = True
            print("[Switched to voice mode]")
            continue
        if user_input.lower() == "text":
            voice_mode = False
            print("[Switched to text mode]")
            continue
        if not user_input:
            continue

        answer = run_agent(user_input, history)
        print(f"\nAssistant: {answer}")

        if voice_mode:
            speak(answer)


if __name__ == "__main__":
    main()
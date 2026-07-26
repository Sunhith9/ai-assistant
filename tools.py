"""
tools.py
Each function here is a "specialist agent" the orchestrator can call.
All are free - no paid API keys needed.
"""

import requests
from ddgs import DDGS


# ---------- WEATHER AGENT ----------
def get_weather(city: str) -> str:
    """Get current weather for a city using free wttr.in API (no key needed)."""
    try:
        url = f"https://wttr.in/{city}?format=%C+%t+%h+%w"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return f"Weather in {city}: {resp.text.strip()}"
        return f"Could not fetch weather for {city}."
    except Exception as e:
        return f"Weather agent error: {e}"


# ---------- WEB SEARCH AGENT ----------
def web_search(query: str) -> str:
    """Search the web using free DuckDuckGo search (no key needed)."""
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append(f"- {r['title']}: {r['body'][:150]}... ({r['href']})")
        if not results:
            return "No search results found."
        return "Search results:\n" + "\n".join(results)
    except Exception as e:
        return f"Web search agent error: {e}"


# ---------- CALCULATOR AGENT ----------
def calculator(expression: str) -> str:
    """Safely evaluate a basic math expression."""
    try:
        allowed = "0123456789+-*/(). "
        if not all(c in allowed for c in expression):
            return "Invalid characters in expression."
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculator error: {e}"


# ---------- FILE NOTES AGENT (local memory, free, no API) ----------
NOTES_FILE = "notes.txt"

def save_note(note: str) -> str:
    """Save a note locally."""
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(note + "\n")
    return f"Saved note: {note}"

def read_notes() -> str:
    """Read all saved notes."""
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return content if content else "No notes saved yet."
    except FileNotFoundError:
        return "No notes saved yet."


# ---------- WEBSITE SCRAPER AGENT ----------
def scrape_page_title_and_text(url: str) -> str:
    """Fetch a webpage and return its title + first chunk of text (free, no key)."""
    try:
        from bs4 import BeautifulSoup
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string if soup.title else "No title"
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs[:5])
        return f"Title: {title}\nContent preview: {text[:500]}"
    except Exception as e:
        return f"Scraper agent error: {e}"

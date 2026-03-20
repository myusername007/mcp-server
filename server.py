from mcp.server.fastmcp import FastMCP
import json
import os

NOTES_FILE = "notes.json"


mcp = FastMCP("My First MCP Server")


def load_notes() -> dict:
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    return {}


@mcp.tool()
def save_note(title: str, content: str) -> str:
    """Save a note with a title and content"""
    notes = load_notes()
    notes[title] = content
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)
    return f"Note '{title}' saved successfully"


@mcp.tool()
def get_note(title: str) -> str:
    """Returns note by title or Note not found"""
    notes = load_notes()
    if title in notes:
        return notes[title]
    else: return "Note not found"


@mcp.tool()
def list_notes() -> str:
    """Returns notes list or No notes yet"""
    notes = load_notes()
    if not notes:
        return "No notes yet"
    return json.dumps(notes, indent=2)  # конвертуємо в str


@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city"""
    weather_data = {
        "Kyiv": "Rainy, 12°C",
        "London": "Cloudy, 15°C",
        "Lviv": "Sunny, 18°C"
    }
    return weather_data.get(city, "Unknown city")


@mcp.tool()
def calculate(expression: str) -> str:
    """Calculate a mathematical expression"""
    try:
        result = eval(expression)
        return str(result)
    except:
        return "Invalid expression"

if __name__ == "__main__":
    mcp.run()
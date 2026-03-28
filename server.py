from mcp.server.fastmcp import FastMCP
import json
import os
import sqlite3
import requests
from dotenv import load_dotenv
load_dotenv("/Users/root7/mcp_server/.env")

NOTES_FILE = "/Users/root7/mcp_server/notes.json"
DB_FILE = "/Users/root7/mcp_server/tasks.db"
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


mcp = FastMCP("My First MCP Server")


def load_notes() -> dict:
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    return {}


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT ,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0 
        )
    """)
    conn.commit()
    return conn

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
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ua"
    }
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        return f"Could not get weather for {city}"
    
    data = response.json()
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    description = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]

    return f"{city}: {description}, {temp}°C (відчувається як {feels_like}°C), вологість {humidity}%"

@mcp.tool()
def calculate(expression: str) -> str:
    """Calculate a mathematical expression"""
    try:
        result = eval(expression)
        return str(result)
    except:
        return "Invalid expression"

#db tools
@mcp.tool()
def add_task(title: str) -> str:
    """"Add a new task"""
    conn = get_db()
    conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    conn.commit()
    conn.close()
    return f"Task '{title}' added"


@mcp.tool()
def get_tasks() -> str:
    """Print all tasks"""
    conn = get_db()
    cursor = conn.execute("SELECT id, title, done FROM tasks")

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No tasks"
    
    result = []
    for task_id, title, done in rows:
        mark = "x" if done else " "
        result.append(f"{task_id}. [{mark}] {title}")

    return "\n".join(result)
    
@mcp.tool()
def complete_task(task_id: int) -> str:
    """Mark task as done"""
    conn = get_db()
    cursor = conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        return "Task not found"
    return f"Task {task_id} is done!"

@mcp.tool()
def delete_task(task_id: int) -> str:
    """Delete task"""
    conn = get_db()
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        return "Task not found"
    return f"Task {task_id} was deleted!"



if __name__ == "__main__":
    mcp.run()
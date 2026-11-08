import asyncio
import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# --- Models ---

@dataclass
class AgentEvent:
    id: str
    timestamp: float
    event_type: str
    payload: str

class TaskRequest(BaseModel):
    task_description: str
    priority: int = 1

# --- Database Layer ---

class DatabaseManager:
    def __init__(self, db_path: str = "agent_data.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    timestamp REAL,
                    event_type TEXT,
                    payload TEXT
                )
            """)
            conn.commit()

    def log_event(self, event_type: str, payload: str):
        event = AgentEvent(str(uuid.uuid4()), time.time(), event_type, payload)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO events VALUES (?, ?, ?, ?)",
                (event.id, event.timestamp, event.event_type, event.payload)
            )

    def get_recent_events(self, limit: int = 20) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

# --- Application ---

app = FastAPI(title="Agent Agentic AI 9F64B3")
db = DatabaseManager()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #09090B; color: #FAFAFA; font-family: 'Inter', sans-serif; }
        .card { background-color: #121214; border: 1px solid #27272A; }
        .mono { font-family: 'Courier New', monospace; }
    </style>
</head>
<body class="p-8">
    <div class="max-w-4xl mx-auto">
        <header class="mb-8">
            <h1 class="text-2xl font-bold tracking-tight">Agent Agentic AI 9F64B3</h1>
            <p class="text-zinc-500 text-sm">Autonomous Infrastructure Controller</p>
        </header>

        <div class="grid grid-cols-1 gap-6">
            <div class="card p-6 rounded-lg">
                <h2 class="text-sm font-semibold mb-4 uppercase tracking-wider text-zinc-400">Dispatch Task</h2>
                <form id="taskForm" class="flex gap-4">
                    <input type="text" id="taskInput" placeholder="Enter instruction..." 
                           class="flex-1 bg-zinc-900 border border-zinc-800 rounded px-4 py-2 focus:outline-none focus:border-blue-500">
                    <button type="submit" class="bg-white text-black px-6 py-2 rounded font-medium hover:bg-zinc-200 transition">Execute</button>
                </form>
            </div>

            <div class="card p-6 rounded-lg">
                <h2 class="text-sm font-semibold mb-4 uppercase tracking-wider text-zinc-400">Event Stream</h2>
                <div id="eventLog" class="space-y-2 mono text-xs"></div>
            </div>
        </div>
    </div>

    <script>
        async function updateLogs() {
            const res = await fetch('/api/events');
            const data = await res.json();
            const logDiv = document.getElementById('eventLog');
            logDiv.innerHTML = data.map(e => `
                <div class="flex justify-between border-b border-zinc-800 py-2">
                    <span class="text-blue-400">[${new Date(e.timestamp * 1000).toLocaleTimeString()}]</span>
                    <span class="text-zinc-300">${e.event_type}</span>
                    <span class="text-zinc-500 truncate max-w-xs">${e.payload}</span>
                </div>
            `).join('');
        }

        document.getElementById('taskForm').onsubmit = async (e) => {
            e.preventDefault();
            const input = document.getElementById('taskInput');
            await fetch('/api/task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task_description: input.value})
            });
            input.value = '';
            updateLogs();
        };

        setInterval(updateLogs, 3000);
        updateLogs();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_TEMPLATE

@app.get("/api/events")
async def get_events():
    return db.get_recent_events()

async def process_task_logic(description: str):
    # Simulated agent reasoning loop
    db.log_event("TASK_RECEIVED", description)
    await asyncio.sleep(1)
    db.log_event("PLANNING", "Decomposing task into sub-steps")
    await asyncio.sleep(1)
    db.log_event("EXECUTION", "Executing sub-steps via internal toolset")
    db.log_event("COMPLETED", "Task finalized successfully")

@app.post("/api/task")
async def create_task(task: TaskRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_task_logic, task.task_description)
    return {"status": "accepted", "task": task.task_description}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from .core import EventBus
from .models import TaskEvent

app = FastAPI(title="Agentic AI 9F64B3")
bus = EventBus()

@app.on_event("startup")
async def startup_event():
    import asyncio
    asyncio.create_task(bus.run_worker())

@app.post("/dispatch")
async def dispatch_task(event: TaskEvent):
    await bus.publish(event)
    return {"status": "queued", "task_id": event.task_id}

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <html class="dark">
    <body class="bg-[#09090B] text-white font-sans p-8">
        <div class="max-w-4xl mx-auto border border-white/10 bg-[#121214] p-6 rounded-xl">
            <h1 class="text-2xl font-bold mb-4">9F64B3 Telemetry</h1>
            <div id="metrics" class="grid grid-cols-3 gap-4">
                <div class="p-4 border border-white/10 rounded-lg">
                    <div class="text-xs text-gray-400">THROUGHPUT</div>
                    <div class="text-2xl font-mono">0.0 ops/s</div>
                </div>
            </div>
        </div>
        <script src="https://cdn.tailwindcss.com"></script>
    </body>
    </html>
    """
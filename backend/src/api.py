"""FastAPI backend for LùnPetShop chatbot."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import uuid
import time
import asyncio
import os
from langchain_core.messages import HumanMessage

from .chatbot import graph
from .prompts import get_greeting
from .metrics import metrics_collector, get_system_metrics, get_service_health, test_chat_endpoint
from .discord_monitor import DiscordHealthMonitor

# Initialize Discord monitor
discord_monitor = DiscordHealthMonitor()
monitor_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup
    global monitor_task
    
    if discord_monitor.enabled:
        print("🔔 Starting Discord health monitoring...")
        # Start monitoring in background
        interval = int(os.getenv("DISCORD_CHECK_INTERVAL", "3600"))  # Default 1 hour
        monitor_task = asyncio.create_task(
            discord_monitor.start_monitoring(interval_seconds=interval)
        )
        print(f"✅ Discord monitoring started (checking every {interval}s)")
    else:
        print("ℹ️  Discord monitoring disabled (set DISCORD_WEBHOOK_URL to enable)")
    
    yield
    
    # Shutdown
    if monitor_task:
        print("🛑 Stopping Discord monitoring...")
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        print("✅ Discord monitoring stopped")


app = FastAPI(
    title="LùnPetShop KittyCat Chatbot API",
    description="AI Chatbot API for LùnPetShop pet store",
    version="0.4.2",
    lifespan=lifespan,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware to track request metrics
@app.middleware("http")
async def track_metrics(request: Request, call_next):
    """Track request metrics."""
    start_time = time.time()
    endpoint = f"{request.method} {request.url.path}"
    
    try:
        response = await call_next(request)
        response_time = time.time() - start_time
        is_error = response.status_code >= 400
        metrics_collector.record_request(endpoint, response_time, is_error)
        return response
    except Exception as e:
        response_time = time.time() - start_time
        metrics_collector.record_request(endpoint, response_time, is_error=True)
        raise


# Request/Response Models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    language: Optional[str] = "vi"


class ChatResponse(BaseModel):
    response: str
    thread_id: str
    language: str


class GreetingRequest(BaseModel):
    language: Optional[str] = "vi"


class GreetingResponse(BaseModel):
    greeting: str
    thread_id: str


# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "LùnPetShop KittyCat Chatbot"}


# Comprehensive health metrics endpoint
@app.get("/health/metrics")
async def health_metrics():
    """Comprehensive health metrics endpoint."""
    app_stats = metrics_collector.get_stats()
    system_metrics = get_system_metrics()
    service_health = get_service_health()
    
    # Test actual chat endpoint functionality
    chat_endpoint_test = test_chat_endpoint()
    
    # Determine overall health status
    overall_status = "healthy"
    
    # Check tunnel first (critical for production)
    tunnel_status = service_health.get("tunnel", {}).get("status", "unknown")
    if tunnel_status == "unhealthy":
        overall_status = "unhealthy"  # Tunnel down = production broken
    elif tunnel_status == "not_configured" and overall_status == "healthy":
        overall_status = "degraded"  # No tunnel = can't serve production
    
    # Check chat endpoint (most critical for functionality)
    if chat_endpoint_test["status"] == "unhealthy":
        overall_status = "unhealthy"
    elif chat_endpoint_test["status"] == "degraded" and overall_status == "healthy":
        overall_status = "degraded"
    
    # Check error rates
    if app_stats["error_rate"] > 0.1:  # More than 10% error rate
        overall_status = "degraded"
    if app_stats["error_rate"] > 0.5:  # More than 50% error rate
        overall_status = "unhealthy"
    
    # xAI API not configured is OK (rule-based responses work)
    if not service_health["xai_api"]["configured"] and overall_status == "healthy":
        overall_status = "degraded"  # Can still work with rule-based responses
    
    return {
        "status": overall_status,
        "service": "LùnPetShop KittyCat Chatbot",
        "version": "0.4.0",
        "timestamp": time.time(),
        "application": app_stats,
        "system": system_metrics,
        "services": service_health,
        "endpoints": {
            "chat": chat_endpoint_test
        }
    }


# Greeting endpoint
@app.post("/api/greeting", response_model=GreetingResponse)
async def get_greeting_message(request: GreetingRequest):
    """Get a greeting message to start the conversation."""
    thread_id = str(uuid.uuid4())
    greeting = get_greeting(request.language)
    
    return GreetingResponse(
        greeting=greeting,
        thread_id=thread_id,
    )


# Chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return a response."""
    try:
        # Generate or use existing thread_id
        thread_id = request.thread_id or str(uuid.uuid4())
        
        # Create config with thread_id for memory
        config = {"configurable": {"thread_id": thread_id}}
        
        # Create input with user message
        input_data = {
            "messages": [HumanMessage(content=request.message)],
            "language": request.language,
        }
        
        # Invoke the graph
        result = graph.invoke(input_data, config)
        
        # Extract the assistant's response (last message)
        assistant_message = result["messages"][-1].content
        detected_language = result.get("language", request.language)
        
        return ChatResponse(
            response=assistant_message,
            thread_id=thread_id,
            language=detected_language,
        )
        
    except Exception as e:
        import traceback
        error_msg = f"Error processing chat: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)


# Serve static files (frontend)
# Widget files are served from the widget/ directory (single source of truth)
try:
    import os
    from pathlib import Path
    
    # Get the project root (go up from backend/src/api.py -> backend -> project root)
    backend_dir = Path(__file__).parent.parent
    project_root = backend_dir.parent
    widget_dir = project_root / "widget"
    
    # Serve widget assets
    app.mount("/static", StaticFiles(directory=str(widget_dir)), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the demo frontend HTML."""
        widget_html = widget_dir / "index.html"
        if widget_html.exists():
            return FileResponse(str(widget_html))
        else:
            return {"message": "Widget demo page not found. Please check widget/index.html"}
except Exception as e:
    # If widget directory doesn't exist yet, that's okay
    print(f"⚠️  Warning: Could not mount widget files: {e}")
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


"""FastAPI backend for LùnPetShop chatbot."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
from langchain_core.messages import HumanMessage

from .chatbot import graph, get_greeting

app = FastAPI(
    title="LùnPetShop KittyCat Chatbot API",
    description="AI Chatbot API for LùnPetShop pet store",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    """Health check endpoint."""
    return {"status": "healthy", "service": "LùnPetShop KittyCat Chatbot"}


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
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the frontend HTML."""
        return FileResponse("static/index.html")
except:
    # If static directory doesn't exist yet, that's okay
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


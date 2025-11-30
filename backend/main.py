"""Main entry point for LùnPetShop KittyCat Chatbot."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import uvicorn

# Load environment variables from project root
backend_dir = Path(__file__).parent
project_root = backend_dir.parent
load_dotenv(project_root / ".env")  # Load from project root .env file

# Check for required environment variables
if not os.getenv("XAI_API_KEY"):
    print("⚠️  Warning: XAI_API_KEY not found in environment variables!")
    print("Please create a .env file with your xAI API key:")
    print("XAI_API_KEY=your_api_key_here")
    print("\nYou can get an API key from: https://console.x.ai/")


class HealthCheckFilter(logging.Filter):
    """Filter to suppress health check request logs."""
    def filter(self, record):
        # Suppress logs for GET /health requests
        message = record.getMessage()
        if 'GET /health HTTP' in message or 'GET /health/metrics HTTP' in message:
            return False
        return True


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print("🐱 Starting LùnPetShop KittyCat Chatbot...")
    print(f"🌐 Server running on: http://{host}:{port}")
    print(f"📱 Open in browser: http://localhost:{port}")
    print("\n🐾 Ready to help customers!\n")
    
    # Change to backend directory for imports
    import sys
    import os
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    # Configure logging to filter out health check requests
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.addFilter(HealthCheckFilter())
    
    uvicorn.run(
        "src.api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )


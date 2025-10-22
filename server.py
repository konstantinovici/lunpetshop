#!/usr/bin/env python3
"""
Simple HTTP server for testing the LùnPetShop chatbot locally.
Usage: python3 server.py
Then open: http://localhost:8000
"""

import http.server
import socketserver
import os

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"""
╔══════════════════════════════════════════════════════╗
║  🐱 LùnPetShop Chatbot - Local Server Running!      ║
╚══════════════════════════════════════════════════════╝

✅ Server started successfully!

📍 Open in your browser:
   → http://localhost:{PORT}
   → http://127.0.0.1:{PORT}

🔑 Don't forget to:
   1. Get your xAI API key from: https://console.x.ai/
   2. Enter it in the interface when prompted

⚡ Press Ctrl+C to stop the server

""")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped. Goodbye!")
            pass

if __name__ == "__main__":
    main()

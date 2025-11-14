# LùnPetShop KittyCat Chatbot – WordPress Plugin

## Installation
1. Zip this directory (`lunpetshop-chatbot`) or copy it into `wp-content/plugins/`.
2. In the WordPress dashboard go to `Plugins → Add New` and upload the zip, then activate **LùnPetShop KittyCat Chatbot**.

## Configuration
1. Start the FastAPI backend (`python main.py`) and expose it if needed:
   - For a quick demo run `lt --port 8000 --subdomain lunpetshop-chatbot`.
   - Note the public URL (e.g. `https://lunpetshop-chatbot.loca.lt`).
2. In WordPress visit `Settings → KittyCat Chatbot`.
3. Enter the API Base URL (the tunnel or production endpoint) and choose the default language.
4. Save changes.

## Verification Checklist
- Visit the public site and ensure the KittyCat 🐱 button appears in the bottom-right corner.
- Open the widget and confirm the greeting loads without errors.
- Send a test message; the response should come back from the FastAPI service.

If the widget cannot reach the backend, double-check the API URL and that the tunnel/server is running with CORS permitting the WordPress domain.


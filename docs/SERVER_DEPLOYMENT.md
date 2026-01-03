# LunPetShop Server Deployment

## Server Location

- **Server**: hw-asus-zorin (HW's Linux laptop)
- **Path**: `/var/www/lunpetshop/`
- **Port**: 3002
- **URL**: `https://media.bluume.space/lunpetshop`

## Architecture

```
Internet → Cloudflare Tunnel → nginx:8000 → /lunpetshop/* → uvicorn:3002
```

## Nginx Config

Location: `/etc/nginx/sites-available/bluume-media`

```nginx
# Inside server { } block
location /lunpetshop/ {
    proxy_pass http://127.0.0.1:3002/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_read_timeout 120s;
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type" always;
}
```

## Starting the Service

```bash
cd /var/www/lunpetshop
source venv/bin/activate
python main.py
```

The `.env` file should contain:
```
PORT=3002
XAI_API_KEY=your_key
DISCORD_WEBHOOK_URL=optional
WOOCOMMERCE_API_PROXY_URL=https://lunpetshop.com/wp-json/lunpetshop/v1/woocommerce-proxy
```

## TODO: Fix env loading issue

When running with `PORT=3002 python main.py`, the XAI_API_KEY doesn't load.

**Fix**: Add `PORT=3002` to `.env` file so all vars load together:
```bash
echo "PORT=3002" >> /var/www/lunpetshop/.env
python main.py  # No PORT= prefix needed
```

## TODO: Set up as systemd service

For production, create `/etc/systemd/system/lunpetshop.service`:

```ini
[Unit]
Description=LunPetShop Chatbot
After=network.target

[Service]
Type=simple
User=hw
WorkingDirectory=/var/www/lunpetshop
Environment=PATH=/var/www/lunpetshop/venv/bin
ExecStart=/var/www/lunpetshop/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable lunpetshop
sudo systemctl start lunpetshop
```

## Health Check

```bash
# Local
curl http://localhost:3002/health

# Through nginx
curl http://localhost:8000/lunpetshop/health

# External
curl https://media.bluume.space/lunpetshop/health
```

## Updating WordPress Plugin

After server is stable, update the API URL in WordPress:
- Go to: lunpetshop.com → WP Admin → Settings → LunPetShop Chatbot
- Set API Base URL to: `https://media.bluume.space/lunpetshop`

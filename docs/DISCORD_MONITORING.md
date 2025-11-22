# 🔔 Discord Health Monitoring

Automated health monitoring that sends hourly reports to your Discord channel.

## 🎯 Features

- ✅ **Hourly Health Checks** - Automatic health monitoring every hour
- 📊 **Rich Metrics** - Application, system, and service health metrics
- 🚨 **Alert System** - Notifications when service is degraded or unhealthy
- 🎨 **Beautiful Embeds** - Formatted Discord messages with color-coded status
- 🔧 **Configurable** - Easy setup via environment variables

## 🚀 Quick Setup

### Step 1: Create Discord Webhook

1. Go to your Discord server
2. Navigate to **Server Settings** → **Integrations** → **Webhooks**
3. Click **New Webhook**
4. Choose the channel where you want health reports (e.g., `#monitoring`)
5. Copy the **Webhook URL** (looks like: `https://discord.com/api/webhooks/...`)

### Step 2: Configure Environment

Add to your `.env` file (or set as environment variables):

```bash
# Discord Webhook URL (required)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN

# Health check URL (optional, defaults to localhost:8000)
HEALTH_CHECK_URL=http://localhost:8000/health/metrics

# Check interval in seconds (optional, defaults to 3600 = 1 hour)
DISCORD_CHECK_INTERVAL=3600
```

### Step 3: Enable Monitoring

**Option A: Integrated (Recommended)**

The Discord monitor automatically starts with the FastAPI server if `DISCORD_WEBHOOK_URL` is set:

```bash
cd backend
python main.py
```

**Option B: Standalone Script**

Run the monitor as a separate process:

```bash
cd backend
python monitor_health.py
```

This is useful if you want to run monitoring separately from the API server.

## 📊 What Gets Reported

Each health report includes:

### Application Metrics
- **Uptime** - How long the service has been running
- **Total Requests** - Number of requests processed
- **Error Rate** - Percentage of failed requests
- **Average Response Time** - Mean response time in milliseconds
- **Requests per Minute** - Current request rate

### System Metrics
- **CPU Usage** - Process and system CPU percentage
- **Memory Usage** - Memory consumption (MB and percentage)
- **Disk Usage** - Disk space usage percentage

### Service Health
- **xAI API Status** - Whether the API key is configured
- **Overall Status** - `healthy`, `degraded`, or `unhealthy`

## 🎨 Example Discord Message

The health reports appear as rich embeds in Discord:

```
✅ LùnPetShop Chatbot Health Report
Status: HEALTHY

📊 Application Metrics
Uptime: 2:15:30
Total Requests: 1,234
Error Rate: 0.50%
Avg Response: 245.3ms
Requests/min: 9.2

💻 System Metrics
CPU: 12.5%
Memory: 125.3MB (2.1%)
Disk: 45.2% used

🔧 Services
xAI API: ✅ Configured
```

## 🚨 Alert Levels

- **✅ Healthy** (Green) - Service is operating normally
- **⚠️ Degraded** (Yellow) - Service has issues but is still functional
  - Error rate > 10%
  - xAI API not configured (but rule-based responses work)
- **❌ Unhealthy** (Red) - Service is down or critically failing
  - Error rate > 50%
  - Health check endpoint unreachable

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DISCORD_WEBHOOK_URL` | Discord webhook URL | - | ✅ Yes |
| `HEALTH_CHECK_URL` | Health metrics endpoint | `http://localhost:8000/health/metrics` | No |
| `DISCORD_CHECK_INTERVAL` | Check interval in seconds | `3600` (1 hour) | No |

### Custom Check Intervals

To check more frequently (e.g., every 15 minutes):

```bash
DISCORD_CHECK_INTERVAL=900  # 15 minutes
```

To check less frequently (e.g., every 6 hours):

```bash
DISCORD_CHECK_INTERVAL=21600  # 6 hours
```

## 🐛 Troubleshooting

### Monitor Not Starting

**Check webhook URL:**
```bash
echo $DISCORD_WEBHOOK_URL
```

**Verify health endpoint is accessible:**
```bash
curl http://localhost:8000/health/metrics
```

### No Messages in Discord

1. **Check webhook URL** - Make sure it's correct and not expired
2. **Check Discord permissions** - Webhook needs permission to post in the channel
3. **Check logs** - Look for error messages in console/logs
4. **Test manually** - Run a manual health check:
   ```python
   from src.discord_monitor import DiscordHealthMonitor
   import asyncio
   
   monitor = DiscordHealthMonitor()
   asyncio.run(monitor.send_report())
   ```

### Service Shows as Unhealthy

- Check if the API server is running
- Verify the health endpoint is accessible
- Check error logs for issues
- Verify network connectivity

## 🔐 Security Notes

- **Never commit webhook URLs** to version control
- Use environment variables or secure secret management
- Webhook URLs can be revoked and regenerated in Discord
- Consider using different webhooks for dev/staging/prod

## 📝 Production Deployment

For production, you can:

1. **Run as integrated service** (monitoring starts with API)
2. **Run as separate process** (more resilient, survives API restarts)
3. **Use systemd/cron** to ensure it stays running:
   ```bash
   # systemd service example
   [Service]
   ExecStart=/usr/bin/python3 /path/to/backend/monitor_health.py
   Restart=always
   ```

## 🎯 Use Cases

- **Production Monitoring** - Get notified when production service goes down
- **Team Alerts** - Keep your team informed about service health
- **Historical Tracking** - Review Discord history for service uptime patterns
- **Quick Diagnostics** - See at a glance if service needs attention

---

**Need Help?** Check the main [README.md](../README.md) or [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md)


"""Discord health monitoring service for LùnPetShop chatbot."""

import os
import asyncio
import httpx
from datetime import datetime
from typing import Optional, Dict, Any
import json


class DiscordHealthMonitor:
    """Monitors health and reports to Discord via webhook."""
    
    def __init__(self, webhook_url: Optional[str] = None, health_url: Optional[str] = None):
        """
        Initialize Discord health monitor.
        
        Args:
            webhook_url: Discord webhook URL (or from DISCORD_WEBHOOK_URL env var)
            health_url: Health metrics endpoint URL (defaults to localhost:8000)
        """
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
        self.health_url = health_url or os.getenv("HEALTH_CHECK_URL", "http://localhost:8000/health/metrics")
        self.enabled = bool(self.webhook_url)
        
        if not self.enabled:
            print("⚠️  Discord monitoring disabled: DISCORD_WEBHOOK_URL not set")
    
    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for health status."""
        status_map = {
            "healthy": "✅",
            "degraded": "⚠️",
            "unhealthy": "❌",
        }
        return status_map.get(status, "❓")
    
    def _format_metrics_message(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Format health metrics as Discord embed."""
        status = metrics.get("status", "unknown")
        emoji = self._get_status_emoji(status)
        
        app_stats = metrics.get("application", {})
        system_metrics = metrics.get("system", {})
        services = metrics.get("services", {})
        endpoints = metrics.get("endpoints", {})
        
        # Build embed
        embed = {
            "title": f"{emoji} LùnPetShop Chatbot Health Report",
            "description": f"**Status:** {status.upper()}",
            "color": 0x00ff00 if status == "healthy" else (0xffaa00 if status == "degraded" else 0xff0000),
            "timestamp": datetime.utcnow().isoformat(),
            "fields": []
        }
        
        # Application metrics
        if app_stats:
            uptime = app_stats.get("uptime_formatted", "N/A")
            total_requests = app_stats.get("total_requests", 0)
            error_rate = app_stats.get("error_rate", 0) * 100
            avg_response = app_stats.get("avg_response_time_ms", 0)
            rpm = app_stats.get("requests_per_minute", 0)
            
            embed["fields"].extend([
                {
                    "name": "📊 Application Metrics",
                    "value": (
                        f"**Uptime:** {uptime}\n"
                        f"**Total Requests:** {total_requests:,}\n"
                        f"**Error Rate:** {error_rate:.2f}%\n"
                        f"**Avg Response:** {avg_response:.1f}ms\n"
                        f"**Requests/min:** {rpm:.1f}"
                    ),
                    "inline": False
                }
            ])
        
        # System metrics
        if system_metrics.get("available"):
            process = system_metrics.get("process", {})
            system = system_metrics.get("system", {})
            
            cpu = process.get("cpu_percent", 0)
            memory_mb = process.get("memory_mb", 0)
            memory_percent = process.get("memory_percent", 0)
            disk_percent = system.get("disk_percent", 0)
            
            embed["fields"].append({
                "name": "💻 System Metrics",
                "value": (
                    f"**CPU:** {cpu}%\n"
                    f"**Memory:** {memory_mb:.1f}MB ({memory_percent:.1f}%)\n"
                    f"**Disk:** {disk_percent:.1f}% used"
                ),
                "inline": False
            })
        
        # Service health
        if services:
            xai_status = services.get("xai_api", {})
            xai_configured = xai_status.get("configured", False)
            xai_status_text = "✅ Configured" if xai_configured else "⚠️ Not Configured"
            
            service_text = f"**xAI API:** {xai_status_text}"
            
            # Add tunnel status
            tunnel_info = services.get("tunnel", {})
            if tunnel_info:
                tunnel_status = tunnel_info.get("status", "unknown")
                tunnel_emoji = "✅" if tunnel_status == "healthy" else ("⚠️" if tunnel_status == "degraded" else "❌")
                tunnel_url = tunnel_info.get("url", "N/A")
                if tunnel_url != "N/A" and len(tunnel_url) > 40:
                    tunnel_url = tunnel_url[:37] + "..."
                service_text += f"\n**Tunnel:** {tunnel_emoji} {tunnel_status.title()}"
                if tunnel_status != "healthy" and tunnel_info.get("error"):
                    service_text += f"\n_Error: {tunnel_info.get('error', 'Unknown')[:50]}..._"
            
            # Add endpoint test results
            if endpoints:
                chat_test = endpoints.get("chat", {})
                chat_status = chat_test.get("status", "unknown")
                chat_emoji = "✅" if chat_status == "healthy" else ("⚠️" if chat_status == "degraded" else "❌")
                service_text += f"\n**Chat Endpoint:** {chat_emoji} {chat_status.title()}"
                
                if not chat_test.get("test_passed", True) and chat_test.get("error"):
                    service_text += f"\n_Error: {chat_test.get('error', 'Unknown')[:50]}..._"
            
            embed["fields"].append({
                "name": "🔧 Services & Endpoints",
                "value": service_text,
                "inline": False
            })
        
        # Alert if unhealthy
        if status != "healthy":
            alert_msg = "⚠️ **ALERT:** Service is experiencing issues!"
            if status == "unhealthy":
                alert_msg = "🚨 **CRITICAL:** Service is unhealthy!"
            embed["fields"].append({
                "name": "🚨 Alert",
                "value": alert_msg,
                "inline": False
            })
        
        return {
            "embeds": [embed]
        }
    
    async def check_health(self) -> Optional[Dict[str, Any]]:
        """Check health metrics from the API."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.health_url)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            return {
                "status": "unhealthy",
                "error": "Health check timeout - service may be down"
            }
        except httpx.RequestError as e:
            return {
                "status": "unhealthy",
                "error": f"Health check failed: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def send_report(self, metrics: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send health report to Discord.
        
        Args:
            metrics: Optional pre-fetched metrics. If None, will fetch them.
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        # Fetch metrics if not provided
        if metrics is None:
            metrics = await self.check_health()
        
        if not metrics:
            return False
        
        # Format message
        if "error" in metrics:
            # Error case - service is down
            message = {
                "embeds": [{
                    "title": "❌ LùnPetShop Chatbot Health Check Failed",
                    "description": f"**Error:** {metrics.get('error', 'Unknown error')}",
                    "color": 0xff0000,
                    "timestamp": datetime.utcnow().isoformat(),
                    "fields": [{
                        "name": "🔗 Health URL",
                        "value": self.health_url,
                        "inline": False
                    }]
                }]
            }
        else:
            message = self._format_metrics_message(metrics)
        
        # Send to Discord
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.webhook_url,
                    json=message,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return True
        except Exception as e:
            print(f"❌ Failed to send Discord notification: {e}")
            return False
    
    async def start_monitoring(self, interval_seconds: int = 3600):
        """
        Start periodic health monitoring.
        
        Args:
            interval_seconds: Check interval in seconds (default: 3600 = 1 hour)
        """
        if not self.enabled:
            print("⚠️  Discord monitoring disabled. Set DISCORD_WEBHOOK_URL to enable.")
            return
        
        print(f"🔔 Starting Discord health monitoring (every {interval_seconds}s)")
        print(f"📊 Health URL: {self.health_url}")
        
        while True:
            try:
                print(f"🔍 Checking health at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                metrics = await self.check_health()
                success = await self.send_report(metrics)
                
                if success:
                    print("✅ Health report sent to Discord")
                else:
                    print("❌ Failed to send health report")
                
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
            
            await asyncio.sleep(interval_seconds)


async def main():
    """Main entry point for standalone monitoring."""
    monitor = DiscordHealthMonitor()
    
    # Get interval from env (default 1 hour)
    interval = int(os.getenv("DISCORD_CHECK_INTERVAL", "3600"))
    
    await monitor.start_monitoring(interval_seconds=interval)


if __name__ == "__main__":
    asyncio.run(main())


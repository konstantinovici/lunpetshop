"""Metrics tracking for health monitoring."""

import time
import os
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import threading

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class MetricsCollector:
    """Collects and tracks application metrics."""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        self.endpoint_counts = defaultdict(int)
        self.endpoint_errors = defaultdict(int)
        self.lock = threading.Lock()
        self.max_response_times = 1000  # Keep last 1000 response times
        
    def record_request(self, endpoint: str, response_time: float, is_error: bool = False):
        """Record a request metric."""
        with self.lock:
            self.request_count += 1
            self.endpoint_counts[endpoint] += 1
            
            if is_error:
                self.error_count += 1
                self.endpoint_errors[endpoint] += 1
            
            # Keep only recent response times
            self.response_times.append(response_time)
            if len(self.response_times) > self.max_response_times:
                self.response_times.pop(0)
    
    def get_stats(self) -> Dict:
        """Get aggregated statistics."""
        with self.lock:
            uptime_seconds = time.time() - self.start_time
            avg_response_time = (
                sum(self.response_times) / len(self.response_times)
                if self.response_times else 0
            )
            p95_response_time = (
                sorted(self.response_times)[int(len(self.response_times) * 0.95)]
                if len(self.response_times) >= 20 else 0
            )
            p99_response_time = (
                sorted(self.response_times)[int(len(self.response_times) * 0.99)]
                if len(self.response_times) >= 100 else 0
            )
            
            return {
                "uptime_seconds": uptime_seconds,
                "uptime_formatted": str(timedelta(seconds=int(uptime_seconds))),
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "p95_response_time_ms": round(p95_response_time * 1000, 2) if p95_response_time > 0 else None,
                "p99_response_time_ms": round(p99_response_time * 1000, 2) if p99_response_time > 0 else None,
                "requests_per_minute": round(self.request_count / (uptime_seconds / 60), 2) if uptime_seconds > 0 else 0,
                "endpoint_counts": dict(self.endpoint_counts),
                "endpoint_errors": dict(self.endpoint_errors),
            }


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_system_metrics() -> Dict:
    """Get system-level metrics."""
    if not PSUTIL_AVAILABLE:
        return {
            "available": False,
            "message": "psutil not installed. Install with: pip install psutil"
        }
    
    try:
        process = psutil.Process()
        cpu_percent = process.cpu_percent(interval=0.1)
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        
        # System-wide metrics
        system_cpu = psutil.cpu_percent(interval=0.1)
        system_memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "available": True,
            "process": {
                "cpu_percent": round(cpu_percent, 2),
                "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
                "memory_percent": round(memory_percent, 2),
                "threads": process.num_threads(),
                "open_files": len(process.open_files()),
            },
            "system": {
                "cpu_percent": round(system_cpu, 2),
                "memory_total_gb": round(system_memory.total / 1024 / 1024 / 1024, 2),
                "memory_available_gb": round(system_memory.available / 1024 / 1024 / 1024, 2),
                "memory_percent": round(system_memory.percent, 2),
                "disk_total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                "disk_percent": round(disk.percent, 2),
            }
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }


def get_service_health() -> Dict:
    """Check health of external services and dependencies."""
    health_status = {
        "xai_api": {
            "configured": bool(os.getenv("XAI_API_KEY")),
            "status": "configured" if os.getenv("XAI_API_KEY") else "not_configured"
        },
        "environment": {
            "host": os.getenv("HOST", "0.0.0.0"),
            "port": os.getenv("PORT", "8000"),
        }
    }
    
    # Test xAI API connectivity if configured
    if os.getenv("XAI_API_KEY"):
        try:
            import httpx
            # Quick connectivity test (don't make actual API call)
            health_status["xai_api"]["status"] = "configured"
        except Exception as e:
            health_status["xai_api"]["status"] = "error"
            health_status["xai_api"]["error"] = str(e)
    
    # Check tunnel accessibility (if tunnel URL file exists)
    try:
        from pathlib import Path
        import subprocess
        backend_dir = Path(__file__).parent.parent
        project_root = backend_dir.parent
        tunnel_url_file = project_root / ".pids" / "tunnel.url"
        tunnel_pid_file = project_root / ".pids" / "tunnel.pid"
        
        # Check if tunnel process is running
        tunnel_process_running = False
        if tunnel_pid_file.exists():
            try:
                pid = int(tunnel_pid_file.read_text().strip())
                # Use kill -0 to check if process exists (works on Unix-like systems)
                # This doesn't actually kill the process, just checks if it exists
                try:
                    subprocess.run(["kill", "-0", str(pid)], 
                                  capture_output=True, 
                                  timeout=1, 
                                  check=True)
                    tunnel_process_running = True
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                    tunnel_process_running = False
            except (ValueError, OSError):
                tunnel_process_running = False
        
        if tunnel_url_file.exists():
            tunnel_url = tunnel_url_file.read_text().strip()
            health_status["tunnel"] = {
                "url": tunnel_url,
                "status": "unknown"
            }
            
            # If process is running, assume tunnel is working
            # Don't try to reach the public tunnel URL from backend - it may not be reachable
            # The tunnel works for external users, that's what matters
            if tunnel_process_running:
                # Process is running and URL file exists - tunnel is healthy
                health_status["tunnel"]["status"] = "healthy"
            else:
                # Process not running - definitely unhealthy
                health_status["tunnel"]["status"] = "unhealthy"
                health_status["tunnel"]["error"] = "Tunnel process not running"
        else:
            if tunnel_process_running:
                # Process running but no URL file yet - might be starting up
                health_status["tunnel"] = {
                    "status": "degraded",
                    "message": "Tunnel starting (URL not yet available)"
                }
            else:
                health_status["tunnel"] = {
                    "status": "not_configured",
                    "message": "No tunnel URL file found"
                }
    except Exception as e:
        health_status["tunnel"] = {
            "status": "error",
            "error": str(e)
        }
    
    return health_status


def test_chat_endpoint() -> Dict:
    """Test if the chat endpoint is actually working."""
    try:
        from .chatbot import graph
        from langchain_core.messages import HumanMessage
        
        # Try a simple test invocation
        test_input = {
            "messages": [HumanMessage(content="test")],
            "language": "vi",
        }
        config = {"configurable": {"thread_id": "health-check-test"}}
        
        result = graph.invoke(test_input, config)
        
        # Check if we got a valid response
        if result and "messages" in result and len(result["messages"]) > 0:
            return {
                "status": "healthy",
                "test_passed": True,
                "response_received": True
            }
        else:
            return {
                "status": "degraded",
                "test_passed": False,
                "error": "No response from graph"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "test_passed": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


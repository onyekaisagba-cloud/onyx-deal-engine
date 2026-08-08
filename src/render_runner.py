"""
Onyx Deal Engine - Resilient Render Web & Background Scheduler
File: src/render_runner.py
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import os
import subprocess
import sys
import threading
import time

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("RenderRunner")

INTERVAL_SECONDS = 21600  # 6 Hours


def execute_pipeline_job():
    """Runs the main pipeline module in an isolated subprocess to prevent thread crashes."""
    logger.info("Triggering scheduled pipeline execution via subprocess...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "src.main"],
            capture_output=True,
            text=True,
            timeout=300,  # 5-minute hard timeout per run
        )
        if result.returncode == 0:
            logger.info("Pipeline execution completed successfully.")
            if result.stdout:
                logger.info(f"Pipeline stdout: {result.stdout.strip()[-300:]}")
        else:
            logger.error(
                f"Pipeline subprocess failed with return code {result.returncode}."
            )
            if result.stderr:
                logger.error(f"Pipeline stderr: {result.stderr.strip()[-300:]}")
    except subprocess.TimeoutExpired:
        logger.error("Pipeline subprocess timed out after 300 seconds.")
    except Exception as e:
        logger.error(f"Unexpected error executing pipeline subprocess: {e}")


def run_resilient_scheduler():
    """Infinite resilient loop that runs immediately on boot and retries every 6 hours."""
    logger.info("Starting background scheduler loop...")
    
    # Run immediately on service startup
    execute_pipeline_job()

    while True:
        try:
            logger.info(
                f"Scheduler sleeping for {INTERVAL_SECONDS // 3600} hours until next run..."
            )
            time.sleep(INTERVAL_SECONDS)
            execute_pipeline_job()
        except Exception as err:
            logger.error(f"Scheduler loop encountered critical error: {err}. Recovering in 60s...")
            time.sleep(60)


class HealthCheckHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        req_path = self.path.split("?")[0].lstrip("/")

        # 1. Sitemap Endpoint
        if req_path == "sitemap.xml":
            if os.path.exists("sitemap.xml"):
                self.send_response(200)
                self.send_header("Content-type", "application/xml; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                with open("sitemap.xml", "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return

        # 2. Privacy Policy Endpoint
        if req_path == "privacy.html":
            if os.path.exists("privacy.html"):
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                with open("privacy.html", "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return

        # 3. Static File Server (index.html or /deals/*.html)
        target_file = req_path if req_path and os.path.exists(req_path) else "index.html"

        if os.path.exists(target_file) and os.path.isfile(target_file):
            content_type = "text/html; charset=utf-8"
            if target_file.endswith(".xml"):
                content_type = "application/xml; charset=utf-8"
            elif target_file.endswith(".css"):
                content_type = "text/css; charset=utf-8"

            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.end_headers()
            with open(target_file, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_HEAD(self):
        req_path = self.path.split("?")[0].lstrip("/")
        self.send_response(200)
        if req_path == "sitemap.xml":
            self.send_header("Content-type", "application/xml; charset=utf-8")
        else:
            self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()


def start_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info(f"Health check & static web server listening on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    # Start resilient scheduler in background thread
    scheduler_thread = threading.Thread(
        target=run_resilient_scheduler, daemon=True
    )
    scheduler_thread.start()

    # Serve static assets and keep Render web instance alive
    start_health_server()

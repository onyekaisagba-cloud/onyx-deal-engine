"""
Onyx Deal Engine - Render Continuous Runner
File: src/render_runner.py
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import os
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RenderRunner")


def run_pipeline_loop():
    """Runs the main pipeline every 12 hours (43,200 seconds)."""
    while True:
        logger.info("Starting scheduled deal engine pipeline run...")
        try:
            os.system("python -m src.main")
            logger.info("Pipeline run completed successfully.")
        except Exception as e:
            logger.error(f"Error executing pipeline: {e}")

        # Sleep for 12 hours before next run
        time.sleep(43200)


class HealthCheckHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        req_path = self.path.lstrip("/")

        # 1. Serve sitemap.xml
        if req_path == "sitemap.xml":
            if os.path.exists("sitemap.xml"):
                self.send_response(200)
                self.send_header("Content-type", "application/xml; charset=utf-8")
                self.end_headers()
                with open("sitemap.xml", "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return

        # 2. Serve static files (root index or /deals/*.html)
        target_file = req_path if req_path and os.path.exists(req_path) else "index.html"

        if os.path.exists(target_file) and os.path.isfile(target_file):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            with open(target_file, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()


def start_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info(f"Health check server listening on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    # Start 12-hour background loop thread
    pipeline_thread = threading.Thread(target=run_pipeline_loop, daemon=True)
    pipeline_thread.start()

    # Keep Render Web Service alive via HTTP health server
    start_health_server()

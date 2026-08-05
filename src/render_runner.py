"""
Onyx Deal Engine - Render Continuous Runner & Web Server
File: src/render_runner.py
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import os
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RenderRunner")


def run_pipeline():
    """Executes the core main pipeline script."""
    logger.info("Executing deal engine pipeline run...")
    try:
        os.system("python -m src.main")
        logger.info("Pipeline run completed successfully.")
    except Exception as e:
        logger.error(f"Error executing pipeline: {e}")


def run_pipeline_loop():
    """Background scheduler running the pipeline every 6 hours (21,600 seconds)."""
    while True:
        # Sleep for 6 hours between automated scheduled runs
        time.sleep(21600)
        run_pipeline()


class HealthCheckHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Normalize request path to strip leading slash and query params
        req_path = self.path.split("?")[0].lstrip("/")

        # 1. Explicit Sitemap Endpoint
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
                self.wfile.write(b"Sitemap building in progress...")
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

        # 3. Static File & Sub-Page Server (Root Index or /deals/*.html)
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
        if req_path == "sitemap.xml" and not os.path.exists("sitemap.xml"):
            self.send_response(404)
        else:
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
    # Synchronous initial run to ensure sitemap.xml exists immediately on boot
    logger.info("Executing boot pipeline run to ensure static assets & sitemap are ready...")
    run_pipeline()

    # Start automated 6-hour interval loop in background
    pipeline_thread = threading.Thread(target=run_pipeline_loop, daemon=True)
    pipeline_thread.start()

    # Serve static assets & HTTP endpoints for Render and Search Console
    start_health_server()

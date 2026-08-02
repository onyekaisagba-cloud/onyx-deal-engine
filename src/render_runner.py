import time
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RenderRunner")

def run_pipeline_loop():
    """Runs the main pipeline every 12 hours (43,200 seconds)."""
    while True:
        logger.info("Starting scheduled deal engine pipeline run...")
        try:
            # Trigger main deal engine workflow
            os.system("python -m src.main")
            logger.info("Pipeline run completed successfully.")
        except Exception as e:
            logger.error(f"Error executing pipeline: {e}")
        
        # Sleep for 12 hours before next run
        time.sleep(43200)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Onyx Deal Engine Runner Active")

def start_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

if __name__ == "__main__":
    # Start the 12-hour background loop thread
    pipeline_thread = threading.Thread(target=run_pipeline_loop, daemon=True)
    pipeline_thread.start()
    
    # Keep the Render Web Service active via HTTP health server
    start_health_server()

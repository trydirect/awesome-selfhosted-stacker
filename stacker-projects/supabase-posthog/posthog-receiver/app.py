"""Minimal PostHog-compatible event receiver using only the Python standard library.

Implements the small subset of the PostHog API that a Stacker pipe demo needs:
  - GET  /                -> status page
  - POST /capture         -> accept an event and return {"status": "ok"}
  - GET  /decide          -> return empty feature flags
  - GET  /static/array.js -> empty JS stub
  - GET  /health          -> health check
"""

import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("posthog-receiver")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        logger.info("%s - %s", self.address_string(), fmt % args)

    def _send(self, status, body=None, content_type="text/plain"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        if body is not None:
            self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body is not None:
            self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            body = b"<h1>PostHog-compatible event receiver</h1><p>Send capture events to POST /capture</p>"
            self._send(200, body, "text/html")
        elif self.path == "/decide":
            body = json.dumps({"featureFlags": {}, "errorsWhileComputingFlags": False, "isAuthenticated": False}).encode()
            self._send(200, body, "application/json")
        elif self.path == "/static/array.js":
            body = b"/* minimal PostHog JS stub */"
            self._send(200, body, "application/javascript")
        elif self.path == "/health":
            body = json.dumps({"status": "healthy"}).encode()
            self._send(200, body, "application/json")
        else:
            self._send(404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == "/capture":
            length = int(self.headers.get("Content-Length", 0))
            payload = self.rfile.read(length) if length else b"{}"
            try:
                event = json.loads(payload)
            except json.JSONDecodeError:
                event = {"raw": payload.decode("utf-8", errors="replace")}
            logger.info("Received capture event: %s", json.dumps(event, default=str))
            body = json.dumps({"status": "ok"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
        else:
            self._send(404)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8000), Handler)
    logger.info("PostHog-compatible receiver listening on http://0.0.0.0:8000")
    server.serve_forever()

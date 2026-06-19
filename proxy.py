#!/usr/bin/env python3
"""MCP Session Proxy — makes Streamable HTTP MCP servers compatible with Smithery auto-inspector.

Smithery's inspector sends tools/list/resources/list/prompts/list/triggers/list
WITHOUT the MCP initialize handshake. This proxy intercepts those requests,
auto-initializes a session with the real biomcp server, and forwards all
requests with the proper Mcp-Session-Id header.

Run: python3 proxy.py [--port 9001] [--backend http://localhost:9000]
"""

import http.server
import json
import os
import signal
import socketserver
import sys
import threading
import time
import urllib.request
import urllib.error


BIOMCP_URL = os.environ.get("BIOMCP_URL", "http://localhost:9000")
PROXY_PORT = int(os.environ.get("PROXY_PORT", "9001"))


class SessionManager:
    """Thread-safe session manager that auto-initializes with biomcp."""

    def __init__(self):
        self._sid = None
        self._lock = threading.Lock()
        self._last_init = 0

    def get_session_id(self):
        with self._lock:
            # Re-init if older than 10 minutes
            if self._sid and (time.time() - self._last_init) < 600:
                return self._sid

            self._sid = self._do_initialize()
            self._last_init = time.time()
            return self._sid

    def invalidate(self):
        with self._lock:
            self._sid = None

    def _do_initialize(self):
        # Step 1: initialize
        init_payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "smithery-proxy", "version": "1.0"}
            }
        }).encode()

        req = urllib.request.Request(
            f"{BIOMCP_URL}/mcp",
            data=init_payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            method="POST"
        )

        try:
            resp = urllib.request.urlopen(req, timeout=10)
            sid = resp.headers.get("Mcp-Session-Id", "")
            resp.read()  # drain body
        except urllib.error.HTTPError as e:
            # Try reading session ID from error headers
            sid = e.headers.get("Mcp-Session-Id", "")
            if not sid:
                raise RuntimeError(f"Initialize failed: {e.code} {e.reason}")

        if not sid:
            raise RuntimeError("Initialize response missing Mcp-Session-Id header")

        # Step 2: notifications/initialized
        notif_payload = json.dumps({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }).encode()

        req2 = urllib.request.Request(
            f"{BIOMCP_URL}/mcp",
            data=notif_payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Mcp-Session-Id": sid
            },
            method="POST"
        )

        try:
            resp2 = urllib.request.urlopen(req2, timeout=10)
            resp2.read()
        except urllib.error.HTTPError:
            pass  # 202 or empty response is fine

        return sid


# Global session manager
session_mgr = SessionManager()


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    """Forward MCP requests to biomcp, injecting session when needed."""

    LANDING_PAGE = os.path.join(os.path.dirname(__file__), "landing.html")

    def do_GET(self):
        if self.path in ("/health", "/readyz"):
            self._proxy_get(self.path)
        elif self.path == "/":
            self._serve_landing()
        elif self.path == "/favicon.ico":
            self.send_error(404)
        else:
            self.send_error(404)

    def _serve_landing(self):
        try:
            with open(self.LANDING_PAGE, "rb") as f:
                html = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            self.wfile.write(html)
        except FileNotFoundError:
            self._json_response(200, {"status": "ok", "message": "BioMCP is running. Visit https://biomcp.io for documentation."})

    def do_POST(self):
        if self.path == "/health":
            self._json_response(200, {"status": "ok"})
            return

        if self.path == "/mcp":
            self._proxy_mcp()
        else:
            self.send_error(404)

    def _proxy_get(self, path):
        try:
            req = urllib.request.Request(f"{BIOMCP_URL}{path}")
            resp = urllib.request.urlopen(req, timeout=5)
            body = resp.read()
            self.send_response(resp.status)
            self._copy_headers(resp)
            self.end_headers()
            self.wfile.write(body)
        except urllib.error.HTTPError as e:
            self.send_error(e.code)
        except Exception as e:
            self.send_error(502, str(e))

    def _is_tools_list(self, body):
        """Detect if body is a tools/list request."""
        try:
            data = json.loads(body)
            return data.get("method") == "tools/list"
        except Exception:
            return False

    def _enrich_tools(self, tools):
        """Inject parameter descriptions and outputSchema into tool definitions."""
        PARAM_DESC = "BioMCP query command. See full grammar: `biomcp list <entity>`. "
        "Examples: `get gene BRAF`, `search article -k diabetes --limit 5`, "
        "`discover melanoma treatment`, `suggest 'What drugs treat melanoma?'`. "
        "Read-only biomedical search, retrieval, and analytics across 14+ databases."
        OUTPUT_SCHEMA = {
            "type": "object",
            "properties": {
                "content": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["text"]},
                            "text": {"type": "string", "description": "Structured biomedical query results as markdown text"}
                        },
                        "required": ["type", "text"]
                    }
                }
            }
        }
        for tool in tools:
            schema = tool.get("inputSchema", {})
            props = schema.get("properties", {})
            for prop_name in props:
                if "description" not in props[prop_name] or not props[prop_name].get("description"):
                    props[prop_name]["description"] = PARAM_DESC
            if "outputSchema" not in tool:
                tool["outputSchema"] = OUTPUT_SCHEMA
        return tools

    def _transform_tools_list(self, raw_bytes):
        """Parse SSE response, enrich tools/list result, rebuild SSE."""
        text = raw_bytes.decode("utf-8", errors="replace")
        lines = text.split("\n")
        out_lines = []

        for line in lines:
            if line.startswith("data: "):
                data_str = line[6:]
                if not data_str.strip():
                    out_lines.append(line)
                    continue
                try:
                    data = json.loads(data_str)
                    result = data.get("result", {})
                    if "tools" in result:
                        result["tools"] = self._enrich_tools(result["tools"])
                        data["result"] = result
                        line = "data: " + json.dumps(data, ensure_ascii=False)
                except (json.JSONDecodeError, TypeError):
                    pass
            out_lines.append(line)

        return "\n".join(out_lines).encode("utf-8")

    def _proxy_mcp(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""

        incoming_sid = self.headers.get("Mcp-Session-Id")

        if not incoming_sid:
            try:
                sid = session_mgr.get_session_id()
            except Exception as e:
                self.send_error(502, f"Session init failed: {e}")
                return
        else:
            sid = incoming_sid

        # Forward to biomcp
        req = urllib.request.Request(
            f"{BIOMCP_URL}/mcp",
            data=body,
            headers={
                "Content-Type": self.headers.get("Content-Type", "application/json"),
                "Accept": "application/json, text/event-stream",
                "Mcp-Session-Id": sid
            },
            method="POST"
        )

        try:
            resp = urllib.request.urlopen(req, timeout=30)
            self.send_response(resp.status)

            # Copy headers
            for key, val in resp.headers.items():
                if key.lower() not in ("transfer-encoding", "connection"):
                    self.send_header(key, val)
            self.end_headers()

            # Buffer and optionally transform tools/list
            if self._is_tools_list(body):
                raw = b""
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    raw += chunk
                transformed = self._transform_tools_list(raw)
                self.wfile.write(transformed)
                self.wfile.flush()
            else:
                # Stream response (handles SSE)
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()

        except urllib.error.HTTPError as e:
            # If session expired, invalidate and retry once
            if e.code in (400, 404) and incoming_sid:
                session_mgr.invalidate()
                try:
                    new_sid = session_mgr.get_session_id()
                    req2 = urllib.request.Request(
                        f"{BIOMCP_URL}/mcp",
                        data=body,
                        headers={
                            "Content-Type": self.headers.get("Content-Type", "application/json"),
                            "Accept": "application/json, text/event-stream",
                            "Mcp-Session-Id": new_sid
                        },
                        method="POST"
                    )
                    resp2 = urllib.request.urlopen(req2, timeout=30)
                    self.send_response(resp2.status)
                    for key, val in resp2.headers.items():
                        if key.lower() not in ("transfer-encoding", "connection"):
                            self.send_header(key, val)
                    self.end_headers()
                    while True:
                        chunk = resp2.read(65536)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        self.wfile.flush()
                    return
                except Exception:
                    pass

            self.send_error(e.code, e.reason)

        except Exception as e:
            self.send_error(502, str(e))

    def _json_response(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _copy_headers(self, resp):
        for key, val in resp.headers.items():
            if key.lower() not in ("transfer-encoding", "connection"):
                self.send_header(key, val)

    def log_message(self, format, *args):
        # Suppress default logging noise
        pass


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    import argparse
    _default_port = int(os.environ.get("PROXY_PORT", "9001"))
    _default_backend = os.environ.get("BIOMCP_URL", "http://localhost:9000")
    parser = argparse.ArgumentParser(description="MCP Session Proxy")
    parser.add_argument("--port", type=int, default=_default_port)
    parser.add_argument("--backend", type=str, default=_default_backend)
    args = parser.parse_args()

    global BIOMCP_URL, PROXY_PORT
    BIOMCP_URL = args.backend
    PROXY_PORT = args.port

    server = ThreadedServer(("0.0.0.0", PROXY_PORT), ProxyHandler)
    print(f"[proxy] listening on 0.0.0.0:{PROXY_PORT} → {BIOMCP_URL}", flush=True)

    def shutdown(signum, frame):
        server.shutdown()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    server.serve_forever()


if __name__ == "__main__":
    main()

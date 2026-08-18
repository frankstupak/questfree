#!/usr/bin/env python3
"""
Quest 1 NUX Spoof Server
Intercepts and satisfies the calls Quest 1 makes during NUX/setup
so the device completes pairing with WAN fully dark.

Endpoints (from DeviceAuth.java + DeviceChallenge.java, firmware 2026-08-18):
  POST /ota_request                  -> {challenge}
  POST /login_request                -> {challenge, signature_algorithm}
  POST /register                     -> {}
  POST /remote_provisioning_register -> {device_identity_cert_pkg}
  GET  /mobile/status.php            -> "true"
  POST /graphql                      -> {data:{}} (logged for analysis)

No cert pinning found in DeviceAuth/OCMS. Self-signed cert works.
Generate: openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem \
          -days 365 -nodes -subj "/CN=graph.facebook-hardware.com"
"""

import ssl, json, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

LOG = []


class QuestSpoofHandler(BaseHTTPRequestHandler):

    def log_and_read(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        entry = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "method": self.command,
            "host": self.headers.get("Host", ""),
            "path": self.path,
            "body_raw": body.decode("utf-8", "replace") if body else None,
        }
        try:
            entry["body_json"] = json.loads(body) if body else None
        except Exception:
            entry["body_json"] = None
        LOG.append(entry)
        print(f"[spoof] {self.command} {entry['host']}{self.path}")
        if body:
            print(f"        {body[:300].decode('utf-8','replace')}")
        return body

    def send_json(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data)
        if LOG:
            LOG[-1]["response"] = obj

    def send_text(self, body=b"true"):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.log_and_read()
        if "status.php" in self.path:
            self.send_text(b"true")
        else:
            self.send_json(200, {"data": {}})

    def do_POST(self):
        self.log_and_read()
        path = self.path
        if "/ota_request" in path:
            self.send_json(200, {"challenge": "QUESTFREE_OTA_CHALLENGE"})
        elif "/login_request" in path:
            self.send_json(200, {"challenge": "QUESTFREE_CHALLENGE", "signature_algorithm": "sha256WithRSAEncryption"})
        elif "/remote_provisioning_register" in path:
            self.send_json(200, {"device_identity_cert_pkg": ""})
        elif "/register" in path:
            self.send_json(200, {})
        elif "/login" in path:
            # Signed challenge response — KEY UNKNOWN until first live capture
            self.send_json(200, {"access_token": "QUESTFREE_TOKEN", "device_ent_id": "QUESTFREE_ENT", "session_ttl": 86400})
        else:
            self.send_json(200, {"data": {}})

    def log_message(self, fmt, *args):
        pass


def save_log(path: str):
    with open(path, "w") as f:
        json.dump(LOG, f, indent=2)
    print(f"[spoof] Saved {len(LOG)} requests -> {path}")


def run(host="0.0.0.0", port=8443, certfile=None, keyfile=None, log_file=None):
    base = os.path.dirname(__file__)
    certfile = certfile or os.path.join(base, "..", "cert.pem")
    keyfile  = keyfile  or os.path.join(base, "..", "key.pem")

    if not os.path.exists(certfile):
        print(f"[spoof] cert not found: {certfile}")
        print("Generate with:")
        print(f"  openssl req -x509 -newkey rsa:2048 -keyout {keyfile} -out {certfile} "
              f"-days 365 -nodes -subj '/CN=graph.facebook-hardware.com'")
        return

    server = HTTPServer((host, port), QuestSpoofHandler)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile, keyfile)
    server.socket = ctx.wrap_socket(server.socket, server_side=True)
    print(f"[spoof] Listening on {host}:{port} (HTTPS)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        if log_file:
            save_log(log_file)

"""Oracle Dashboard Backend — bridges GUI to Agent Vault.

Run: python3 oracle/dashboard_server.py
Dashboard: http://localhost:8788
"""
import json
import subprocess
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = 8788
VAULT = "oracle"
VAULT_ADDR = "http://127.0.0.1:8902"


class OracleHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/dashboard.html':
            self.path = '/dashboard.html'
            return super().do_GET()
        elif self.path == '/api/vault/list':
            self.send_json(self.vault_list())
        elif self.path == '/api/health':
            self.send_json({"status": "ok", "vault": VAULT, "addr": VAULT_ADDR})
        else:
            return super().do_GET()

    def do_POST(self):
        if self.path == '/api/vault/set':
            body = self.read_body()
            result = self.vault_set(body.get('key', ''), body.get('value', ''))
            self.send_json(result)
        elif self.path == '/api/vault/get':
            body = self.read_body()
            result = self.vault_get(body.get('key', ''))
            self.send_json(result)
        else:
            self.send_error(404)

    def read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}

    def send_json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def vault_list(self):
        try:
            result = subprocess.run(
                ['agent-vault', 'vault', 'credential', 'list', '--vault', VAULT],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                # Parse table output to extract keys
                keys = []
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and '│' in line and 'KEY' not in line and '──' not in line and '─' not in line:
                        parts = [p.strip() for p in line.split('│') if p.strip()]
                        if parts:
                            keys.append(parts[0])
                return {"keys": keys}
            return {"keys": [], "error": result.stderr}
        except Exception as e:
            return {"keys": [], "error": str(e)}

    def vault_set(self, key, value):
        if not key or not value:
            return {"ok": False, "error": "key and value required"}
        try:
            result = subprocess.run(
                ['agent-vault', 'vault', 'credential', 'set', f'{key}={value}', '--vault', VAULT],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return {"ok": True, "message": f"Set {key}"}
            return {"ok": False, "error": result.stderr}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def vault_get(self, key):
        if not key:
            return {"ok": False, "error": "key required"}
        try:
            result = subprocess.run(
                ['agent-vault', 'vault', 'credential', 'get', key, '--vault', VAULT],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return {"ok": True, "value": result.stdout.strip()}
            return {"ok": False, "error": result.stderr}
        except Exception as e:
            return {"ok": False, "error": str(e)}


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('0.0.0.0', PORT), OracleHandler)
    print(f"Oracle Dashboard: http://localhost:{PORT}")
    print(f"Agent Vault: {VAULT_ADDR}")
    print(f"Vault: {VAULT}")
    server.serve_forever()

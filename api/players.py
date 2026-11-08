from http.server import BaseHTTPRequestHandler
import json
import requests

URL = "http://kota2.indopride.id:30120"
TIMEOUT = 1


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            players = requests.get(f"{URL}/players.json", timeout=TIMEOUT).json()
            info = requests.get(f"{URL}/info.json", timeout=TIMEOUT).json()
            v = info.get("vars", {})
            body = {
                "online": len(players),
                "max": int(v.get("sv_maxClients", 0) or 0),
                "name": v.get("sv_projectName") or v.get("sv_hostname") or "FiveM Server",
                "icon": info.get("icon"),  # base64 PNG, bisa kosong
            }
            status = 200
        except Exception as e:
            body = {"error": str(e)}
            status = 502

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "s-maxage=15")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

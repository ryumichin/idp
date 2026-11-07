from http.server import BaseHTTPRequestHandler
import json
import requests

URL = "http://kota2.indopride.id:30120"
TIMEOUT = 5


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            players = requests.get(f"{URL}/players.json", timeout=TIMEOUT).json()
            info = requests.get(f"{URL}/info.json", timeout=TIMEOUT).json()
            body = {
                "online": len(players),
                "max": info.get("vars", {}).get("sv_maxClients", "?"),
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

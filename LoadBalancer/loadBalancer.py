import os
import requests
import socketserver
from dotenv import load_dotenv
from http.server import BaseHTTPRequestHandler

servers = []
master = 0
current_server = 0
tries = 0
try_servers = 1

def get_server():
    global current_server
    val = (current_server + 1) % len(servers)
    current_server = val if val != master else val + 1
    return servers[current_server]

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global try_servers
        server_url = servers[master]
        self.proxy(server_url)
        try_servers = 1

    def do_DELETE(self):
        global try_servers
        server_url = servers[master]
        self.proxy(server_url)
        try_servers = 1

    def do_GET(self):
        global try_servers
        server_url = get_server()
        self.proxy(server_url)
        try_servers = 1

    def proxy(self, server_url):
        global master
        global try_servers
        try:
            url = f'http://{server_url["ip"]}:{server_url["port"]}{self.path}'
            resp = requests.request(
                method=self.command,
                url=url,
                data=self.rfile.read(int(self.headers.get('Content-Length', 0)))
            )
            self.send_response(resp.status_code)
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
            for header in headers:
                self.send_header(*header)
            self.end_headers()
            self.wfile.write(resp.content)
        except Exception as e:
            if tries >= 3:
                if self.command == 'GET':
                    server_url = get_server()
                    self.proxy(server_url)
                else:
                    master = (current_server + 1) % len(servers)
                    server_url = servers[master]
                    self.proxy(server_url)
                tries = 0
                try_servers += 1
                if try_servers >= len(servers):
                    return
            tries += 1
            self.proxy(server_url)

if __name__ == '__main__':
    load_dotenv()
    servers = [
        {
            'ip':os.getenv("SERVERIP1"),
            'port':os.getenv("PORTSERVER1")
        },
        {
            'ip':os.getenv("SERVERIP2"),
            'port':os.getenv("PORTSERVER2")
        },
        {
            'ip':os.getenv("SERVERIP3"),
            'port':os.getenv("PORTSERVER3")
        }
    ]
    portHttp = int(os.getenv("PORTHTTP"))
    try:
        with socketserver.TCPServer(("", portHttp), RequestHandler) as httpd:
            print("Listening at port", portHttp)
            httpd.serve_forever()
    finally:
        print("Finishing server...")

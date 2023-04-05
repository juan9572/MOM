import os
import requests
import socketserver
from dotenv import load_dotenv
from http.server import BaseHTTPRequestHandler

servers = []
current_server = 0

def get_server():
    global current_server
    val = (current_server + 1) % len(servers)
    current_server = val if val != 0 else 1
    return servers[current_server]

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        server_url = servers[0]
        self.proxy(server_url)

    def do_DELETE(self):
        server_url = servers[0]
        self.proxy(server_url)

    def do_GET(self):
        server_url = get_server()
        self.proxy(server_url)

    def proxy(self, server_url):
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

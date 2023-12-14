import http.server
from  http.server import BaseHTTPRequestHandler
import asyncio
from kasa import (SmartBulb, SmartPlug)
import socketserver
from json import dumps
import urllib.parse
from time import sleep

port = 8080
loop = None

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        dev = SmartBulb("192.168.2.25")
        tree = SmartPlug("192.168.2.9")
        outdoor = SmartPlug("192.168.2.6")

        req = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(req.query)

        if req.path == '/favicon.ico':
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes('Not found', 'utf-8'))
            return

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if 'which' in query and query['which'][0] == 'tree':
            which = tree
        if 'which' in query and query['which'][0] == 'outdoor':
            which = outdoor
        else:
            which = dev

        if req.path == '/info':
            asyncio.run(which.update())
            self.wfile.write(bytes(dumps(which.hw_info), 'utf-8'))
        elif req.path == '/status':
            asyncio.run(which.update())
            if which.is_on:
                status = 'on'
            else:
                status = 'off'
            self.wfile.write(bytes(status, 'utf-8'))
        elif req.path == '/on':
            asyncio.run(which.turn_on())
            self.wfile.write(bytes('Turned light on.', 'utf-8'))
        elif req.path == '/off':
            asyncio.run(which.turn_off())
            self.wfile.write(bytes('Turned light off.', 'utf-8'))
        else:
            try:
                in_file = open("/src/index.html", "rb")
            except:
                in_file = open("index.html", "rb")
            data = in_file.read()
            in_file.close()
            self.wfile.write(data)

Handler = MyHandler

def main():
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print("Web Server is running at http://localhost:%s" %port)
        httpd.serve_forever()

main()
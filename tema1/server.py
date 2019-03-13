from http.server import BaseHTTPRequestHandler, HTTPServer
import datetime

port = 8085

class myHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/service1':
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write("Hello World")

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write("hei")

server = HTTPServer(('', port), myHandler)
print('Started httpserver on port ', port)

#Wait forever for incoming http requests
server.serve_forever()
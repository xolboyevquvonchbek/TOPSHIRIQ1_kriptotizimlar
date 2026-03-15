from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
from urllib.parse import parse_qs
from argon2 import PasswordHasher

ph = PasswordHasher()

users = {
    "admin": {"password": ph.hash("12345"), "role": "admin"},
    "quvonch": {"password": ph.hash("12345"), "role": "user"}
}

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open("login.html", "rb") as f:
                self.wfile.write(f.read())

        elif self.path == "/admin":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>Admin panel</h1>")

    def do_POST(self):
        if self.path == "/login":
            length = int(self.headers["Content-Length"])
            body = self.rfile.read(length).decode()
            data = parse_qs(body)

            username = data.get("username", [""])[0]
            password = data.get("password", [""])[0]

            if username in users:
                try:
                    ph.verify(users[username]["password"], password)
                    role = users[username]["role"]

                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()

                    if role == "admin":
                        self.wfile.write(b"<h1>Welcome Admin</h1>")
                    else:
                        self.wfile.write(b"<h1>Welcome Quvonch</h1>")

                except Exception:
                    self.send_response(401)
                    self.end_headers()
                    self.wfile.write(b"Login failed")
            else:
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Login failed")

server_address = ("0.0.0.0", 4443)
httpd = HTTPServer(server_address, MyHandler)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(
    certfile="C:/Users/admin/TLS_project_Quvonch/server.crt",
    keyfile="C:/Users/admin/TLS_project_Quvonch/server.key"
)
#context.verify_mode = ssl.CERT_REQUIRED
#context.load_verify_locations(cafile="C:/Users/admin/TLS_project_Quvonch/rootCA.crt")

httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print("Server running on https://localhost:4443")
httpd.serve_forever()
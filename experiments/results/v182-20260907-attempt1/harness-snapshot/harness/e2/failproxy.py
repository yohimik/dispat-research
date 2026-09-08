"""Fault-injecting reverse proxy in front of verdaccio. A PUT whose path
contains a name listed in /deny/ answers 502; everything else forwards.
~60 lines, stdlib only."""
import http.client
import http.server
import os
import sys

UPSTREAM = os.environ.get("UPSTREAM", "verdaccio:4873")
DENY_DIR = os.environ.get("DENY_DIR", "/deny")


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _denied(self):
        if self.command != "PUT":
            return False
        for name in os.listdir(DENY_DIR) if os.path.isdir(DENY_DIR) else []:
            if name and name in self.path:
                return True
        return False

    def _forward(self):
        if self._denied():
            body = b'{"error":"injected fault"}'
            self.send_response(502)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            sys.stderr.write(f"DENY {self.command} {self.path}\n")
            return
        length = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(length) if length else None
        conn = http.client.HTTPConnection(UPSTREAM, timeout=60)
        headers = {k: v for k, v in self.headers.items()
                   if k.lower() != "host"}
        conn.request(self.command, self.path, body=body, headers=headers)
        resp = conn.getresponse()
        data = resp.read()
        self.send_response(resp.status)
        for k, v in resp.getheaders():
            if k.lower() in ("transfer-encoding", "connection", "content-length"):
                continue
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    do_GET = do_PUT = do_POST = do_DELETE = _forward

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("", 4873), H).serve_forever()

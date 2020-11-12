#!/usr/bin/env python3

import sys
import io
import requests
import socket
import http.server


def get_broadcaster_status():
    hn = socket.gethostname()

    sout = io.StringIO()

    sout.write("# HELP varnish_broadcaster_requests Numbeer of broadcaster requests\n")
    sout.write("# TYPE varnish_broadcaster_requests counter\n")

    r = requests.get("http://localhost:8089/api/stats")
    for gn, g in r.json()['groups'].items():
        if hn in g['hosts']:
            # Found us!
            h = g['hosts'][hn]
            for r, statuses in h['requests'].items():
                for s, num in statuses.items():
                    sout.write('varnish_broadcaster_requests{{method="{}",status="{}"}} {}\n'.format(r, s, num))
    return sout.getvalue()


class HttpHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        status = get_broadcaster_status()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(status.encode('ascii'))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--server':
        httpd = http.server.HTTPServer(('', 9135), HttpHandler)
        httpd.serve_forever()
    else:
        print(get_broadcaster_status())

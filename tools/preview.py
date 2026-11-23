"""Serve the draft on loopback with fixture bookings and external actions blocked."""

import argparse
from datetime import datetime, timedelta
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]


def preview_script():
    today = datetime.now(ZoneInfo("Asia/Hong_Kong")).date()
    full = today + timedelta(days=1)
    partial_day = today + timedelta(days=2)
    csv = json.dumps(f"date,morning,afternoon,evening\n{full},x,x,x\n{partial_day},x,,\n")
    return f"""
<script>
(() => {{
  const originalFetch = window.fetch.bind(window);
  window.fetch = (url, options) => {{
    const target = new URL(url, location.href);
    if (target.origin === 'https://docs.google.com')
      return Promise.resolve(new Response({csv}, {{headers: {{'Content-Type': 'text/csv'}}}}));
    if (target.origin === 'https://api.web3forms.com')
      return Promise.resolve(Response.json({{success:true}}));
    if (target.origin !== location.origin)
      return Promise.reject(new Error('External requests are blocked in this preview.'));
    return originalFetch(url, options);
  }};
  window.open = url => {{
    const message = new URL(url).searchParams.get('text');
    alert(message ? 'Preview only. No message sent.\\n\\n' + message : 'External links are disabled in this preview.');
  }};
  document.addEventListener('click', event => {{
    const link = event.target.closest('a[href]');
    if (link && new URL(link.href).origin !== location.origin) {{
      event.preventDefault();
      alert('External links are disabled in this preview.');
    }}
  }});
}})();
</script>
<aside style="padding:.5rem;text-align:center;background:#27251e;color:white">
  Local preview · Sample availability · Messages are simulated
</aside>
"""


class PreviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        page = self.path.split("?", 1)[0]
        if page not in {"/", "/index.html", "/booking.html"}:
            return super().do_GET()

        filename = "index.html" if page == "/" else page[1:]
        html = (ROOT / filename).read_text(encoding="utf-8")
        body = html.replace("<body>", "<body>" + preview_script(), 1).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Security-Policy", "connect-src 'self'; form-action 'none'")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    handler = partial(PreviewHandler, directory=ROOT)
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
        print(f"Nook draft preview on http://127.0.0.1:{args.port}/", flush=True)
        server.serve_forever()

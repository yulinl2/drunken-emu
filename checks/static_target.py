"""Run bin/emu against an unchanged HTML file over HTTP (#76).

Only the page's directory is served, on loopback and an OS-assigned port.
The server belongs to this invocation and is closed even if a check fails.
file:// is unavailable in some managed browsers and differs on fetch/CORS.
"""
import functools
import http.server
import os
from pathlib import Path
import subprocess
import sys
import threading
from urllib.parse import quote


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    mode, raw, *args = sys.argv[1:]
    path = Path(raw).resolve()
    if not path.is_file():
        print(f"HTML input is not a file: {path}", file=sys.stderr)
        return 2
    handler = functools.partial(QuietHandler, directory=str(path.parent))
    with http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_port}/{quote(path.name)}"
            env = dict(os.environ, EMU_TARGET_KIND="html", EMU_MOUNT=os.environ.get("EMU_MOUNT", "body"))
            return subprocess.run(["bash", str(Path(__file__).resolve().parents[1] / "bin/emu"), mode, url, *args], env=env).returncode
        finally:
            server.shutdown()
            thread.join()


if __name__ == "__main__":
    sys.exit(main())

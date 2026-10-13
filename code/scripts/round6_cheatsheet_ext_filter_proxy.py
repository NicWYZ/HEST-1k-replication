"""Round 6 extension, cheatsheet track: the filtering proxy that is a trial's only route out.

Round 6's proxy (round6_cheatsheet_filter_proxy.py) with one addition, the
direct mode of instruction section 6.5. A container on the Mac has no upstream
proxy, so with --direct an allowed CONNECT is answered by opening a TCP
connection straight to the allowed host. The allow list is unchanged.


It listens on a Unix socket, accepts an HTTP `CONNECT host:port` only when
host:port is on the allow list (the Anthropic API host on 443), and forwards
the tunnel, through an upstream proxy (--upstream) or straight to the host
(--direct). Every request line it receives is logged with a timestamp and
whether it was allowed. Anything that is not a CONNECT to an allowed host gets
403 and the connection is closed (instruction section 6.4, property I3).

    python round6_cheatsheet_ext_filter_proxy.py SOCKET_PATH LOG_PATH --direct \
        [--allow api.anthropic.com:443]
"""
import argparse
import asyncio
import datetime
import os
import urllib.parse


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")


class Filter:
    def __init__(self, upstream, allow, log_path):
        self.direct = upstream is None
        if not self.direct:
            u = urllib.parse.urlsplit(upstream)
            self.up_host, self.up_port = u.hostname, u.port
        self.allow = set(allow)
        self.log = open(log_path, "a", buffering=1)

    def record(self, verdict, line):
        self.log.write(f"{now()}\t{verdict}\t{line}\n")

    async def pipe(self, r, w):
        try:
            while True:
                b = await r.read(65536)
                if not b:
                    break
                w.write(b)
                await w.drain()
        except (ConnectionError, asyncio.CancelledError):
            pass
        finally:
            try:
                w.close()
            except Exception:
                pass

    async def handle(self, cr, cw):
        try:
            head = await asyncio.wait_for(cr.readuntil(b"\r\n\r\n"), 30)
        except Exception:
            cw.close()
            return
        line = head.split(b"\r\n", 1)[0].decode("latin-1", "replace")
        parts = line.split()
        target = parts[1] if len(parts) >= 2 else ""
        if len(parts) != 3 or parts[0].upper() != "CONNECT" or target not in self.allow:
            self.record("DENY", line)
            cw.write(b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
            await cw.drain()
            cw.close()
            return
        if self.direct:
            host, port = target.rsplit(":", 1)
            try:
                ur, uw = await asyncio.wait_for(asyncio.open_connection(host, int(port)), 30)
            except Exception as e:
                self.record("UPSTREAM_ERROR", f"{line} :: {e!r}")
                cw.write(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n")
                await cw.drain()
                cw.close()
                return
            self.record("ALLOW", f"{line} -> direct")
            cw.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
            await cw.drain()
            await asyncio.gather(self.pipe(cr, uw), self.pipe(ur, cw))
            return
        try:
            ur, uw = await asyncio.open_connection(self.up_host, self.up_port)
            uw.write(f"CONNECT {target} HTTP/1.1\r\nHost: {target}\r\n\r\n".encode())
            await uw.drain()
            resp = await asyncio.wait_for(ur.readuntil(b"\r\n\r\n"), 30)
        except Exception as e:
            self.record("UPSTREAM_ERROR", f"{line} :: {e!r}")
            cw.write(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n")
            await cw.drain()
            cw.close()
            return
        status = resp.split(b"\r\n", 1)[0].decode("latin-1", "replace")
        self.record("ALLOW", f"{line} -> {status}")
        cw.write(resp)
        await cw.drain()
        await asyncio.gather(self.pipe(cr, uw), self.pipe(ur, cw))


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("socket")
    ap.add_argument("log")
    ap.add_argument("--upstream", default=os.environ.get("HTTPS_PROXY"))
    ap.add_argument("--direct", action="store_true")
    ap.add_argument("--allow", action="append", default=None)
    a = ap.parse_args()
    if a.direct:
        a.upstream = None
    elif not a.upstream:
        ap.error("give --direct or --upstream")
    allow = a.allow or ["api.anthropic.com:443"]
    f = Filter(a.upstream, allow, a.log)
    if os.path.exists(a.socket):
        os.unlink(a.socket)
    server = await asyncio.start_unix_server(f.handle, path=a.socket)
    os.chmod(a.socket, 0o666)
    f.record("START", f"socket={a.socket} upstream={a.upstream} allow={sorted(allow)} pid={os.getpid()}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

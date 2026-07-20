# enablessh hook for plan9/9front (VM_TRANSPORT=telnet). Host-side python,
# exec()'d into build.py's globals, so build.py functions are bare names.
#
# There is no sshd to enable. Instead this hook gives the guest its
# remote-exec + file channel:
#
#   1. Through the serial console (the guest sits at the rc prompt after the
#      unattended first boot) persist /rc/bin/termrc.local -- DHCP + no-auth
#      telnetd on 23 + exportfs 9P on 564 -- so every later boot (including
#      anyvm runtime boots) comes up remotely reachable; then run the same
#      three commands directly so THIS boot is reachable too.
#   2. Wait until the guest's telnetd answers through the hostfwd.
#   3. Replace /sys/src/cmd/exportfs/io.c with files/exportfs-io.c (the
#      anyvm errstr-decoration patch: the Plan 9 kernel decorates error
#      strings with the path, which breaks Linux v9fs errno mapping and
#      with it every file-create over a kernel 9p mount) and rebuild
#      exportfs in-guest with mk install. listen1 fork+execs a fresh
#      /bin/exportfs per connection, so new mounts pick the patched binary
#      up without a reboot.
#   4. Create the runtime work dir.
#
# The patched io.c is delivered to the guest over http via hget. We do NOT
# reuse build.py's shared http.server on port 8000 -- concurrent local
# builds (or any other listener) can hold that port and the guest would
# fetch the wrong tree (404). Instead this hook serves the single file on
# its own ephemeral port, bound to the host loopback that the slirp gateway
# (192.168.122.1) forwards to.

import http.server
import threading

log("plan9 enablessh: baking termrc.local + starting listeners (console)")

for _l in [
    "echo 'ip/ipconfig' >/rc/bin/termrc.local",
    "echo 'aux/listen1 -t ''tcp!*!23'' /bin/ip/telnetd -t -u glenda &'"
    " >>/rc/bin/termrc.local",
    "echo 'aux/listen1 -t ''tcp!*!564'' /bin/exportfs -r / &'"
    " >>/rc/bin/termrc.local",
    "cat /rc/bin/termrc.local",
    # bring this very boot up too (the baked file only helps future boots)
    "ip/ipconfig",
    "aux/listen1 -t 'tcp!*!23' /bin/ip/telnetd -t -u glenda &",
    "aux/listen1 -t 'tcp!*!564' /bin/exportfs -r / &",
]:
    string(_l)
    enter()
    time.sleep(3)
time.sleep(5)

if not _wait_telnet(max_retries=30):
    raise SystemExit("plan9 enablessh: guest telnetd never answered")

# --- serve the patched io.c on our own ephemeral port -----------------------
with open("files/exportfs-io.c", "rb") as _f:
    _patch_bytes = _f.read()

class _PatchHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(_patch_bytes)))
        self.end_headers()
        self.wfile.write(_patch_bytes)

    def log_message(self, *a):
        pass

_patch_port = free_port(18000, 18999)
_httpd = http.server.HTTPServer(("0.0.0.0", _patch_port), _PatchHandler)
_httpd_thread = threading.Thread(target=_httpd.serve_forever, daemon=True,
                                 name="plan9-patch-http")
_httpd_thread.start()
log("plan9 enablessh: serving exportfs-io.c on :%d" % _patch_port)

try:
    log("plan9 enablessh: patching exportfs (errstr decoration) in-guest")
    _url = "http://192.168.122.1:%d/exportfs-io.c" % _patch_port
    _ok, _text = telnet_exec([
        "chmod 666 /sys/src/cmd/exportfs/io.c",
        "hget %s >/sys/src/cmd/exportfs/io.c" % _url,
        # marker echoes: the quote-split keeps the guest's echo of the typed
        # command from matching; $status is empty on success in rc.
        "grep -s anyvm /sys/src/cmd/exportfs/io.c && echo patch''-present-ok",
        # force a clean relink so a stale io.6 / a live 6.exportfs can't
        # leave the old binary in place
        "cd /sys/src/cmd/exportfs && rm -f *.6 6.exportfs",
        "cd /sys/src/cmd/exportfs && mk install && echo mk''-install-ok",
        "mkdir -p /usr/glenda/work && echo workdir''-ok",
    ], settle=15.0)
    log("plan9 enablessh transcript:\n%s" % _text)
finally:
    try:
        _httpd.shutdown()
    except Exception:
        pass

for _marker in ("patch-present-ok", "mk-install-ok", "workdir-ok"):
    if _marker not in _text:
        raise SystemExit("plan9 enablessh: marker %r missing -- exportfs "
                         "patch/rebuild did not complete" % _marker)

log("plan9 enablessh: done (telnetd + patched exportfs + work dir)")

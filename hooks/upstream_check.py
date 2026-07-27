#!/usr/bin/env python3
# Print the current 9front release number, e.g. "11554". Empty output
# means "nothing detected" and is not an error; a non-zero exit means
# detection itself is broken (network error, HTTP error, or a page that no
# longer matches the expected shape) and must be reported by the caller,
# never swallowed. A failure must NEVER print a plausible-but-wrong
# version -- the version is only printed after every step below has
# succeeded.
#
# Source of truth: https://9front.org/iso/
# Fetched and confirmed by hand (2026-07-26): unlike a typical release
# archive, this directory holds ONLY the files for the current release --
# there is no historical listing of older release numbers here (upstream
# overwrites this directory in place on every release, and a full history
# lives instead at https://9front.org/releases/YYYY/MM/DD/N/, one
# announcement page per cut, which is not a machine-readable index). This
# is still a genuine, distinct release number, not a rolling/nightly
# build: 9front.org's own front page names the same cut "latest release"
# with a fixed date, e.g.
#   latest release:
#   <a href="http://9front.org/releases/2026/01/24/0/">GEFS SERVICE PACK 1
# and the /iso/ page is a plain autoindex, one row per file, e.g.
#   <td><a class="file name" href="9front-11554.amd64.qcow2.gz">
#     9front-11554.amd64.qcow2.gz</a></td>
# The amd64 qcow2 asset is the exact image family this builder's
# VM_VHD_LINK downloads (9front-<rel>.amd64.qcow2.gz); its filename is the
# only place the release number appears on this page.
#
# stdlib only (urllib.request, re, sys, os) -- no external dependencies.

import os
import re
import sys
import urllib.request

URL = "https://9front.org/iso/"
TIMEOUT = 60
USER_AGENT = "anyvm-org-upstream-watcher/1.0"

PATTERN = re.compile(r'href="9front-(\d+)\.amd64\.qcow2\.gz"')


def resolve_natural_key():
    """Return the engine's own natural_key, or fail loudly.

    watch.yml clones base-builder INTO the builder repo root, so at
    detection time it sits at "base-builder/" (relative to this hook's
    cwd, the builder repo root). A local checkout instead has it as a
    sibling, "../base-builder". Try both, in that order.

    There is deliberately NO local fallback copy. Ordering must be the
    single rule the engine uses -- a per-hook duplicate would have to be
    kept in sync by hand across every builder and would drift silently,
    and a hook that ranks versions differently from watch.py is worse
    than one that refuses to run. Both real contexts (CI and a local
    sibling checkout) always provide base-builder, so an ImportError here
    means the environment is wrong: report it as broken detection rather
    than guessing an order.
    """
    for candidate in ("base-builder", os.path.join("..", "base-builder")):
        if not os.path.isdir(candidate):
            continue
        path = os.path.abspath(candidate)
        if path not in sys.path:
            sys.path.insert(0, path)
        try:
            import gendata
            return gendata.natural_key
        except ImportError:
            continue
    raise ImportError(
        "base-builder/gendata.py not importable from %s; expected it at "
        "./base-builder (CI) or ../base-builder (local checkout)"
        % os.getcwd())


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", "replace")


def main():
    try:
        key = resolve_natural_key()
    except ImportError as e:
        sys.stderr.write("upstream_check: %s\n" % e)
        return 1
    try:
        html = fetch(URL)
    except Exception as e:
        sys.stderr.write("upstream_check: fetch of %s failed: %s\n"
                         % (URL, e))
        return 1
    versions = PATTERN.findall(html)
    if not versions:
        sys.stderr.write("upstream_check: no 9front-<rel>.amd64.qcow2.gz "
                         "found in %s; page shape may have changed\n" % URL)
        return 1
    newest = sorted(set(versions), key=key)[-1]
    print(newest)
    return 0


if __name__ == "__main__":
    sys.exit(main())

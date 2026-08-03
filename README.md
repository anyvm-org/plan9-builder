

[![Build](https://github.com/anyvm-org/plan9-builder/actions/workflows/build.yml/badge.svg)](https://github.com/anyvm-org/plan9-builder/actions/workflows/build.yml)

Latest: v2.0.0


The image builder for `plan9`


All the supported releases are here:



| Release (9front) | x86_64 (amd64) |
|---------|---------|
| 11952 | ✅ (9p) |
| 11554 | ✅ (9p) |

<!-- release-label: Release (9front) -->
<!-- arch-label: x86_64 = x86_64 (amd64) -->

<!-- 9front is a rolling upstream that keeps ONLY the newest image on
     9front.org/iso/: when 11952 was published (2026-08-02, landed by the
     watcher), 9front-11554.amd64.qcow2.gz was deleted upstream (HTTP 404,
     build run 30768208391), so 11554 can never be rebuilt from source
     again. Its tag is therefore left OUT of conf/all.release.conf (the
     hand-owned build membership): the table row and the already-published
     release assets stay usable, only the build stops. Expect to drop a
     tag from the membership every time 9front cuts a release. -->




How to build:

1. Use the [manual.yml](.github/workflows/manual.yml) to build manually.
   
    Run the workflow manually, you will get a view-only webconsole from the output of the workflow, just open the link in your web browser.
   
    You will also get an interactive VNC connection port from the output, you can connect to the vm by any vnc client.

2. Run the builder locally on your Ubuntu machine.

    Just clone the repo. and run:
    ```bash
    python3 build.py conf/plan9-11952.conf
    ```
   

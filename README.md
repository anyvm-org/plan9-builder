

[![Build](https://github.com/anyvm-org/plan9-builder/actions/workflows/build.yml/badge.svg)](https://github.com/anyvm-org/plan9-builder/actions/workflows/build.yml)

Latest: 0.0.0


The image builder for `plan9`


All the supported releases are here:



| Release (9front) | x86_64 (amd64) |
|------------------|----------------|
| 11554            |  ⏳ (pending CI)  |




How to build:

1. Use the [manual.yml](.github/workflows/manual.yml) to build manually.
   
    Run the workflow manually, you will get a view-only webconsole from the output of the workflow, just open the link in your web browser.
   
    You will also get an interactive VNC connection port from the output, you can connect to the vm by any vnc client.

2. Run the builder locally on your Ubuntu machine.

    Just clone the repo. and run:
    ```bash
    python3 build.py conf/plan9-11554.conf
    ```
   

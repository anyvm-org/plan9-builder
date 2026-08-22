

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

How the images are built:

Each image is built automatically in the
[anyvm-org/plan9-builder](https://github.com/anyvm-org/plan9-builder)
repo's GitHub Actions: it downloads the official 9front amd64 qcow2
image, boots it in QEMU, configures console access and the anyvm
runtime support, pre-installs what the conf lists, and exports the disk
as a compressed qcow2 image. No interactive installer is run.

Upstream media: the official 9front release images from
https://9front.org/iso/ (release notes: http://9front.org/releases/).

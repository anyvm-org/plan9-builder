

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
     again. no-build keeps its table row and its already-published release
     assets usable while taking it out of the build matrix. Expect to add
     one of these lines every time 9front cuts a release. -->
<!-- no-build: 11554 -->

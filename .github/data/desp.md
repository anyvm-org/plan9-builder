How the images are built:

Each image is built automatically in the
[anyvm-org/plan9-builder](https://github.com/anyvm-org/plan9-builder)
repo's GitHub Actions: it downloads the official 9front amd64 qcow2
image, boots it in QEMU, configures console access and the anyvm
runtime support, pre-installs what the conf lists, and exports the disk
as a compressed qcow2 image. No interactive installer is run.

Upstream media: the official 9front release images from
https://9front.org/iso/ (release notes: http://9front.org/releases/).

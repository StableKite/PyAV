# CPython 3.15t engineering wheels

A normal `pip install git+https://github.com/StableKite/PyAV.git` selects the
verified wheel on CPython 3.15t Windows x86-64 and Linux x86-64 with glibc 2.39+.
pip validates its pinned SHA-256.

Version `19.0.2+stablekite.2` describes the buffers accepted by `Packet` and
`CodecContext.parse` and the stream carried by each packet type. A packet's
`stream` can be `None`, for example before it is associated with a stream.
Stream-level encoders and demux retain their specific packet types. A
`stream_index` is read-only.

The prior handling of FFmpeg failed opens remains in place. An unsuccessful
open preserves the selected codec. A caller retrying an audio open must restore
the full configuration because FFmpeg clears the channel layout on failure.

The native extensions were rebuilt against the upstream PyAV FFmpeg 9.0.2-2
shared SDK. The final wheels carry the exact stubs and version file from
the source recorded in `binary_wheels.json`. Each wheel was tested in
a clean environment, including the canonical test suite, AAC and libopus
failure recovery, native imports, threading and real packet encode, demux and
decode with the GIL off. The release qualification file records per-platform
counts and artifact hashes.

Native or build source changes, explicit build settings, compiler overrides
and other ABIs or platforms use the source backend. The Windows x86-64 3.15t
source backend verifies and bundles the pinned SDK when no explicit build
options are supplied. Other source platforms use the normal development SDK.

The FFmpeg SDK recipes are available from the
[PyAV SDK project](https://github.com/PyAV-Org/pyav-ffmpeg).

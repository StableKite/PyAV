# CPython 3.15t engineering wheels

A normal `pip install git+https://github.com/StableKite/PyAV.git` selects the
verified engineering wheel on CPython 3.15t Windows x86-64 or Linux x86-64 with
glibc 2.39+. No FFmpeg SDK, compiler or extra consumer flag is required for
these recorded binary paths. pip validates the pinned SHA256.

Version `19.0.2+stablekite.1` preserves the selected FFmpeg codec after an
unsuccessful open, so retrying invalid input raises an ordinary exception.
Correcting the complete configuration permits real encoding on the same
context. FFmpeg itself clears the audio channel layout during failed-open
cleanup; callers must restore it as well as correcting the invalid format.

Both original wheels were built from clean source against the official
PyAV FFmpeg 9.0.2-2 shared SDK, with every Cython extension rebuilt together.
The Windows source commit is `7b25676794bb2fdf1d28024c60126e6604b5f50f`;
Linux and the corrected subprocess regression use
`e2ccdab29a07d1797dbbd84f72a4521fe17d8c4a`. Their runtime/build sources are
identical; the latter changes only three lines of the regression helper.
Each platform passed all 574 canonical tests (543 passed, 31 pre-existing
SDK capability skips), real AAC and libopus failure/recovery, every native
module import, lossless video and native-thread encoding with natural GIL OFF.

`binary_wheels.json` records the source snapshot, original artifact hashes
and delivery-file checks. Native/build source changes, explicit build settings,
compiler overrides or another ABI/platform retain the original source backend.
On Windows 3.15t x86-64 that source fallback automatically obtains the official
SDK, checks its size and SHA256, builds the extensions and bundles their DLLs
using delvewheel. Other source platforms retain their normal development SDK
prerequisites.

The SDK build recipes and third-party component versions are maintained in
the [upstream SDK project](https://github.com/PyAV-Org/pyav-ffmpeg).
These artifacts are engineering dependency builds, not a StableKite release.

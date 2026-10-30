# Experimental CPython 3.15t Linux wheels

A normal `pip install` from this repository selects the verified release wheel
for the recorded source snapshot on Linux x86_64, CPython 3.15t and glibc 2.39+.
pip performs downloading, dependency resolution and SHA256 validation.
No consumer SDK setup or extra build flag is required for this binary path.

The original PEP 517 backend and its build requirements are preserved. Changed
native/build sources, another ABI/platform, explicit configuration settings or
compiler overrides use that original source build. The JSON manifest records
the source commit, artifact hash and the checked delivery metadata. Source
builds retain their ordinary development-library prerequisites.

These are engineering dependency artifacts, not a StableKite release.

On CPython 3.15t Windows x86-64, a normal source installation automatically
fetches the official PyAV FFmpeg 9.0.2-2 SDK, verifies its SHA256 and size,
compiles the original PyAV extensions, and uses delvewheel to bundle their DLL
dependencies. The usual Visual C++ build tools are required; no FFmpeg SDK
installation or consumer configuration flag is required. The pinned SDK is
`https://github.com/PyAV-Org/pyav-ffmpeg/releases/download/9.0.2-2/ffmpeg-windows-x86_64.tar.gz`,
SHA256 `647a8f6d7d5f6e78ce9d33b8ea43b1f98eb1055e69ac5de26b31ecfe8b45142d`.
Its source build recipes and third-party component versions are maintained in
the [upstream SDK project](https://github.com/PyAV-Org/pyav-ffmpeg).

The Linux wheel's native source snapshot remains unchanged. The manifest also
accounts for the Windows-only delivery helper and the doctest lifecycle fix;
neither changes a runtime Python/Cython extension. The doctest fix runs each
original example through its public unittest lifecycle and preserves expected
bytes output. Explicit build settings and compiler overrides retain the
original developer-managed source build.

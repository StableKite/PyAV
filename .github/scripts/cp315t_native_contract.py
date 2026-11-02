"""Real PyAV codecs, every native import, independent streams on native threads."""

import concurrent.futures
import importlib
import importlib.machinery
import io
import json
from pathlib import Path
import sys
import threading

expected = sys._xoptions.get("gil") == "1"
assert sys._is_gil_enabled() is expected
import av

assert sys._is_gil_enabled() is expected
import numpy as np

assert sys._is_gil_enabled() is expected
native = []
for path in Path(av.__file__).parent.rglob("*"):
    suffix = next(
        (s for s in importlib.machinery.EXTENSION_SUFFIXES if path.name.endswith(s)),
        None,
    )
    if suffix:
        relative = path.relative_to(Path(av.__file__).parent)
        name = ".".join(("av", *relative.parts[:-1], relative.name[: -len(suffix)]))
        importlib.import_module(name)
        assert sys._is_gil_enabled() is expected, name
        native.append(name)
capabilities = {}
for name in ("ffv1", "libx264", "libx264rgb", "libx265", "h264_nvenc", "hevc_nvenc"):
    try:
        capabilities[name] = av.codec.Codec(name, "w").name
    except av.codec.codec.UnknownCodecError:
        capabilities[name] = None
print(
    json.dumps(
        dict(
            libraries=av.library_versions,
            capabilities=capabilities,
            module=av.__file__,
            GIL=sys._is_gil_enabled(),
            native_modules=len(native),
        )
    ),
    flush=True,
)


def roundtrip(codec, index=0):
    data = io.BytesIO()
    originals = []
    with av.open(data, mode="w", format="matroska") as output:
        stream = output.add_stream(codec, rate=24)
        stream.width, stream.height = 64, 48
        stream.pix_fmt = "bgr0" if codec == "ffv1" else "rgb24"
        if codec != "ffv1":
            stream.options = {"crf": "0", "preset": "ultrafast"}
        for number in range(4):
            array = np.full((48, 64, 3), (index + number) % 255, dtype=np.uint8)
            array[:, :, 1] = 87
            array[12:30, 15:42, 2] = 193
            originals.append(array)
            frame = av.VideoFrame.from_ndarray(array, format="rgb24")
            frame.pts = number
            for packet in stream.encode(frame):
                output.mux(packet)
        for packet in stream.encode(None):
            output.mux(packet)
    data.seek(0)
    with av.open(data, mode="r") as input:
        restored = [f.to_ndarray(format="rgb24") for f in input.decode(video=0)]
    assert len(restored) == len(originals)
    for actual, wanted in zip(restored, originals):
        np.testing.assert_array_equal(actual, wanted)
    return len(data.getvalue())


sizes = {name: roundtrip(name) for name in ("ffv1", "libx264rgb")}
assert capabilities["libx264"] and capabilities["libx265"], capabilities
barrier = threading.Barrier(4)


def worker(index):
    barrier.wait(timeout=10)
    for iteration in range(8):
        roundtrip("ffv1", index + iteration)
    return threading.get_native_id()


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    thread_ids = list(executor.map(worker, range(4)))
assert len(set(thread_ids)) == 4
assert sys._is_gil_enabled() is expected
print(
    json.dumps(
        dict(
            status="PASS",
            python=sys.version,
            version=av.__version__,
            GIL=sys._is_gil_enabled(),
            native=native,
            encoded_sizes=sizes,
            native_threads=thread_ids,
            threaded_encoded_decoded_frames=128,
        )
    )
)

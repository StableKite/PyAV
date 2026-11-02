import av, io, json, sys
from fractions import Fraction

assert sys.flags.gil is None and not sys._is_gil_enabled()
buffer = io.BytesIO()
with av.open(buffer, "w", format="ogg") as output:
    stream = output.add_stream("libopus", rate=48000)
    stream.layout = "stereo"
    stream.format = "fltp"
    frame = av.AudioFrame(format="fltp", layout="stereo", samples=960)
    frame.sample_rate = 48000
    frame.time_base = Fraction(1, 48000)
    frame.pts = 0
    for plane in frame.planes:
        plane.update(bytes(plane.buffer_size))
    for attempt in range(3):
        try:
            stream.encode(frame)
        except av.error.ArgumentError as error:
            print(
                json.dumps({"expected_failed_open": attempt, "exception": str(error)}),
                flush=True,
            )
        else:
            raise AssertionError("Real libopus must reject fltp")
        assert not stream.codec_context.is_open
        assert stream.codec_context.name == stream.codec_context.codec.name == "libopus"
        assert stream.codec_context.is_encoder and not stream.codec_context.is_decoder
    # FFmpeg clears ch_layout after failed open; restore complete configuration.
    stream.layout = "stereo"
    stream.format = "flt"
    packets = list(stream.encode(frame)) + list(stream.encode(None))
    assert packets
    for packet in packets:
        output.mux(packet)
assert buffer.getvalue()
buffer.seek(0)
with av.open(buffer) as source:
    frames = list(source.decode(audio=0))
    assert frames and all(
        f.sample_rate == 48000 and f.layout.name == "stereo" for f in frames
    )
    samples = sum(f.samples for f in frames)
    assert samples == 960, samples
assert sys.flags.gil is None and not sys._is_gil_enabled()
print(
    json.dumps(
        {"marker": "REAL_LIBOPUS_RETRY_RECOVERY_PASS", "samples": samples, "GIL": False}
    ),
    flush=True,
)

from typing import Literal

from av.codec.context import CodecContext
from av.packet import Packet, StreamT
from av.stream import Stream
from av.subtitles.subtitle import SubtitleSet

class SubtitleCodecContext(CodecContext):
    type: Literal["subtitle"]
    subtitle_header: bytes | None
    def decode2(self, packet: Packet[StreamT]) -> SubtitleSet | None: ...
    def encode_subtitle(self, subtitle: SubtitleSet) -> Packet[Stream]: ...

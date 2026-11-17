from av.packet import Packet, StreamT
from av.stream import Stream
from av.subtitles.subtitle import AssSubtitle, BitmapSubtitle, SubtitleSet

from .codeccontext import SubtitleCodecContext

class SubtitleStream(Stream):
    codec_context: SubtitleCodecContext
    def decode(
        self, packet: Packet[StreamT] | None = None
    ) -> list[AssSubtitle] | list[BitmapSubtitle]: ...
    def decode2(self, packet: Packet[StreamT]) -> SubtitleSet | None: ...

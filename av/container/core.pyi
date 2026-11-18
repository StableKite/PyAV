from collections.abc import Callable
from enum import Flag, IntEnum
from fractions import Fraction
from pathlib import Path
from types import TracebackType
from typing import Any, Literal, Self, TypedDict, cast, overload

from av.codec.hwaccel import HWAccel
from av.format import ContainerFormat
from av.rational import AVRational

from .input import InputContainer
from .output import OutputContainer
from .streams import StreamContainer

Real = int | float | Fraction | AVRational

class Flags(Flag):
    _value_: int
    gen_pts = ...
    ign_idx = ...
    non_block = ...
    ign_dts = ...
    no_fillin = ...
    no_parse = ...
    no_buffer = ...
    custom_io = ...
    discard_corrupt = ...
    flush_packets = ...
    bitexact = ...
    sort_dts = ...
    fast_seek = ...
    shortest = ...
    auto_bsf = ...

class AudioCodec(IntEnum):
    none = cast(int, ...)
    pcm_alaw = cast(int, ...)
    pcm_bluray = cast(int, ...)
    pcm_dvd = cast(int, ...)
    pcm_f16le = cast(int, ...)
    pcm_f24le = cast(int, ...)
    pcm_f32be = cast(int, ...)
    pcm_f32le = cast(int, ...)
    pcm_f64be = cast(int, ...)
    pcm_f64le = cast(int, ...)
    pcm_lxf = cast(int, ...)
    pcm_mulaw = cast(int, ...)
    pcm_s16be = cast(int, ...)
    pcm_s16be_planar = cast(int, ...)
    pcm_s16le = cast(int, ...)
    pcm_s16le_planar = cast(int, ...)
    pcm_s24be = cast(int, ...)
    pcm_s24daud = cast(int, ...)
    pcm_s24le = cast(int, ...)
    pcm_s24le_planar = cast(int, ...)
    pcm_s32be = cast(int, ...)
    pcm_s32le = cast(int, ...)
    pcm_s32le_planar = cast(int, ...)
    pcm_s64be = cast(int, ...)
    pcm_s64le = cast(int, ...)
    pcm_s8 = cast(int, ...)
    pcm_s8_planar = cast(int, ...)
    pcm_u16be = cast(int, ...)
    pcm_u16le = cast(int, ...)
    pcm_u24be = cast(int, ...)
    pcm_u24le = cast(int, ...)
    pcm_u32be = cast(int, ...)
    pcm_u32le = cast(int, ...)
    pcm_u8 = cast(int, ...)
    pcm_vidc = cast(int, ...)

class Chapter(TypedDict):
    id: int
    start: int
    end: int
    time_base: AVRational
    metadata: dict[str, str]

class Container:
    name: str
    file: Any
    buffer_size: int
    io_open: Any
    open_files: Any
    format: ContainerFormat
    options: dict[str, str]
    container_options: dict[str, str]
    streams: StreamContainer
    metadata: dict[str, str]
    open_timeout: Real | None
    read_timeout: Real | None
    flags: int
    video_codec_id: int
    def dumps_format(self) -> str: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
    @property
    def input_was_opened(self) -> bool: ...
    def close(self) -> None: ...
    def chapters(self) -> list[Chapter]: ...
    def set_chapters(self, chapters: list[Chapter]) -> None: ...

@overload
def open(
    file: Any,
    mode: Literal["r"],
    format: str | None = None,
    options: dict[str, str] | None = None,
    container_options: dict[str, str] | None = None,
    buffer_size: int = 32768,
    timeout: Real | None | tuple[Real | None, Real | None] = None,
    io_open: Callable[..., Any] | None = None,
    hwaccel: HWAccel | None = None,
) -> InputContainer: ...
@overload
def open(
    file: str | Path,
    mode: Literal["r"] | None = None,
    format: str | None = None,
    options: dict[str, str] | None = None,
    container_options: dict[str, str] | None = None,
    buffer_size: int = 32768,
    timeout: Real | None | tuple[Real | None, Real | None] = None,
    io_open: Callable[..., Any] | None = None,
    hwaccel: HWAccel | None = None,
) -> InputContainer: ...
@overload
def open(
    file: Any,
    mode: Literal["w"],
    format: str | None = None,
    options: dict[str, str] | None = None,
    container_options: dict[str, str] | None = None,
    buffer_size: int = 32768,
    timeout: Real | None | tuple[Real | None, Real | None] = None,
    io_open: Callable[..., Any] | None = None,
    hwaccel: HWAccel | None = None,
) -> OutputContainer: ...
@overload
def open(
    file: Any,
    mode: Literal["r", "w"] | None = None,
    format: str | None = None,
    options: dict[str, str] | None = None,
    container_options: dict[str, str] | None = None,
    buffer_size: int = 32768,
    timeout: Real | None | tuple[Real | None, Real | None] = None,
    io_open: Callable[..., Any] | None = None,
    hwaccel: HWAccel | None = None,
) -> InputContainer | OutputContainer: ...

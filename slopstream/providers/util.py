import subprocess
from pathlib import Path

from slopstream import config


def download(url: str, dest: Path, session) -> None:
    with session.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)


def _has_audio(src: Path) -> bool:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(src)],
        capture_output=True, text=True,
    )
    return bool(out.stdout.strip())


def transcode_to_stream_format(src: Path, dest: Path) -> None:
    """Normalize every clip to identical codec/resolution/fps/audio so the
    streamer can concatenate them without re-encoding glitches. YouTube
    requires an audio track, so silent audio is added when the source has none."""
    w, h = config.STREAM_RESOLUTION.split("x")
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src)]
    if not _has_audio(src):
        cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-shortest"]
    cmd += [
        "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
               f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,fps={config.STREAM_FPS}",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "44100", "-ac", "2",
        str(dest),
    ]
    subprocess.run(cmd, check=True)

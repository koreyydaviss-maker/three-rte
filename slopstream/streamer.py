"""Keeps a continuous RTMP feed to YouTube alive.

Plays clips from the queue in order; when the queue is empty, streams a
generated standby loop so YouTube never sees the feed drop. Each clip is
already normalized to the same format, so we stream-copy video (cheap) and
only encode when playing standby."""

import logging
import subprocess
import time

from slopstream import config

log = logging.getLogger("streamer")

RTMP_TARGET_TEMPLATE = "{url}/{key}"


def rtmp_target() -> str:
    if not config.YOUTUBE_STREAM_KEY:
        raise SystemExit("Set YOUTUBE_STREAM_KEY in .env (YouTube Studio → Go Live)")
    return RTMP_TARGET_TEMPLATE.format(url=config.YOUTUBE_RTMP_URL, key=config.YOUTUBE_STREAM_KEY)


def next_clip():
    clips = sorted(config.QUEUE_DIR.glob("*.mp4"))
    return clips[0] if clips else None


def stream_clip(path, target) -> None:
    log.info("streaming %s", path.name)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-re", "-i", str(path),
         "-c", "copy", "-f", "flv", target],
        check=True,
    )


def stream_standby(target, seconds: int = 10) -> None:
    log.info("queue empty — standby loop %ds", seconds)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-re",
         "-f", "lavfi", "-i",
         f"smptebars=size={config.STREAM_RESOLUTION}:rate={config.STREAM_FPS}",
         "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
         "-t", str(seconds),
         "-vf", "drawtext=text='generating more slop...':fontcolor=white:fontsize=36:"
                "box=1:boxcolor=black@0.6:x=(w-text_w)/2:y=(h-text_h)/2",
         "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
         "-g", str(config.STREAM_FPS * 2),
         "-c:a", "aac", "-f", "flv", target],
        check=True,
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    target = rtmp_target()
    while True:
        clip = next_clip()
        try:
            if clip is None:
                stream_standby(target)
            else:
                stream_clip(clip, target)
                clip.rename(config.PLAYED_DIR / clip.name)
        except subprocess.CalledProcessError:
            log.exception("ffmpeg failed; retrying in 5s")
            time.sleep(5)


if __name__ == "__main__":
    main()

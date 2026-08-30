"""Test provider: renders a color test-pattern clip with the prompt as an
overlay, using ffmpeg. Lets you verify the whole pipeline with zero API cost."""

import subprocess
from pathlib import Path

from slopstream import config


class MockProvider:
    def generate(self, prompt: str, out_path: Path) -> None:
        text = prompt.replace("'", "").replace(":", " ")[:80]
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error",
                "-f", "lavfi",
                "-i", f"testsrc2=size={config.STREAM_RESOLUTION}:rate={config.STREAM_FPS}",
                "-f", "lavfi",
                "-i", "sine=frequency=220:sample_rate=44100",
                "-t", str(config.CLIP_SECONDS),
                "-vf", f"drawtext=text='{text}':fontcolor=white:fontsize=28:"
                       "box=1:boxcolor=black@0.6:x=(w-text_w)/2:y=h-80",
                "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-shortest",
                str(out_path),
            ],
            check=True,
        )

"""Replicate text-to-video provider. Requires REPLICATE_API_TOKEN."""

from pathlib import Path

import requests

from slopstream import config
from slopstream.providers.util import download, transcode_to_stream_format


class ReplicateProvider:
    def generate(self, prompt: str, out_path: Path) -> None:
        import replicate

        output = replicate.run(config.REPLICATE_MODEL, input={"prompt": prompt})
        video_url = output if isinstance(output, str) else str(output)
        raw = out_path.with_suffix(".raw.mp4")
        download(video_url, raw, session=requests.Session())
        transcode_to_stream_format(raw, out_path)
        raw.unlink(missing_ok=True)

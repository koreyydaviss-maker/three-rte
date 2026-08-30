"""fal.ai text-to-video provider. Requires FAL_KEY; model set via FAL_MODEL."""

from pathlib import Path

import requests

from slopstream import config
from slopstream.providers.util import download, transcode_to_stream_format


class FalProvider:
    def generate(self, prompt: str, out_path: Path) -> None:
        import fal_client

        result = fal_client.subscribe(
            config.FAL_MODEL,
            arguments={"prompt": prompt},
        )
        video_url = result["video"]["url"]
        raw = out_path.with_suffix(".raw.mp4")
        download(video_url, raw, session=requests.Session())
        transcode_to_stream_format(raw, out_path)
        raw.unlink(missing_ok=True)

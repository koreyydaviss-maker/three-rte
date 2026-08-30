"""Continuously generates clips into the queue directory.

Reads the current prompt from PROMPT_FILE (written by the director from live
chat); falls back to random seed themes. Pauses when the queue is full."""

import logging
import time
import uuid

from slopstream import config, themes
from slopstream.providers import get_provider

log = logging.getLogger("generator")


def current_prompt() -> str:
    try:
        text = config.PROMPT_FILE.read_text().strip()
        if text:
            return text
    except FileNotFoundError:
        pass
    return themes.random_prompt()


def queue_size() -> int:
    return len(list(config.QUEUE_DIR.glob("*.mp4")))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    provider = get_provider()
    log.info("using provider: %s", config.VIDEO_PROVIDER)
    while True:
        if queue_size() >= config.MAX_QUEUE:
            time.sleep(5)
            continue
        prompt = current_prompt()
        log.info("generating: %s", prompt)
        tmp = config.QUEUE_DIR / f".tmp-{uuid.uuid4().hex}.mp4"
        final = config.QUEUE_DIR / f"{int(time.time())}-{uuid.uuid4().hex[:8]}.mp4"
        try:
            provider.generate(prompt, tmp)
            tmp.rename(final)  # atomic: streamer only ever sees complete files
            log.info("queued %s (queue=%d)", final.name, queue_size())
        except Exception:
            log.exception("generation failed; retrying in 15s")
            tmp.unlink(missing_ok=True)
            time.sleep(15)


if __name__ == "__main__":
    main()

"""Reads your YouTube live chat and decides what the AI generates next.

Viewers type:  !gen <prompt>
Each round (ROUND_SECONDS), the most recent valid suggestion wins and is
written to PROMPT_FILE for the generator. Repeated identical suggestions
within a round count as votes, so the most-suggested prompt wins ties."""

import logging
import time
from collections import Counter

import requests

from slopstream import config

log = logging.getLogger("director")

API = "https://www.googleapis.com/youtube/v3"
COMMAND = "!gen "
MAX_PROMPT_LEN = 300
BANNED_TERMS = {"nsfw", "nude", "gore"}  # crude guardrail; extend as needed


def get_live_chat_id() -> str:
    if not (config.YOUTUBE_API_KEY and config.YOUTUBE_VIDEO_ID):
        raise SystemExit("Set YOUTUBE_API_KEY and YOUTUBE_VIDEO_ID in .env")
    r = requests.get(
        f"{API}/videos",
        params={"part": "liveStreamingDetails", "id": config.YOUTUBE_VIDEO_ID,
                "key": config.YOUTUBE_API_KEY},
        timeout=30,
    )
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        raise SystemExit(f"Video {config.YOUTUBE_VIDEO_ID} not found")
    chat_id = items[0].get("liveStreamingDetails", {}).get("activeLiveChatId")
    if not chat_id:
        raise SystemExit("No active live chat — is the broadcast live?")
    return chat_id


def poll_messages(chat_id: str, page_token: str | None):
    params = {"liveChatId": chat_id, "part": "snippet", "key": config.YOUTUBE_API_KEY,
              "maxResults": 200}
    if page_token:
        params["pageToken"] = page_token
    r = requests.get(f"{API}/liveChat/messages", params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    texts = [
        item["snippet"].get("displayMessage", "")
        for item in data.get("items", [])
        if item["snippet"]["type"] == "textMessageEvent"
    ]
    return texts, data.get("nextPageToken"), data.get("pollingIntervalMillis", 5000) / 1000


def extract_prompt(message: str) -> str | None:
    if not message.lower().startswith(COMMAND):
        return None
    prompt = message[len(COMMAND):].strip()[:MAX_PROMPT_LEN]
    if not prompt or any(term in prompt.lower() for term in BANNED_TERMS):
        return None
    return prompt


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    chat_id = get_live_chat_id()
    log.info("watching live chat %s", chat_id)
    page_token = None
    round_start = time.time()
    suggestions: Counter[str] = Counter()
    while True:
        try:
            texts, page_token, wait = poll_messages(chat_id, page_token)
        except requests.RequestException:
            log.exception("chat poll failed; retrying in 10s")
            time.sleep(10)
            continue
        for text in texts:
            prompt = extract_prompt(text)
            if prompt:
                suggestions[prompt] += 1
                log.info("suggestion (+%d): %s", suggestions[prompt], prompt)
        if time.time() - round_start >= config.ROUND_SECONDS:
            if suggestions:
                winner = suggestions.most_common(1)[0][0]
                config.PROMPT_FILE.parent.mkdir(parents=True, exist_ok=True)
                config.PROMPT_FILE.write_text(winner)
                log.info("round winner: %s", winner)
            else:
                # No suggestions: clear so the generator falls back to seed themes.
                config.PROMPT_FILE.write_text("")
            suggestions.clear()
            round_start = time.time()
        time.sleep(max(wait, 2))


if __name__ == "__main__":
    main()

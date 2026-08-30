# SlopStream — an endless AI-generated TV channel for YouTube

An "infinite slop" pipeline: an AI video model generates short clips
continuously, an ffmpeg loop stitches them into a 24/7 RTMP livestream to
your YouTube channel, and your live chat decides what gets generated next.

```
YouTube live chat ──> director (collects !gen prompts, votes)
                          │ picks winning prompt
                          ▼
                     generator (fal.ai / MiniMax / Replicate)
                          │ writes .mp4 clips
                          ▼
                   clips/queue/ ──> streamer (ffmpeg) ──RTMP──> YouTube Live
```

## What you need

1. **A YouTube channel enabled for live streaming** (enable it in YouTube
   Studio → Go Live; first-time activation takes 24h).
2. **Your stream key** from YouTube Studio → Go Live → Stream settings.
3. **A video generation API key** — one of:
   - [fal.ai](https://fal.ai) (`FAL_KEY`) — recommended, hosts MiniMax/LTX/etc.
   - [Replicate](https://replicate.com) (`REPLICATE_API_TOKEN`)
4. **A YouTube Data API v3 key** (for reading live chat) from
   [Google Cloud Console](https://console.cloud.google.com/apis/library/youtube.googleapis.com).
5. `ffmpeg` installed (`apt install ffmpeg` / `brew install ffmpeg`).

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
```

## Run

Three processes (use tmux, or `honcho`/`foreman` with the included Procfile):

```bash
python -m slopstream.streamer    # keeps the RTMP feed to YouTube alive
python -m slopstream.generator   # generates clips into clips/queue/
python -m slopstream.director    # reads live chat, sets the next prompt
```

Start the streamer first — it broadcasts a standby loop until clips arrive,
so YouTube sees a continuous feed and the stream never goes offline.

### How chat controls the channel

Viewers type in your live chat:

```
!gen a cat detective flying a spaceship to the moon
```

The director tallies suggestions each round (default 60s). The prompt with
the most `+1` replies (or the most recent one, if no votes) is handed to the
generator. Between chat prompts, the generator riffs on a rotating list of
seed themes in `slopstream/themes.py` so the channel never goes quiet.

## Costs & practicalities

- Video generation is the dominant cost: roughly $0.02–$0.50 per 5–10s clip
  depending on the model. A 24/7 channel burns clips continuously, so start
  with scheduled streams (a few hours) before committing to always-on.
- YouTube requires streams to comply with its policies; AI content should be
  disclosed (YouTube Studio has an "altered content" disclosure setting).
- Latency: clips arrive 10–60s after generation starts; the queue plus the
  standby loop absorbs the gap.

## Configuration

All via `.env` — see `.env.example`. Key settings:

| Variable | Purpose |
|---|---|
| `YOUTUBE_STREAM_KEY` | RTMP ingest key from YouTube Studio |
| `YOUTUBE_API_KEY` | Data API key for live chat reading |
| `YOUTUBE_VIDEO_ID` | The video ID of your active live broadcast |
| `VIDEO_PROVIDER` | `fal`, `replicate`, or `mock` (testing, no API cost) |
| `FAL_KEY` / `REPLICATE_API_TOKEN` | Provider credentials |
| `CLIP_SECONDS` | Target clip length (default 6) |
| `ROUND_SECONDS` | How often chat's next prompt is picked (default 60) |

`VIDEO_PROVIDER=mock` generates colored test-pattern clips with ffmpeg so you
can verify the whole pipeline end-to-end without spending a cent.

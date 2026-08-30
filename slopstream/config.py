import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent

YOUTUBE_STREAM_KEY = os.getenv("YOUTUBE_STREAM_KEY", "")
YOUTUBE_RTMP_URL = os.getenv("YOUTUBE_RTMP_URL", "rtmp://a.rtmp.youtube.com/live2")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_VIDEO_ID = os.getenv("YOUTUBE_VIDEO_ID", "")

VIDEO_PROVIDER = os.getenv("VIDEO_PROVIDER", "mock")
FAL_KEY = os.getenv("FAL_KEY", "")
FAL_MODEL = os.getenv("FAL_MODEL", "fal-ai/minimax/hailuo-02/standard/text-to-video")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
REPLICATE_MODEL = os.getenv("REPLICATE_MODEL", "minimax/video-01")

CLIP_SECONDS = int(os.getenv("CLIP_SECONDS", "6"))
ROUND_SECONDS = int(os.getenv("ROUND_SECONDS", "60"))
QUEUE_DIR = ROOT / os.getenv("QUEUE_DIR", "clips/queue")
PLAYED_DIR = ROOT / os.getenv("PLAYED_DIR", "clips/played")
MIN_QUEUE = int(os.getenv("MIN_QUEUE", "2"))
MAX_QUEUE = int(os.getenv("MAX_QUEUE", "6"))
STREAM_RESOLUTION = os.getenv("STREAM_RESOLUTION", "1280x720")
STREAM_FPS = int(os.getenv("STREAM_FPS", "30"))

# File the director writes and the generator reads: the next prompt to render.
PROMPT_FILE = ROOT / "clips" / "next_prompt.txt"

QUEUE_DIR.mkdir(parents=True, exist_ok=True)
PLAYED_DIR.mkdir(parents=True, exist_ok=True)

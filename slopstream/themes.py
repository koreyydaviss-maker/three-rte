"""Seed themes the generator riffs on when chat hasn't suggested anything."""

import random

THEMES = [
    "a cat detective flying a spaceship through an asteroid field",
    "a cooking show where a robot chef makes dumplings, 1970s TV style",
    "an infomercial for a gadget that doesn't make sense, VHS quality",
    "nature documentary about tiny dragons living in a garden",
    "a news broadcast from an underwater city",
    "claymation dinosaurs running a coffee shop",
    "an 80s aerobics video but everyone is an astronaut",
    "a soap opera scene between two sentient houseplants",
    "surreal interdimensional cable commercial, absurd product",
    "a game show where contestants guess what clouds taste like",
]

STYLES = [
    "cinematic, 35mm film grain",
    "retro VHS, tracking artifacts",
    "saturday morning cartoon style",
    "hyperrealistic, dramatic lighting",
    "stop-motion claymation",
]


def random_prompt() -> str:
    return f"{random.choice(THEMES)}, {random.choice(STYLES)}"

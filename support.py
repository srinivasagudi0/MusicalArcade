"""
Helpers for the Streamlit games.

This project intentionally avoids returning song lyrics. Lyrics are copyrighted, and a
"guess the song" game works well using spoiler-free clues instead.
"""

import json
import os
import random
import re
from typing import Any, Dict

# A tiny offline dataset so the game works even without an API key.
# Keeping it small makes the project simple to run and easy to extend later.
FALLBACK_ROUNDS = [
    {
        "clue": "Clues:\n1) 1985 synth-pop hit.\n2) Famous for a rotoscoped/animated music video.\n3) Big falsetto chorus.",
        "answer_title": "Take On Me",
        "answer_artist": "a-ha",
    },
    {
        "clue": "Clues:\n1) Late 1970s rock stadium staple.\n2) Built around a stomp-stomp-clap rhythm.\n3) Often played at sports games.",
        "answer_title": "We Will Rock You",
        "answer_artist": "Queen",
    },
    {
        "clue": "Clues:\n1) Early 1990s grunge anthem.\n2) Quiet-loud dynamics with a huge chorus.\n3) Title references youth culture.",
        "answer_title": "Smells Like Teen Spirit",
        "answer_artist": "Nirvana",
    },
    {
        "clue": "Clues:\n1) Early 1980s pop classic.\n2) Linked to an iconic 'moonwalk' performance.\n3) Title is a woman's name.",
        "answer_title": "Billie Jean",
        "answer_artist": "Michael Jackson",
    },
    {
        "clue": "Clues:\n1) 2014 funk-pop mega-hit.\n2) A producer/DJ teamed up with a singer known for big retro vocals.\n3) Music video features sharp suits and dancing.",
        "answer_title": "Uptown Funk",
        "answer_artist": "Mark Ronson ft. Bruno Mars",
    },
    {
        "clue": "Clues:\n1) 2015 pop song built on a marimba-like hook.\n2) The title is also a body part.\n3) By a British singer-songwriter known for acoustic pop.",
        "answer_title": "Shape of You",
        "answer_artist": "Ed Sheeran",
    },
    {
        "clue": "Clues:\n1) Classic singalong often shouted at parties.\n2) The chorus names a woman.\n3) Frequently played at baseball games.",
        "answer_title": "Sweet Caroline",
        "answer_artist": "Neil Diamond",
    },
]


def normalize_guess(text: str) -> str:
    """Normalize a guess so punctuation/case differences don't matter."""
    normalized = text.strip().lower()
    # Example: "Take-On-Me!!!" -> "takeonme"
    normalized = re.sub(r"[^a-z0-9\s]", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def get_song_round() -> Dict[str, str]:
    """
    Get a new "Guess the Song" round.

    Returns a dict:
      - clue: spoiler-free clues (no lyrics)
      - answer_title: song title
      - answer_artist: artist

    If `OPENAI_API_KEY` isn't set, or the API call fails for any reason, we fall back to
    `FALLBACK_ROUNDS` so the app stays usable.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return random.choice(FALLBACK_ROUNDS)

    # Optional: override via env var without changing code.
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    system_prompt = (
        "You create short clues for a 'Guess the Song' game.\n"
        "- Do NOT quote or paraphrase lyrics.\n"
        "- Do NOT include the song title or artist in the clue.\n"
        "- Return ONLY strict JSON with keys: clue, answer_title, answer_artist.\n"
        "- clue should include 3 numbered clues."
    )

    try:
        from openai import OpenAI  # Optional dependency (only needed with an API key)

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": "Pick a well-known song and generate the JSON now.",
                },
            ],
            temperature=1,
        )

        content = (response.choices[0].message.content or "").strip()
        # We asked for strict JSON so parsing is predictable.
        data: Dict[str, Any] = json.loads(content)
        clue = str(data.get("clue", "")).strip()
        answer_title = str(data.get("answer_title", "")).strip()
        answer_artist = str(data.get("answer_artist", "")).strip()

        if not clue or not answer_title:
            raise ValueError("Missing required fields")

        # Quick safety check: the clue shouldn't accidentally contain the answer.
        clue_l = clue.lower()
        if answer_title and answer_title.lower() in clue_l:
            raise ValueError("Clue leaked the title")
        if answer_artist and answer_artist.lower() in clue_l:
            raise ValueError("Clue leaked the artist")

        return {"clue": clue, "answer_title": answer_title, "answer_artist": answer_artist}
    except Exception:
        # If anything goes wrong (network error, bad JSON, etc.), still return something playable.
        return random.choice(FALLBACK_ROUNDS)


def is_correct_guess(guess: str, answer_title: str) -> bool:
    """
    Simple matching logic for user guesses.

    Normalizes both strings, then checks:
    - exact match
    - substring match (helps with small differences like "the take on me song")
    """
    g = normalize_guess(guess)
    a = normalize_guess(answer_title)
    if not g or not a:
        return False
    return g == a or g in a or a in g


# Backwards-compatible name used by the old UI.
def get_random_song() -> str:
    # Old name kept so earlier versions of `app.py` still work.
    return get_song_round()["clue"]

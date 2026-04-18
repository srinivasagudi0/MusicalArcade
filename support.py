"""
Utility helpers and small datasets for the Streamlit music/rhythm games.

This module intentionally avoids copyrighted lyrics.
- "Guess the Song" uses clue‑based rounds.
- Fill‑in‑the‑blank uses traditional/public‑domain lines.
"""

import json
import os
import random
import re
from collections import Counter
from typing import Any, Dict, List


# ============================================================================
#  DATASETS
# ============================================================================

# Offline fallback rounds for "Guess the Song"
FALLBACK_ROUNDS = [
    {
        "clue": "Clues:\n1) 1985 synth‑pop hit.\n2) Rotoscoped music video.\n3) Big falsetto chorus.",
        "answer_title": "Take On Me",
        "answer_artist": "a‑ha",
    },
    {
        "clue": "Clues:\n1) Late 70s rock anthem.\n2) Stomp‑stomp‑clap.\n3) Played at sports games.",
        "answer_title": "We Will Rock You",
        "answer_artist": "Queen",
    },
    {
        "clue": "Clues:\n1) Early 90s grunge.\n2) Quiet‑loud‑quiet.\n3) Youth‑culture title.",
        "answer_title": "Smells Like Teen Spirit",
        "answer_artist": "Nirvana",
    },
    {
        "clue": "Clues:\n1) Early 80s pop.\n2) Linked to the moonwalk.\n3) Title is a woman's name.",
        "answer_title": "Billie Jean",
        "answer_artist": "Michael Jackson",
    },
    {
        "clue": "Clues:\n1) 2014 funk‑pop.\n2) Retro vocals + DJ producer.\n3) Suits + dancing video.",
        "answer_title": "Uptown Funk",
        "answer_artist": "Mark Ronson ft. Bruno Mars",
    },
    {
        "clue": "Clues:\n1) 2015 pop hit.\n2) Marimba‑like hook.\n3) British singer‑songwriter.",
        "answer_title": "Shape of You",
        "answer_artist": "Ed Sheeran",
    },
    {
        "clue": "Clues:\n1) Classic singalong.\n2) Chorus names a woman.\n3) Played at baseball games.",
        "answer_title": "Sweet Caroline",
        "answer_artist": "Neil Diamond",
    },
]

# Regex for extracting words
_WORD_RE = re.compile(r"[A-Za-z']+")

# Public‑domain lyric lines for fill‑in‑the‑blank
FILL_BLANK_ITEMS = [
    {"title": "Twinkle, Twinkle, Little Star", "artist": "Traditional",
     "line": "Twinkle, twinkle, little star, how I wonder what you are"},
    {"title": "Mary Had a Little Lamb", "artist": "Traditional",
     "line": "Mary had a little lamb, its fleece was white as snow"},
    {"title": "Row, Row, Row Your Boat", "artist": "Traditional",
     "line": "Row, row, row your boat, gently down the stream"},
    {"title": "London Bridge", "artist": "Traditional",
     "line": "London Bridge is falling down, falling down, falling down"},
    {"title": "Amazing Grace", "artist": "John Newton",
     "line": "Amazing grace! how sweet the sound, that saved a wretch like me"},
    {"title": "Auld Lang Syne", "artist": "Traditional (Robert Burns)",
     "line": "Should auld acquaintance be forgot, and never brought to mind"},
    {"title": "Oh! Susanna", "artist": "Stephen Foster",
     "line": "Oh! Susanna, don't you cry for me"},
    {"title": "Yankee Doodle", "artist": "Traditional",
     "line": "Yankee Doodle went to town, riding on a pony"},
]


# ============================================================================
#  NORMALIZATION HELPERS
# ============================================================================

def normalize_guess(text: str) -> str:
    """Lowercase, trim, and remove punctuation for easier matching."""
    cleaned = text.strip().lower()
    cleaned = re.sub(r"[^a-z0-9\s]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def is_correct_word_guess(guess: str, answer_word: str) -> bool:
    """Exact match after normalization."""
    return normalize_guess(guess) == normalize_guess(answer_word)


def is_correct_guess(guess: str, answer_title: str) -> bool:
    """
    Flexible matching for song titles:
    - exact match
    - substring match (helps with “that take on me song”)
    """
    g = normalize_guess(guess)
    a = normalize_guess(answer_title)
    if not g or not a:
        return False
    return g == a or g in a or a in g


# ============================================================================
#  FILL‑IN‑THE‑BLANK GENERATION
# ============================================================================

def _pick_blank_word(line: str) -> str:
    """Choose a good word to blank out from a lyric line."""
    words = _WORD_RE.findall(line)
    letter_words = [w for w in words if re.fullmatch(r"[A-Za-z]+", w or "")]
    if not letter_words:
        return ""

    counts = Counter(w.lower() for w in letter_words)

    # Prefer unique, longer words
    candidates = [w for w in letter_words if len(w) >= 4 and counts[w.lower()] == 1]
    if not candidates:
        candidates = [w for w in letter_words if counts[w.lower()] == 1] or letter_words

    return random.choice(candidates)


def get_fill_blank_round() -> Dict[str, Any]:
    """Create a fill‑in‑the‑blank question from the public‑domain list."""
    item = random.choice(FILL_BLANK_ITEMS)
    line = item["line"]

    answer_word = _pick_blank_word(line)
    if not answer_word:
        return {
            "prompt_line": line,
            "answer_word": "",
            "choices": [],
            "title": item["title"],
            "artist": item["artist"],
            "full_line": line,
        }

    # Replace chosen word with a blank
    match = re.search(rf"\b{re.escape(answer_word)}\b", line, flags=re.IGNORECASE)
    if not match:
        return {
            "prompt_line": line,
            "answer_word": "",
            "choices": [],
            "title": item["title"],
            "artist": item["artist"],
            "full_line": line,
        }

    prompt_line = f"{line[:match.start()]}____{line[match.end():]}"

    # Build distractor pool
    pool: List[str] = []
    for other in FILL_BLANK_ITEMS:
        pool.extend(_WORD_RE.findall(other["line"]))

    pool = [w for w in pool if normalize_guess(w) != normalize_guess(answer_word)]
    pool = list(dict.fromkeys(pool))  # de‑dupe

    distractors = random.sample(pool, k=min(3, len(pool)))
    choices = distractors + [answer_word]
    random.shuffle(choices)

    return {
        "prompt_line": prompt_line,
        "answer_word": answer_word,
        "choices": choices,
        "title": item["title"],
        "artist": item["artist"],
        "full_line": line,
    }


# ============================================================================
#  GUESS‑THE‑SONG GENERATION
# ============================================================================

def get_song_round() -> Dict[str, str]:
    """Generate a clue‑based round using OpenAI if available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return random.choice(FALLBACK_ROUNDS)

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    system_prompt = (
        "You create short clues for a 'Guess the Song' game.\n"
        "- No lyrics.\n"
        "- No title or artist leaks.\n"
        "- Return strict JSON: clue, answer_title, answer_artist.\n"
        "- Clue must contain 3 numbered hints."
    )

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Pick a well‑known song and generate the JSON."},
            ],
            temperature=1,
        )

        raw = (response.choices[0].message.content or "").strip()
        data = json.loads(raw)

        clue = str(data.get("clue", "")).strip()
        title = str(data.get("answer_title", "")).strip()
        artist = str(data.get("answer_artist", "")).strip()

        if not clue or not title:
            raise ValueError("Missing fields")

        # Safety: ensure clue doesn't leak answer
        low = clue.lower()
        if title.lower() in low or artist.lower() in low:
            raise ValueError("Clue leaked answer")

        return {"clue": clue, "answer_title": title, "answer_artist": artist}

    except Exception:
        return random.choice(FALLBACK_ROUNDS)


# ============================================================================
#  LEGACY COMPATIBILITY
# ============================================================================

def get_random_song() -> str:
    """Old helper kept for older versions of the UI."""
    return get_song_round()["clue"]


# ============================================================================
#  RHYTHM PATTERN HELPERS
# ============================================================================

def get_rhythm_pattern(length: int = 8, min_hits: int = 2, max_hits: int = 6) -> List[bool]:
    """
    Create a simple on/off rhythm pattern.
    True = hit (●)
    False = rest (○)
    """
    length = max(1, int(length))
    min_hits = max(0, min(int(min_hits), length))
    max_hits = max(min_hits, min(int(max_hits), length))

    hits = random.randint(min_hits, max_hits)
    pattern = [False] * length

    for idx in random.sample(range(length), k=hits):
        pattern[idx] = True

    return pattern


def pattern_to_dots(pattern: List[bool]) -> str:
    """Render a bool pattern as dots (●) and circles (○)."""
    return " ".join("●" if step else "○" for step in pattern)


def rhythm_accuracy(guess: List[bool], answer: List[bool]) -> Dict[str, int]:
    """Return simple accuracy stats for a guessed pattern."""
    total = min(len(guess), len(answer))
    correct = sum(1 for i in range(total) if guess[i] == answer[i])
    return {"correct": correct, "total": total}

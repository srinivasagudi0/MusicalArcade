import streamlit as st
import time

from support import (
    get_fill_blank_round,
    get_rhythm_pattern,
    get_song_round,
    is_correct_guess,
    is_correct_word_guess,
    pattern_to_dots,
    rhythm_accuracy,
)

# ---------------------------------------------------------------------------
#  Page Setup
# ---------------------------------------------------------------------------

st.title("Game Library")
st.write("Pick a game from the sidebar to get started.")

st.sidebar.title("What game are you looking for?")
game_choice = st.sidebar.selectbox(
    "Select a game",
    ["Guess the Song", "Lyric Fill-in-the-Blank", "Rhythm Pattern Copy"],
)

# ---------------------------------------------------------------------------
#  Guess the Song
# ---------------------------------------------------------------------------

def render_guess_the_song():
    st.header("Guess the Song")
    st.write("Read the clues and try to guess the song title.")

    # Initialize state
    if "song_round" not in st.session_state:
        st.session_state.song_round = get_song_round()
        st.session_state.revealed = False
        st.session_state.correct_this_round = False

    st.session_state.setdefault("score", 0)

    def new_round():
        st.session_state.song_round = get_song_round()
        st.session_state.revealed = False
        st.session_state.correct_this_round = False
        st.session_state.guess = ""

    # Controls
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.button("New Song", on_click=new_round)
    with col_b:
        st.caption(f"Score: {st.session_state.score}")

    # Clue
    st.write(st.session_state.song_round["clue"])

    # Guess input
    st.text_input("Your guess (song title)", key="guess", placeholder="Type the song title…")

    # Check + Reveal
    check_col, reveal_col = st.columns(2)

    with check_col:
        if st.button("Check Guess"):
            title = st.session_state.song_round["answer_title"]
            if is_correct_guess(st.session_state.guess, title):
                if not st.session_state.correct_this_round:
                    st.session_state.score += 1
                    st.session_state.correct_this_round = True
                st.success("Correct!")
            else:
                st.error("Not quite. Try again or reveal the answer.")

    with reveal_col:
        if st.button("Reveal Answer"):
            st.session_state.revealed = True

    if st.session_state.revealed:
        t = st.session_state.song_round["answer_title"]
        a = st.session_state.song_round["answer_artist"]
        st.info(f"Answer: {t} - {a}")


# ---------------------------------------------------------------------------
#  Lyric Fill‑in‑the‑Blank
# ---------------------------------------------------------------------------

def render_fill_blank():
    st.header("Song Lyric Fill‑in‑the‑Blank")
    st.write("One word is missing - type it or pick from the choices.")
    st.caption("Demo uses public‑domain lines. Add more in support.py → FILL_BLANK_ITEMS.")

    # Init state
    if "fib_round" not in st.session_state:
        st.session_state.fib_round = get_fill_blank_round()
        st.session_state.fib_revealed = False
        st.session_state.fib_correct_this_round = False

    st.session_state.setdefault("fib_score", 0)
    st.session_state.setdefault("fib_method", "Type it")

    def new_round():
        st.session_state.fib_round = get_fill_blank_round()
        st.session_state.fib_revealed = False
        st.session_state.fib_correct_this_round = False
        st.session_state.pop("fib_guess", None)
        st.session_state.pop("fib_choice", None)

    # Controls
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.button("New Lyric", on_click=new_round)
    with col_b:
        st.caption(f"Score: {st.session_state.fib_score}")

    # Prompt
    st.subheader("Lyric")
    st.write(st.session_state.fib_round["prompt_line"])

    # Answer method
    st.radio(
        "Answer method",
        ["Type it", "Pick from choices"],
        key="fib_method",
        horizontal=True,
    )

    # Input
    if st.session_state.fib_method == "Pick from choices":
        choices = st.session_state.fib_round.get("choices", [])
        if choices:
            guess = st.selectbox("Pick the missing word", choices, key="fib_choice")
        else:
            st.warning("No choices available - try typing instead.")
            guess = ""
    else:
        guess = st.text_input("Type the missing word", key="fib_guess")

    # Check + Reveal
    check_col, reveal_col = st.columns(2)

    with check_col:
        if st.button("Check"):
            answer = st.session_state.fib_round.get("answer_word", "")
            if not answer:
                st.error("This lyric didn't generate a blank. Try a new one.")
            elif is_correct_word_guess(guess, answer):
                if not st.session_state.fib_correct_this_round:
                    st.session_state.fib_score += 1
                    st.session_state.fib_correct_this_round = True
                st.success("Correct!")
            else:
                st.error("Not quite. Try again or reveal the answer.")

    with reveal_col:
        if st.button("Reveal"):
            st.session_state.fib_revealed = True

    if st.session_state.fib_revealed:
        ans = st.session_state.fib_round["answer_word"]
        title = st.session_state.fib_round["title"]
        artist = st.session_state.fib_round["artist"]
        full = st.session_state.fib_round["full_line"]

        st.info(f"Missing word: {ans}")
        st.write(full)
        st.caption(f"{title} - {artist}")


# ---------------------------------------------------------------------------
#  Rhythm Pattern Copy
# ---------------------------------------------------------------------------

def render_rhythm_copy():
    st.header("Rhythm Pattern Copy")
    st.write("Memorize the pattern, then copy it from memory (● = hit, ○ = rest).")

    # Init state
    if "rhythm_pattern" not in st.session_state:
        st.session_state.rhythm_pattern = get_rhythm_pattern(length=8)
        st.session_state.rhythm_correct_this_round = False
        st.session_state.rhythm_phase = "idle"
        st.session_state.rhythm_show_started_at = 0.0
        st.session_state.rhythm_guess_deadline = 0.0

    st.session_state.setdefault("rhythm_score", 0)

    pattern = st.session_state.rhythm_pattern
    length = len(pattern)

    def reset_pattern():
        st.session_state.rhythm_pattern = get_rhythm_pattern(length)
        st.session_state.rhythm_correct_this_round = False
        st.session_state.rhythm_phase = "idle"
        st.session_state.rhythm_show_started_at = 0.0
        st.session_state.rhythm_guess_deadline = 0.0
        for i in range(length):
            st.session_state.pop(f"rhythm_step_{i}", None)

    # Controls
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.button("New Pattern", on_click=reset_pattern)
    with col_b:
        st.caption(f"Score: {st.session_state.rhythm_score}")

    SHOW_SECONDS = 3
    GUESS_SECONDS = 10

    def start_show():
        st.session_state.rhythm_phase = "showing"
        st.session_state.rhythm_show_started_at = time.time()
        st.session_state.rhythm_correct_this_round = False
        for i in range(length):
            st.session_state.pop(f"rhythm_step_{i}", None)

    def start_guess():
        st.session_state.rhythm_phase = "guessing"
        st.session_state.rhythm_guess_deadline = time.time() + GUESS_SECONDS

    # Phase: idle
    if st.session_state.rhythm_phase == "idle":
        st.button("Start Challenge", on_click=start_show)
        st.caption(f"You get {SHOW_SECONDS}s to look, then {GUESS_SECONDS}s to copy.")

    # Phase: showing
    if st.session_state.rhythm_phase == "showing":
        title_slot = st.empty()
        pattern_slot = st.empty()
        caption_slot = st.empty()
        bar = st.progress(0.0)

        start = st.session_state.rhythm_show_started_at
        while True:
            elapsed = time.time() - start
            if elapsed >= SHOW_SECONDS:
                break

            title_slot.subheader("Memorize (pattern visible)")
            pattern_slot.write(pattern_to_dots(pattern))
            caption_slot.caption(f"Time left: {int(SHOW_SECONDS - elapsed) + 1}s")
            bar.progress(min(1.0, elapsed / SHOW_SECONDS))
            time.sleep(0.1)

        bar.progress(1.0)
        start_guess()
        st.rerun()

    # Phase: guessing or done
    if st.session_state.rhythm_phase in ("guessing", "done"):
        st.subheader("Your copy (pattern hidden)")

        if st.session_state.rhythm_phase == "guessing":
            time_left = max(0, int(st.session_state.rhythm_guess_deadline - time.time()))
            st.caption(f"Time left: {time_left}s")
            if st.button("Refresh timer"):
                st.rerun()
        else:
            st.caption("Round finished.")

        # Checkboxes for user guess
        cols = st.columns(length)
        for i, col in enumerate(cols):
            with col:
                st.checkbox(f"{i+1}", key=f"rhythm_step_{i}")

        guess = [bool(st.session_state.get(f"rhythm_step_{i}", False)) for i in range(length)]
        st.write(pattern_to_dots(guess))

        if st.button("Check"):
            if st.session_state.rhythm_phase != "guessing":
                st.info("Start a new challenge to play again.")
                return

            if time.time() > st.session_state.rhythm_guess_deadline:
                st.session_state.rhythm_phase = "done"
                st.error("Time's up!")
            else:
                stats = rhythm_accuracy(guess, pattern)
                st.session_state.rhythm_phase = "done"

                if stats["correct"] == stats["total"]:
                    if not st.session_state.rhythm_correct_this_round:
                        st.session_state.rhythm_score += 1
                        st.session_state.rhythm_correct_this_round = True
                    st.success("Perfect copy!")
                else:
                    st.warning(f"Accuracy: {stats['correct']}/{stats['total']}")

            st.write("Correct pattern:")
            st.write(pattern_to_dots(pattern))


# ---------------------------------------------------------------------------
#  Router
# ---------------------------------------------------------------------------

if game_choice == "Guess the Song":
    render_guess_the_song()

elif game_choice == "Lyric Fill-in-the-Blank":
    render_fill_blank()

elif game_choice == "Rhythm Pattern Copy":
    render_rhythm_copy()

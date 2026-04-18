import streamlit as st
from support import get_song_round, is_correct_guess

# Simple game hub. For now there's only one game, but the sidebar is set up to add more later.

st.title("Game Library")
st.write("Pick a game from the sidebar.")

st.sidebar.title("What game are you looking for?")
game_choice = st.sidebar.selectbox("Select a game", ["Guess the Song"])
if game_choice == "Guess the Song":
    # --- Guess the Song (simple MVP) ---
    st.header("Guess the Song")
    st.write("Read the clues and guess the song!")

    # Streamlit reruns the script top-to-bottom on every interaction, so we keep state in `st.session_state`.
    if "song_round" not in st.session_state:
        # First load: start a round and reset per-round flags.
        st.session_state.song_round = get_song_round()
        st.session_state.revealed = False
        st.session_state.correct_this_round = False
    if "score" not in st.session_state:
        st.session_state.score = 0

    def new_round() -> None:
        """Start a new song and clear the input + per-round state."""
        st.session_state.song_round = get_song_round()
        st.session_state.revealed = False
        st.session_state.correct_this_round = False
        st.session_state.guess = ""

    controls_col, score_col = st.columns([1, 2])
    with controls_col:
        st.button("New Song", on_click=new_round)
    with score_col:
        st.caption(f"Score: {st.session_state.score}")

    # Show spoiler-free clues (no lyrics).
    st.write(st.session_state.song_round["clue"])

    # We store the text box value in session state so it survives reruns.
    st.text_input("Your guess (song title)", key="guess", placeholder="Type the song title…")

    check_col, reveal_col = st.columns(2)
    with check_col:
        if st.button("Check Guess"):
            if is_correct_guess(st.session_state.guess, st.session_state.song_round["answer_title"]):
                # Only award points once per round.
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
        # Once revealed, show the answer (title + artist).
        title = st.session_state.song_round["answer_title"]
        artist = st.session_state.song_round["answer_artist"]
        st.info(f"Answer: {title} — {artist}")

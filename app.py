import streamlit as st
import time
from support import get_random_song

# i dont know what games to add the games will now only be placeholder and I will search for games to add later

st.title("Game Library")
st.write("deciding games...")

st.sidebar.title("What game are you looking for?")
game_choice = st.sidebar.selectbox("Select a game", ["Guess the Song"])
if game_choice == "Guess the Song":
    # It is going to be good and simple
    st.header("Guess the Song")
    st.write("See the lyrics and guess the song!")
    st.write(get_random_song())

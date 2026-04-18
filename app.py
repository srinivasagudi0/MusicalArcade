import streamlit as st
import time

# i dont know what games to add the games will now only be placeholder and I will search for games to add later

st.title("Game Library")
st.write("deciding games...")

st.sidebar.title("What game are you looking for?")
game_choice = st.sidebar.selectbox("Select a game", ["Guess the Song"])
if game_choice="Guess the Song":
    # It is goign to be good and simple

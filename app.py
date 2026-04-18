import streamlit as st
import time

# i dont know what games to add the games will now only be placeholder and I will search for games to add later

st.title("Game Library")
st.write("deciding games...")

st.sidebar.title("What game are you looking for?")
game_choice = st.sidebar.selectbox("Select a game", ["Beat Tap"])

if game_choice == "Beat Tap":
    '''
    simplest music-related option:

Play a song beat track
Show a cue (flash/circle) on each beat
Player taps in time
Score based on timing accuracy (Perfect/Good/Miss)

THis will be the first game I add to the library, I will add more games later on but for now this is the only game in the library
    '''
from openai import OpenAI
import os

def get_random_song():
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides random song lyrics. Just give lyrics only, no comments or explanations. Dont say what song it is or who sings it. I will try to guess it."},
            {"role": "user", "content": "Give me the lyrics of a random song."}
        ]
    )
    return response.choices[0].message.content

print(get_random_song())

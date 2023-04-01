"""
Created by: Eugene Cho
Date created: April 1, 2023

file containing the top level functions for Versify
"""
import cohere
from discography import Discography, Song
from sqlite3 import connect, Cursor, Connection
import openai
import tiktoken

def get_api_keys() -> tuple[str, str]:

    with open('keys.txt', 'r') as file:
        cohere_apikey = file.readline().strip()
        openai_apikey = file.readline().strip()

    return cohere_apikey, openai_apikey


def generate_discography(artist_name: str) -> Discography | None:
    """
    """
    cohere_apikey, openai.api_key = get_api_keys()
    co = cohere.Client(cohere_apikey)

    conn, curr = connect_to_database()
    songs = get_songs(artist_name, curr)

    if songs == []:
        return None

    discography = Discography(artist_name)

    for i in range(min(100, len(songs))):
        title = songs[i][0]
        lyrics = songs[i][1]
        embedding = co.embed([lyrics]).embeddings[0]
        discography.add_song(title, lyrics, embedding)

    discography.match_all_similarities()

    conn.close()   # Close the connection to the database
    return discography

def generate_song_title(lyrics: str) -> str:
    """"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a song title generator based on given song lyrics"},
            {"role": "user", "content": f"Create an appopriate song title for these lyrics: {lyrics}. Make sure"
                                        f"to give only the song name and no other additional text."},
        ]
    )

    title = response.choices[0]['message']['content']
    return title

def generate_song(discography: Discography) -> str:
    """Uses ChatGPT API to generate a return a new song
    lyric using the given songs lyrics as prompts for the generation
    """
    song_prompts = list(discography.top_five_songs())
    song_lyrics = ''
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    for song in song_prompts:
        song_lyrics += f'----------{song.title}----------\n'
        song_lyrics += song.lyrics

    system_description_content = 'You generate lyrics of a song in the style of example songs that you are given.'
    prompt = f"Write a unique and original song lyrics in a similar style to that of the following songs: " \
             f"{song_lyrics}." \
             f" Ensure that the lyrics are completely original! Don't reuse phrasing from the given lyrics. " \
             f"Remove any additional text that is not a part of the lyrics!"

    num_tokens = len(encoding.encode(system_description_content + prompt))

    while num_tokens >= 3200:
        song_prompts.pop()
        song_lyrics = ''

        for song in song_prompts:
            song_lyrics += f'----------{song.title}----------\n'
            song_lyrics += song.lyrics

        system_description_content = 'You generate lyrics of a song in the style of example songs that you are given.'
        prompt = f"Write a unique and original song lyrics in a similar style to that of the following songs: " \
                 f"{song_lyrics}." \
                 f" Ensure that the lyrics are completely original! Don't reuse phrasing from the given lyrics. " \
                 f"Remove any additional text that is not a part of the lyrics!"

        num_tokens = len(encoding.encode(system_description_content + prompt))

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=800,
        messages=[
            {"role": "system", "content": system_description_content},
            {"role": "user", "content": prompt},
        ]
    )

    lyrics = response.choices[0]['message']['content']
    return lyrics


def connect_to_database() -> tuple[Connection, Cursor]:
    """Returns the cursor"""
    conn = connect('lyrics_ds.db')
    curr = conn.cursor()
    return conn, curr


def get_songs(artist_name: str, curr: Cursor) -> list[tuple[str, str]]:
    """
    """
    curr.execute('SELECT title, lyrics FROM songs WHERE artist = ? COLLATE NOCASE ORDER BY views DESC',
                 (artist_name.lower(),))
    return curr.fetchall()

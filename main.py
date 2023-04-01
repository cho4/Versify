"""something"""
from lyricsgenius import Genius
import cohere
from discography import Discography, Song
from sqlite3 import connect, Cursor, Connection
import openai
import tiktoken

cohere_apikey = 'qiqWWzNgpO0oJ5pzLu21ETOuC37beHi6ON0XaigM'
openai.api_key = ''
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
model_engine = "gpt-3.5-turbo"
co = cohere.Client(cohere_apikey)


def generate_discography(artist_name: str) -> Discography:
    """
    """
    conn, curr = connect_to_database()
    songs = get_songs(artist_name, curr)
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
            {"role": "user", "content": f"Create an appopriate song title for these lyrics: {lyrics}"},
        ]
    )

    title = response.choices[0]['message']['content']
    return title

def generate_song(discography: Discography) -> str:
    """Uses ChatGPT API to generate a return a new song
    lyric using the given songs lyrics as prompts for the generation
    """
    song_prompts = discography.top_five_songs()
    lyrics = ''

    for song in song_prompts:
        lyrics += f'----------{song.title}----------\n'
        lyrics += song.lyrics

    num_tokens = len(encoding.encode(lyrics))
    # if num_tokens >

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You generate lyrics of a song in the style "
                                          "of example songs that you are given."},
            {"role": "user", "content": f"Write a unique and original song lyrics in a similar style to that "
                                        f"of the following songs: {lyrics}. Ensure that the lyrics are completely"
                                        f"original! Don't reuse phrasing from the given lyrics. Remove any additional"
                                        f"text that is not a part of the lyrics!"},
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
    curr.execute('SELECT title, lyrics FROM songs WHERE artist = ?', (artist_name,))
    return curr.fetchall()

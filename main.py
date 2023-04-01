"""something"""
from lyricsgenius import Genius
import cohere
from discography import Discography, Song
from sqlite3 import connect, Cursor, Connection
import openai

cohere_apikey = 'qiqWWzNgpO0oJ5pzLu21ETOuC37beHi6ON0XaigM'
openai.api_key = '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'
model_engine = "gpt-3.5-turbo"
co = cohere.Client(cohere_apikey)


def generate_discography(artist_name: str) -> Discography:
    """
    """
    conn, curr = connect_to_database()
    songs = get_songs(artist_name, curr)
    discography = Discography(artist_name)

    for song in songs:
        title = song[0]
        lyrics = song[1]
        embedding = co.embed([lyrics]).embeddings[0]
        discography.add_song(title, lyrics, embedding)

    discography.match_all_similarities()

    conn.close()   # Close the connection to the database
    return discography

def generate_song_title(discography: Discography) -> str:
    """"""
    return 'Hi my name is Joe'

def generate_song(discography: Discography) -> str:
    """Uses ChatGPT API to generate a return a new song
    lyric using the given songs lyrics as prompts for the generation
    """

    song_prompts = discography.top_five_songs()

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You generate lyrics of a song in the style "
                                          "of example songs that you are given."},
            {"role": "user", "content": f"Write song lyrics in the style of this song: {song_prompts[0].lyrics}"}
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

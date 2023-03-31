"""something"""
from lyricsgenius import Genius
import cohere
from discography import Discography
from sqlite3 import connect, Cursor

cohere_apikey = 'qiqWWzNgpO0oJ5pzLu21ETOuC37beHi6ON0XaigM'
co = cohere.Client(cohere_apikey)


def generate_discography(artist_name: str) -> Discography:
    """
    """
    curr = connect_to_database()
    songs = get_songs(artist_name, curr)
    discography = Discography(artist_name)

    for song in songs:
        title = song[0]
        lyrics = song[1]
        embedding = co.embed([lyrics]).embeddings[0]
        discography.add_song(title, lyrics, embedding)



    return discography

def connect_to_database() -> Cursor:
    """Returns the cursor"""
    conn = connect('lyrics_ds.db')
    curr = conn.cursor()
    return curr


def get_songs(artist_name: str, curr: Cursor) -> list[tuple[str, str]]:
    """
    """
    curr.execute('SELECT title, lyrics FROM songs WHERE artist = ?', (artist_name,))
    return curr.fetchall()

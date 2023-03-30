from lyricsgenius import Genius
import cohere

genius_apikey = '2YNVCh64u2_spmTHbvnNAob6wyXkTwe7yB90UsERleejLKwafWbGAl_R-TWK8pL8'
cohere_apikey = 'qiqWWzNgpO0oJ5pzLu21ETOuC37beHi6ON0XaigM'

genius = Genius(genius_apikey)
co = cohere.Client(cohere_apikey)

class Discography:

    def __init__(self, artist_name: str) -> None:
        """
        """
        self.artist_name = artist_name
        self.songs = {}

    def add_song(self, title, lyrics, embedding) -> None:
        """
        """
        song = Song(title, lyrics, embedding)
        self.songs[title] = song

class Song:

    def __init__(self, title: str, lyrics: str, embedding: list[float]) -> None:
        self.title = title
        self.lyrics = lyrics
        self.embedding = embedding
        self.similar_songs = {}

def generate_discography(artist_name: str) -> Discography:
    """
    """
    artist = genius.search_artist(artist_name, max_songs=3)
    songs = artist.songs

    discography = Discography(artist.name)

    for song in songs:
        title = song.title
        lyrics = song.lyrics
        embedding = co.embed([lyrics]).embeddings[0]

        discography.add_song(title, lyrics, embedding)

    return discography

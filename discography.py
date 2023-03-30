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

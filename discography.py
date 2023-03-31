"""classes of Song and Discography"""
import cohere
import numpy as np


class Discography:
    """
    Discography Class represented by a Graph datastructure
    """

    def __init__(self, artist_name: str) -> None:
        """
        Discography initializer
        """
        self.artist_name = artist_name
        self.songs = {}

    def add_song(self, title, lyrics, embedding) -> None:
        """
        Creates a Song object
        """
        song = Song(title, lyrics, embedding)
        self.songs[title] = song

    def add_similarity_edge(self, song1: Song, song2: Song) -> None:
        """
        Add an edge between song1 and song2
        """
        song1.similar_songs[song2.title] = song2
        song2.similar_songs[song1.title] = song1

    def match_all_similarities(self) -> None:
        """
        Traverses through self.songs and creates edge for all lyrically similar songs
        """
        threshold = 0.8

        for song1 in self.songs:
            for song2 in self.songs:
                if song1 != song2:
                    if song1.lyrical_similarity(song2) > threshold:
                        self.add_similarity_edge(song1, song2)

    def top_five_songs(self) -> tuple[Song]:
        """
        Return the top five songs in the Discography with the highest degrees
        """
        top_five = []
        songs = [song for song in self.songs.values()]
        degrees = [len(song.similar_songs) for song in self.songs.values()]
        for _ in range(5):
            k = max(degrees)
            i = degrees.index(k)
            degrees.pop(i)
            song = songs.pop(i)
            top_five.append(song)

        return tuple(top_five)


class Song:

    def __init__(self, title: str, lyrics: str, embedding: list[float]) -> None:
        self.title = title
        self.lyrics = lyrics
        self.embedding = embedding
        self.similar_songs = {}

    def lyrical_similarity(self, other: Song) -> float:
        """
        Returns a float between 0 and 1 based on how lyrically similar self is to other based on comparing
        their self.embedding values
        """
        a = self.embedding
        b = other.embedding
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

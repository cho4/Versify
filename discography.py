"""
Created by: Hamin Lee
Date created: April 1, 2023

file containing the Song and Discography class for Versify
"""
from __future__ import annotations
import numpy as np

class Song:
    """
    Song class for Versify Project

    This class creates a song object that holds information about its title, lyrics, and embedding.

    Embedding is a list of floats created from cohere library that is going to be used to compare two distinct Song
    objects

    Representation Invariants:
    - title and lyrics are matching of the actual song
    - embedding is created from cohere API call
    - all songs in similar_songs have the same artist
    """
    title: str
    lyrics: str
    embedding: list[float]
    similar_songs: dict[str, Song]

    def __init__(self, title: str, lyrics: str, embedding: list[float]) -> None:
        """
        Song initializer

        Preconditions:
        - title != ''
        - lyrics != ''
        - embedding != []
        """
        self.title = title
        self.lyrics = lyrics
        self.embedding = embedding
        self.similar_songs = {}

    def lyrical_similarity(self, other: Song) -> float:
        """
        Returns a float between 0 and 1 based on how lyrically similar self is to other based on comparing
        their self.embedding values

        Preconditions:
        - self.embedding != []
        - other.embedding != []
        """
        a = self.embedding
        b = other.embedding
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

class Discography:
    """
    Discography Class represented by a Graph datastructure

    Representation Invariants:
    - artist_name is of an artist in given database
    - song in songs are all from the same artist
    """
    artist_name: str
    songs: dict[str, Song]

    def __init__(self, artist_name: str) -> None:
        """
        Discography initializer

        Preconditions:
        - artist_name != ''
        """
        self.artist_name = artist_name
        self.songs = {}

    def add_song(self, title: str, lyrics: str, embedding: list[float]) -> None:
        """
        Creates a Song object

        Preconditions:
        - title != ''
        - lyrics != ''
        - embedding != []
        """
        song = Song(title, lyrics, embedding)
        self.songs[title] = song

    def add_similarity_edge(self, song1: Song, song2: Song) -> None:
        """
        Add an edge between song1 and song2

        Preconditions:
        - song1 is not song2
        """
        song1.similar_songs[song2.title] = song2
        song2.similar_songs[song1.title] = song1

    def match_all_similarities(self) -> None:
        """
        Traverses through self.songs and creates edge for all lyrically similar songs

        Preconditions:
        - len(self.songs) > 0
        """
        threshold = 0.6

        for song1 in self.songs:
            for song2 in self.songs:
                if song1 != song2:
                    if self.songs[song1].lyrical_similarity(self.songs[song2]) > threshold:
                        self.add_similarity_edge(self.songs[song1], self.songs[song2])

    def top_five_songs(self) -> list[Song]:
        """
        Return the top five songs in the Discography with the highest degrees

        Preconditions:
        - len(self.songs.values()) > 0
        """
        top_five = []
        songs = [song for song in self.songs.values()]
        degrees = [len(song.similar_songs) for song in self.songs.values()]
        for _ in range(min(5, len(self.songs))):
            k = max(degrees)
            i = degrees.index(k)
            degrees.pop(i)
            song = songs.pop(i)
            top_five.append(song)

        return top_five

"""Versify: The FUTURE of Songwriting (Classes)

Created by: Hamin Lee
Date created: April 1, 2023

General Information
===============================

Versify aims to utilize natural language processing and lyrical databases to generate completely new song lyrics in the
style of a given musical artist. This will be entirely based on their most commonly used vocabulary and semantic
patterns which are derived from existing songs.

This file contains the Song and Discography class for Versify
Discography objects model a graph and Song objects model a vertex/node

Copyright and Usage Information
===============================

This file is Copyright (c) 2023 Hamin Lee, Eugene Cho.
"""
from __future__ import annotations
import numpy as np


class Song:
    """
    Song class for Versify Project

    This class creates a song object that holds information about its title, lyrics, and embedding.

    Instance Attributes:
        - title: title of the Song
        - lyrics: lyrics of the Song
        - embedding: a list of floats generated by cohere that is used to compare two distinct Song objects
        - similar_songs: a dictionary that stores other songs that are similar to self (they share an edge)

    Representation Invariants:
        - title and lyrics are matching of the actual song
        - embedding is created from cohere API call
        - all songs in similar_songs have the same artist
        - all(self in song.similar_songs for song in self.similar_songs.values())
        - self not in self.similar_songs
        - all(title == song.title for title, song in self.similar_songs.items())
    """
    title: str
    lyrics: str
    embedding: list[float]
    similar_songs: dict[str, Song]

    def __init__(self, title: str, lyrics: str, embedding: list[float]) -> None:
        """
        Song initializer

        It is initialized with given title, lyrics, embedding and no connection to any other Song

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
        # computation taken from https://docs.cohere.ai/docs/embeddings
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class Discography:
    """
    Discography Class of a single artist represented by a Graph datastructure

    Instance Attributes:
        - artist_name: name of the artist's Discography
        - songs: mapping of song title to Song object up to 100 songs of the artist

    Representation Invariants:
        - artist_name is of an artist in given database
        - song in songs are all from the same artist
        - all(title == self.songs[title].title for title in self.songs)
    """
    artist_name: str
    songs: dict[str, Song]

    def __init__(self, artist_name: str) -> None:
        """
        Discography initializer

        Initializes Discography with the given name as self.artist_name and starts with 0 songs.

        Preconditions:
            - artist_name != ''
        """
        self.artist_name = artist_name
        self.songs = {}

    def add_song(self, title: str, lyrics: str, embedding: list[float]) -> None:
        """
        Creates a Song object for the artist with given arguments, and adds it to self.songs

        Preconditions:
            - title != ''
            - lyrics != ''
            - embedding != []
        """
        song = Song(title, lyrics, embedding)
        self.songs[title] = song

    def add_similarity_edge(self, song1: Song, song2: Song) -> None:
        """
        Adds an edge between song1 and song2

        This ultimately adds each song into others Song.similar_songs

        Preconditions:
            - song1 is not song2
        """
        song1.similar_songs[song2.title] = song2
        song2.similar_songs[song1.title] = song1

    def match_all_similarities(self) -> None:
        """
        Traverses through self.songs and creates an edge for all "lyrically similar" songs

        Do nothing if this Discography has 5 or fewer songs.

        Note: We do nothing if the Discography has 5 or fewer songs, since we would then be
        using all of the songs in the Discography for the lyric generation prompt anyways.

        Preconditions:
            - len(self.songs) > 0
        """
        if len(self.songs) > 5:
            threshold = 0.75

            for song1 in self.songs:
                for song2 in self.songs:
                    if song1 != song2 and self.songs[song1].lyrical_similarity(self.songs[song2]) > threshold:
                        self.add_similarity_edge(self.songs[song1], self.songs[song2])

    def top_five_songs(self) -> list[Song]:
        """
        Return the top five songs in the Discography with the highest degrees

        If this Discography has 5 or fewer songs, then all of this Discography's songs are simply returned.

        Preconditions:
            - len(self.songs.values()) > 0
        """
        if len(self.songs) <= 5:
            return list(self.songs.values())
        else:
            top_five = []
            # separate lists of songs and their corresponding degrees
            songs = list(self.songs.values())
            degrees = [len(s.similar_songs) for s in self.songs.values()]

            for _ in range(5):
                k = max(degrees)
                i = degrees.index(k)
                degrees.pop(i)
                song = songs.pop(i)
                top_five.append(song)

            return top_five


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['__future__', 'numpy'],
        'allowed-io': [],
        'max-line-length': 120,
        'disable': ['too-many-nested-blocks']
    })

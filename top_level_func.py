"""
Created by: Eugene Cho
Date created: April 1, 2023

file containing the top level functions for Versify
"""
from sqlite3 import connect, Cursor, Connection
import sqlite3
import cohere
import openai
import tiktoken
from discography import Discography, Song


# ----------------- MAIN TOP LEVEL FUNCTIONS -----------------
def generate_discography(artist_name: str) -> Discography | str:
    """Returns a complete Discography graph of the songs of a given artist
    with "similar" Songs sharing edges.

    Or if an error occurs while trying to create the Discography, a string is returned
    indicating why the error occured.

    "API_ERROR" is returned if there is an issue accessing either cohere or openai API.

    "ARTIST_ERROR" is returned if the given artist cannot be found in the lyrics_ds.db database.

    "DATABASE_ERROR" is returned if there is an issue connecting to lyrics_ds.db.

    Preconditions:
        - artist_name != ""
    """
    try:
        cohere_apikey, openai.api_key = get_api_keys()
        co = cohere.Client(cohere_apikey)
    except cohere.CohereError:
        return "API_ERROR"
    #  Retrieve API keys and connect to cohere API

    try:
        conn = connect_to_database()
        cur = conn.cursor()
        if not check_artist(artist_name, cur):
            return "ARTIST_ERROR"
    except sqlite3.Error:
        return "DATABASE_ERROR"
    #  Connect to the lyrics_ds.db database and check if the given artist is in the database

    songs = get_songs(artist_name, cur)
    discography = Discography(artist_name)

    try:
        for song in songs:
            title = song[0]
            lyrics = song[1]
            embedding = co.embed([lyrics]).embeddings[0]  # Call cohere API to get the embedding of the song lyric
            discography.add_song(title, lyrics, embedding)

        discography.match_all_similarities()

        conn.close()   # Close the connection to the database
        return discography

    except cohere.CohereError:
        conn.close()
        return "API_ERROR"


def generate_song_title(lyrics: str) -> str:
    """ Returns a song title given song lyrics.

    Uses openai.ChatCompletion.create() (using the GPT-3.5 model)

    Preconditions:
        - lyrics != ""
    """
    try:
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

    except openai.error.OpenAIError:
        return "API_ERROR"


def generate_song(discography: Discography) -> str:
    """Returns song lyrics "in the style" of the lyrics found in the given a Discography.

    More formally, the function takes (at most) the top five songs with the highest degrees
    and uses the lyrics of these songs as prompts to generate a new song lyric.

    Uses openai.ChatCompletion.create() (using the GPT-3.5 model)

    Preconditions:
        - len(discography.songs) > 0
    """
    song_prompts = discography.top_five_songs()

    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    system_description_content, prompt = generate_prompt(song_prompts)
    num_tokens = len(encoding.encode(system_description_content + prompt))
    # Calculates the number of openai tokens the prompt will cost
    # The maximum tokens for an API call is 4096 (this includes the prompt and the response message),
    # so to ensure that an error is not raised, we cap the tokens for the prompt to 3200, and 800 for the response

    while num_tokens > 3200:
        song_prompts.pop()
        system_description_content, prompt = generate_prompt(song_prompts)
        num_tokens = len(encoding.encode(system_description_content + prompt))
    # Keep removing a song from the prompts until the number of tokens for the prompt is at most 3200.

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            max_tokens=800,  # Limit the tokens to 800 for the reponse
            messages=[
                {"role": "system", "content": system_description_content},
                {"role": "user", "content": prompt},
            ]
        )

        lyrics = response.choices[0]['message']['content']
        return lyrics

    except openai.error.OpenAIError:
        return "API_ERROR"

# ----------------- MAIN TOP LEVEL FUNCTIONS -----------------


# ----------------- HELPER FUNCTIONS -----------------
def generate_prompt(song_prompts: list[Song]) -> tuple[str, str]:
    """Generates the message prompts to pass to openai.ChatCompletion.create().

    system_description_content is the prompt that specifies to GPT what its objective/role is.
    prompt is the actual prompt that instructs GPT to generate lyrics based on the given lyrics.

    Preconditions:
        - song_prompts != []
    """
    song_lyrics = ''

    for song in song_prompts:
        song_lyrics += f'----------{song.title}----------\n'
        song_lyrics += song.lyrics

    system_description_content = 'You generate lyrics of a song in the style of example songs that you are given.'
    prompt = f"Write a unique and original song lyrics in a similar style to that of the following songs: " \
             f"{song_lyrics}." \
             f" Ensure that the lyrics are completely original! Don't reuse phrasing from the given lyrics. " \
             f"Remove any additional text that is not a part of the lyrics!"

    return system_description_content, prompt


def get_api_keys() -> tuple[str, str]:
    """Retrieves and returns the cohere and openai API keys from keys.txt.

    Preconditions:
        - The first line of keys.txt is a valid API key for cohere
        - The second line of keys.txt is a valid API key for openai
    """
    with open('keys.txt', 'r') as file:
        cohere_apikey = file.readline().strip()
        openai_apikey = file.readline().strip()

    return cohere_apikey, openai_apikey


def connect_to_database() -> Connection:
    """Opens and returns the connection to the lyrics_ds.db database.

    Preconditions:
        - lyrics_ds.db contains a table called 'artists'
        - lyrics_ds.db contains a table called 'songs'
    """
    conn = connect('lyrics_ds.db')
    return conn


def check_artist(artist_name: str, cur: Cursor) -> bool:
    """Checks if the given artist name exists in the artists table of lyrics_ds.db.

    Returns True if the artist exists and False otherwise.

    Note that the query ignores capitlization of artist_name. So passing in artist_name
    as 'DRAKE' vs 'drake' would result in the same query.

    Preconditions:
        - cur is a cursor of a connection to lyrics_ds.db
        - lyrics_ds.db contains a table called 'artists'
        - The 'artists' table contains a 'name' column
        - artist_name != ""
    """
    cur.execute('SELECT name FROM artists WHERE name = ? COLLATE NOCASE', (artist_name.lower(),))
    return cur.fetchone() is not None


def get_songs(artist_name: str, cur: Cursor) -> list[tuple[str, str]]:
    """Queries and returns the songs made by the given artist from the songs table of lyrics_ds.db

    Returns a list of tuples where each tuple represents a song. Each tuple contains two strings,
    the first string is the title of the song, and the latter is the song's lyrics.

    Note that the query ignores capitlization of artist_name. So passing in artist_name
    as 'DRAKE' vs 'drake' would result in the same query.

    Preconditions:
        - cur is a cursor of a connection to lyrics_ds.db
        - lyrics_ds.db contains a table called 'songs'
        - The 'songs' table contains a 'title', 'lyrics' and 'views' column
        - artist_name != ""
        - There exists at least one song by artist_name in the 'songs' table
    """
    cur.execute('SELECT title, lyrics FROM songs WHERE artist = ? COLLATE NOCASE ORDER BY views DESC LIMIT 100',
                (artist_name.lower(),))
    # We cap the query results at at most 100 songs because the free version of
    # cohere (when we call co.embed()) only allows 100 API calls per minute

    return cur.fetchall()
# ----------------- HELPER FUNCTIONS -----------------


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['cohere', 'discography', 'sqlite3', 'openai', 'tiktoken'],
        'allowed-io': ['connect_to_database', 'get_api_keys'],
        'max-line-length': 120
    })

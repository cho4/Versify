## INTRODUCTION
Discovering music by category is now easier than ever through a Google search. However, the industry is made up of endless unique styles that serve as an artist’s signature and help them stand out. There are several reasons why one might want to imitate an artist’s songwriting style, such as finding inspiration, creating parodies or tributes, or expanding one’s own style. In exploring our curiosities towards possible technological advancements for the musical industry, we also recognized that with the explosion of ChatGPT and other generative AI models, the applications of prompt engineering have become more and more prominent. In light of these, our project aims to utilize graphs in conjunction with natural language processing to generate completely new song lyrics in the style of a given musical artist. This will be entirely based on their commonly used vocabulary and semantic patterns which are derived from their existing songs. To compute this, we use graphs to model an artist’s discography, where each vertex represents a song by that artist. In conjunction with the use of an NLP startup, Cohere, we are able to obtain embeddings of the lyrics of these songs, providing us with numerical representations of semantics for each lyric. We then form an edge between two Songs when their embeddings are more than 75% similar. Furthermore, using OpenAI’s GPT-3.5 model, we can take the top five songs with the highest degree in the discography graph to generate lyrics that are most representative of a given artist—applying its powerful prompt-based generation model. This process represents the makeup of our course project, Versify: The Future of Songwriting.

## DATASETS
In order to make Versify work, we needed a way to access data about artists, discographies, and lyric data for each song. Initially, we proposed to use musixmatch API to access this information, however through testing it in the early stages of the development of the project, it proved to be both slow and unreliable. We ultimately decided to switch gears and instead use a fixed dataset, enabling us to directly access the data.

In doing so, we turned to Kaggle, a Google owned service which allows users to find and publish datasets for training machine learning models and further applications in data science. We quickly found a suitable dataset called 5 Million Song Lyrics Dataset which was provided in the form of a csv file. 

However, we soon determined that we would not be able to work with this data set in its given format, as iterating through such a large file would not be computationally efficient. Thus, after implementing several efficiency related workarounds found in the csv and pandas libraries, we ultimately settled on using the Python sqlite3 library—whose results were researched to be 50 times more efficient than pandas.

For our purposes, we then converted the data in our csv file to a SQL table in a db file, done through a one time use of the pandas.read_csv function in the Python console. This function converts the data in the csv to a pandas.DataFrame object, which is then converted into an SQL table called ‘songs’ by using the pandas.DataFrame.to_sql method, storing the table in  lyrics_ds.db. To reduce the size of the already large database file and further improve efficiency, we dropped all the columns from the table that were outside the scope of the project—keeping only ‘title’, ‘artist’, ‘views’ and ‘lyrics’. Through our testing, we found that on average, a SELECT query to ‘songs’ takes 20-30 seconds, which is significantly better than the several minutes it would take to perform the same task using a csv file.

Moreover, we created an additional single-columned table in lyrics_ds.db called ‘artists’, which contains the names of all possible artists in our dataset. As the number of rows of the ‘artists’ table is significantly smaller than that of  ‘songs’ (approx. 700k vs 5 mil), this enabled us to more efficiently validate whether an inputted artist exists in our dataset and provide near-instant feedback to the user.

In addition, we generated a separate file called discographies.pkl which contains a dictionary of already instantiated Discography objects for several artists (done using the pickle library). This file updates every time the user enters a new artist, and when an artist name that is already in discographies.pkl is entered, the process of querying lyrics_db.db is skipped, shaving off the need for expensive computations. 

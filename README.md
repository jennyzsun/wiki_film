# Wikipedia Film
Author: Jenny Sun <br />
Coauthor: John Sun (author to get_soup_search and get_wiki_val functions) <br />
May 2015
___________________________________________________________________________________________________________________________
![bb7k-overview](https://raw.githubusercontent.com/jennyzsun/wiki_film/master/wikifilm.png)

##Purpose
The goal of wiki_film is to provide a module to users with functions that aid in the extraction of box office sales and budget data of a movie off of Wikipedia. <br />

###Functions Include:
* predict_movie_filter(movie, year) 
* get_soup_search(x, search) 
* get_wiki_val(title, search) 
* get_wiki_data(movie, year) 
* get_dollar_amount(x) 

###To Use:
Download `wiki_film.py`. To get data (as shown in the picture above), use `get_wiki_data("insert_movie_name", insert_movie_year)`. <br />
For example: `get_wiki_data("Pitch Perfect", 2012)`

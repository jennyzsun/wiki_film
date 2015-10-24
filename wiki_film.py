import pandas as pd
import wikipedia #Reference: https://pypi.python.org/pypi/wikipedia/
import bs4
from bs4 import BeautifulSoup
import urllib2
import numpy as np


def predict_movie_filter(movie, year):
    """Predict movie title and return that title."""
    my_searches = set(wikipedia.search('%s (%i film)' % (movie, year)) + 
                      wikipedia.search('%s (film)' % movie))
    
    #list Comprehesions: [expression for item in list if conditional]
    searches = [element for element in list(my_searches)
                if (movie.lower() in element.lower()) &
                ('List of accolades' not in element)]
    
    #if list of searches (searches) is empty, return None, otherwise
    #     convert everyhting to lower case
    if len(searches) == 0:
        return None
    else:
        searches = [search.lower() for search in searches]
        
    #return movie titles in preference of: 
    #     1. movie (year film)
    #     2. movie (film)
    #     3. movie
    #otherwise: return searches[0]
    #note: must movie.lower because wikipedia package returns lower
    lmovie = movie.lower()
    first = '%s (%i film)' % (lmovie, year)
    second = '%s (film)' % lmovie
    
    if  first in searches:
        return '%s (%i film)' % (movie, year)
    if second in searches:
        return '%s (film' % movie
    if lmovie in searches:
        return movie
    return searches[0]


def get_soup_search(x, search):
    """Searches to see if search is in the soup content and returns true if it is (false o/w)."""
    if len(x.contents) == 0:
        return False
    return x.contents[0] == search


def get_wiki_val(title, search):
    """Searches for header and returns the corresponding value."""
    url = wikipedia.page(title).url
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())
    results = filter(lambda x: get_soup_search(x,search), soup.findAll('th') )
    if len(results) < 1:
        return None
    # gonna get possibly several things.  Take everything that does not have links
    contents = results[0].fetchNextSiblings()[0].contents
    temp = u' '.join([out for out in contents if isinstance(out, bs4.element.Tag) == False])
    return temp.encode('utf-8')


def get_wiki_data(movie, year):
    """Extracts 'Box Office' and 'Budget' values and returns a series that includes movie, year,
     title, box office, and budget.


    movie -- movie name
    year -- year movie was released
    """
    title = predict_movie_filter(movie, year)
    #if movie in EXCEPTIONS:
    #    title = EXCEPTIONS[movie]

    box_office = get_wiki_val(title, 'Box office')
    budget = get_wiki_val(title, 'Budget')
    
    if box_office == None:
        box_office = ''
    if budget == None:
        budget = ''
    
    return pd.Series([movie, year, title, box_office, budget], 
                     index = ['movie', 'year', 'title', 'boxoffice', 'budget'])


def get_dollar_amount(x):
    """Changes string into the equivalent float in U.S. dollars and returns it."""
    x = x.strip(' ')
    x = x.replace(',', '')
    x = x.replace('+', '')
    x = x.replace('est.', '')
    
    #Case: Empty String
    if x == '':
        return float(0)
    
    #Corner Case: Contains the string 'or'
    if 'or' in x:
        try:
            s = x.split('or')
            return get_dollar_amount(s[0])
        except:
            return np.nan
        
    #Corner Case: For '\xe2\x80\x93'
    if '\xe2\x80\x93' in x:
        x = x.replace('\xe2\x80\x93', '-')
        return get_dollar_amount(x)
    
    #Corner Case: For '\xc2\xa0'
    if '\xc2\xa0' in x:
        x = x.replace('\xc2\xa0', '')
        return get_dollar_amount(x)
    
    #Corner Case: For ''\xc2\xa3' --> missing pound symbol // exchange rate: £1 = $1.5 (US)
    if '\xc2\xa3' in x:
        x = x.replace('\xc2\xa3', '')
        return 1.5 * get_dollar_amount(x) 
    
    #Corner Case: Contains '-' (ie: range) --> Returns larger number
    if '-' in x:
        try:
            s = x.split('-')
            return get_dollar_amount(s[1])
        except:
            return np.nan
        
    #Corner Case: Contains 'over'
    if 'ov' in x or 'more than' in x:
        try:
            s = x.split('$')
            return get_dollar_amount(s[1])
        except:
            return np.nan

    #Corner Case: Contains 'Anticipated rentals accruing'
    if 'Ant' in x:
        try:
            s = x.split('A')
            return get_dollar_amount(s[0])
        except:
            return np.nan
        
    #Corner Case: Contains a new line in the case where (US) and (UK) are given
    if '(US)' in x and '(UK)' in x:
        try:
            s = x.split('\n')
            return get_dollar_amount(s[0])
        except:
            return np.nan

    #Corner Case: In pounds and dollars
    if '$' in x and '£' in x:
        try:
            s = x.split('$')
            return get_dollar_amount(s[1])
        except:
            return np.nan
        
    #Corner Case: In SEK and dollars
    if 'SEK' in x and '$' in x:
        try:
            x = x.replace('\n', '')
            s = x.split('$')
            return get_dollar_amount(s[1])
        except:
            return np.nan
    
    #Corner Case: Contains '\n'
    if '\n' in x:
        s = x.split('\n')
        return get_dollar_amount(s[0])
        
    #Corner Case: In pounds only // exchange rate: £1 = $1.5 (US)
    if '£' in x:
        try:
            x = x.replace('£', '')
            x = float(x) * 1.5
            return x
        except:
            return np.nan
        
    #Corner Case: Contains two values
    if '($' in x:
        try:
            s = x.split('(')
            return get_dollar_amount(s[1])
        except:
            return np.nan
        
    #Corner case: Contains '(...)'
    if '(' in x:
        try:
            s = x.split('(')
            return get_dollar_amount(s[0])
        except:
            return np.nan
    
    #General Case: Amt is in $ (US)
    else:
        try:
            x = x.replace('$', '')
            x = x.replace('(', '')
            x = x.replace(')', '')
            x = x.replace('US', '')
            x = x.replace('U.S.', '')
            x = x.replace('United States', '')

            #Case 1a: Contains 'millions'
            if 'million' in x:
                x = x.replace('million', '')
                num = float(x) * 1000000
            #Case 1b: Contains 'billions'
            elif 'billion' in x:
                x = x.replace('billion', '')
                num = float(x) * 1000000000
            else:
                x = x.replace(',', '')
                num = x

            return float(num)
        except:
            return np.nan

# -*- coding: utf-8 -*-
import urllib, unicodedata, traceback
from api_daum_movie import MovieSearch



def searchMovie(results, media, lang):
    Log('SEARCH : %s %s' % (media.name, media.year))
    movie_name = unicodedata.normalize('NFKC', unicode(media.name)).strip()            
    is_include_kor, movie_list = MovieSearch.search_movie(movie_name, media.year)
    Log(movie_list)
    for data in movie_list:
        Log(data)
        results.Append(MetadataSearchResult(id=data['id'], name=data['title'], year=int(data['year']), score=data['score'], lang=lang))

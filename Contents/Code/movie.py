# -*- coding: utf-8 -*-
import urllib, unicodedata, traceback
from api_daum_movie import MovieSearch
import re
import time

def searchMovie(results, media, lang):
    Log('SEARCH : [%s] [%s]' % (media.name, media.year))
    movie_year = media.year
    movie_name = unicodedata.normalize('NFKC', unicode(media.name)).strip()            
    match = Regex(r'^(?P<name>.*?)[\s\.\[\_\(](?P<year>\d{4})').match(movie_name)
    
    if match:
        movie_name = match.group('name').replace('.', ' ').strip()
        movie_name = re.sub(r'\[(.*?)\]', '', movie_name )
        movie_year = match.group('year')
    is_include_kor, movie_list = MovieSearch.search_movie(movie_name, movie_year)
    #Log(movie_list)
    for data in movie_list:
        #Log(data)
        try:
            meta_id = data['id']
            if Prefs['include_time_info']:
                meta_id += '_%s' % int(time.time())
            results.Append(MetadataSearchResult(id=meta_id, name=data['title'], year=int(data['year']), score=data['score'], lang=lang))
        except Exception as e: 
            Log('Exception:%s', e)
            Log(traceback.format_exc())  


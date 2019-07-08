# -*- coding: UTF-8 -*-
# SJVA, Plex SJ Daum Agent, shell 공용
import os
import sys
import re
import traceback
import logging
import urllib

logger = None
is_sjva = True
is_shell = True
is_plex = True

try:
    import requests
    import lxml.html
    is_plex = False
except:
    is_sjva = False
    is_shell = False

try:
    # SJVA
    from framework.util import Util
    package_name = __name__.split('.')[0]
    logger = logging.getLogger(package_name)
    is_shell = False
except:
    is_sjva = False


####################################################
if is_shell:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())


def log_debug(msg, *args, **kwargs):
    if logger is not None:
        logger.debug(msg, *args, **kwargs)
    else:
        Log(msg, *args, **kwargs)

def log_error(msg, *args, **kwargs):
    if logger is not None:
        logger.error(msg, *args, **kwargs)
    else:
        Log(msg, *args, **kwargs)

def get_json(url):
    try:
        if is_plex:
            return JSON.ObjectFromURL(url)
        else:
            return requests.get(url).json()
    except Exception as e: 
        log_error('Exception:%s', e)
        log_error(traceback.format_exc())            

def get_html(url):
    try:
        if is_plex:
            return HTML.ElementFromURL(url)
        else:
            return lxml.html.document_fromstring(requests.get(url).content)
    except Exception as e: 
        log_error('Exception:%s', e)
        log_error(traceback.format_exc())




####################################################

class MovieSearch(object):
    @staticmethod
    def search_movie(movie_name, movie_year):
        try:
            movie_year = '%s' % movie_year
            movie_list = []

            #8년 전쟁 이란 vs 이라크
            split_index = -1
            is_include_kor = False
            for index, c in enumerate(movie_name):
                if ord(u'가') <= ord(c) <= ord(u'힣'):
                    is_include_kor = True
                    split_index = -1
                elif ord('a') <= ord(c.lower()) <= ord('z'):
                    is_include_eng = True
                    if split_index == -1:
                        split_index = index
                elif ord('0') <= ord(c.lower()) <= ord('9') or ord(' '):
                    pass
                else:
                    split_index = -1

            if is_include_kor and split_index != -1:
                kor = movie_name[:split_index].strip()
                eng = movie_name[split_index:].strip()
            else:
                kor = None
                eng = None
            log_debug('SEARCH_MOVIE : [%s] [%s] [%s] [%s]' % (movie_name, is_include_kor, kor, eng))
            
            movie_list = MovieSearch.search_movie_web(movie_list, movie_name, movie_year)
            if movie_list and movie_list[0]['score'] == 100:
                log_debug('SEARCH_MOVIE STEP 1 : %s' % movie_list)
                return is_include_kor, movie_list

            if kor is not None:
                movie_list = MovieSearch.search_movie_web(movie_list, kor, movie_year)
                if movie_list and movie_list[0]['score'] == 100:
                    log_debug('SEARCH_MOVIE STEP 2 : %s' % movie_list)
                    return is_include_kor, movie_list

            if eng is not None:
                movie_list = MovieSearch.search_movie_web(movie_list, eng, movie_year)
                if movie_list and movie_list[0]['score'] == 100:
                    log_debug('SEARCH_MOVIE STEP 3 : %s' % movie_list)
                    return is_include_kor, movie_list

            #검찰측의 죄인 検察側の罪人. Kensatsu gawa no zainin. 2018.1080p.KOR.FHDRip.H264.AAC-RTM
            # 영어로 끝나지전은 한글
            # 그 한글중 한글로 시작하지 않는곳까지
            if kor is not None:
                tmps = kor.split(' ')
                index = -1
                for i in range(len(tmps)):
                    if ord(u'가') <= ord(tmps[i][0]) <= ord(u'힣') or ord('0') <= ord(tmps[i][0]) <= ord('9'):
                        pass
                    else:
                        index = i
                        break
                if index != -1:
                    movie_list = MovieSearch.search_movie_web(movie_list, ' '.join(tmps[:index]), movie_year)
                    if movie_list and movie_list[0]['score'] == 100:
                        log_debug('SEARCH_MOVIE STEP 4 : %s' % movie_list)
                        return is_include_kor, movie_list

            if is_plex == False:
                # 95점이면 맞다고 하자. 한글로 보내야하기때문에 검색된 이름을..
                if movie_list and movie_list[0]['score'] == 95:
                    movie_list = MovieSearch.search_movie_web(movie_list, movie_list[0]['title'], movie_year)
                    if movie_list and movie_list[0]['score'] == 100:
                        log_debug('SEARCH_MOVIE STEP 5 : %s' % movie_list)
                        return is_include_kor, movie_list

            # IMDB
            if is_include_kor == False:
                movie = MovieSearch.search_imdb(movie_name.lower(), movie_year)
                if movie is not None:
                    movie_list = MovieSearch.search_movie_web(movie_list, movie['title'], movie_year)
                    if movie_list and movie_list[0]['score'] == 100:
                        log_debug('SEARCH_MOVIE STEP IMDB : %s' % movie_list)
                        return is_include_kor, movie_list

            log_debug('SEARCH_MOVIE STEP LAST : %s' % movie_list)
        except Exception as e: 
            log_error('Exception:%s', e)
            log_error(traceback.format_exc())            
        return is_include_kor, movie_list

    @staticmethod
    def movie_append(movie_list, data):
        try:
            flag_exist = False
            for tmp in movie_list:
                if tmp['id'] == data['id']:
                    flag_exist = True
                    tmp['score'] = data['score']
                    tmp['title'] = data['title']
                    if 'country' in data:
                        tmp['country'] = data['country']
                    break
            if not flag_exist:
                movie_list.append(data)
        except Exception as e: 
            log_error('Exception:%s', e)
            log_error(traceback.format_exc())    

    @staticmethod
    def search_movie_web(movie_list, movie_name, movie_year):
        try:
            #movie_list = []
            url = 'https://suggest-bar.daum.net/suggest?id=movie&cate=movie&multiple=1&mod=json&code=utf_in_out&q=%s' % (urllib.quote(movie_name.encode('utf8')))
            data = get_json(url)
            
            for index, item in enumerate(data['items']['movie']):
                tmps = item.split('|')
                score = 85 - (index*5)
                if tmps[0].find(movie_name) != -1 and tmps[3] == movie_year:
                    score = 95
                elif tmps[3] == movie_year:
                    score = score + 5
                if score < 10:
                    score = 10
                MovieSearch.movie_append(movie_list, {'id':tmps[1], 'title':tmps[0], 'year':tmps[3], 'score':score})
        except Exception as e: 
            log_error('Exception:%s', e)
            log_error(traceback.format_exc())
        
        try:
            url = 'https://search.daum.net/search?nil_suggest=btn&w=tot&DA=SBC&q=%s%s' % ('%EC%98%81%ED%99%94+', urllib.quote(movie_name.encode('utf8')))
            html = get_html(url)
            movie = None
            try:
                movie = html.get_element_by_id('movieEColl')
            except Exception as e: 
                #log_error('Exception:%s', e)
                #log_error('SEARCH_MOVIE NOT MOVIEECOLL')
                pass
            if movie is not None:
                title = movie.get_element_by_id('movieTitle')
                a_tag = title.find('a')
                href = a_tag.attrib['href']
                title = a_tag.find('b').text_content()
                country_tag = movie.xpath('//div[3]/div/div[1]/div[2]/dl[1]/dd[2]')
                country = ''
                if country_tag:
                    country = country_tag[0].text_content().split('|')[0].strip()
                MovieSearch.movie_append(movie_list, {'id':href.split('=')[1], 'title':title, 'year':movie_year, 'score':100, 'country':country})
                #results.Append(MetadataSearchResult(id=href.split('=')[1], name=title, year=movie_year, score=100, lang=lang))
                tmp = movie.find('div[@class="coll_etc"]')
                if tmp is not None:
                    tag_list = tmp.findall('.//a')
                    for tag in tag_list:
                        match = re.compile(r'(.*?)\((.*?)\)').search(tag.text_content())
                        if match:
                            daum_id = tag.attrib['href'].split('||')[1]
                            score = 80
                            if match.group(2) == movie_year:
                                score = 90
                            MovieSearch.movie_append(movie_list, {'id':daum_id, 'title':match.group(1), 'year':match.group(2), 'score':score})
                            #results.Append(MetadataSearchResult(id=daum_id, name=match.group(1), year=match.group(2), score=score, lang=lang))
        except Exception as e: 
            log_error('Exception:%s', e)
            log_error(traceback.format_exc())
        movie_list = list(reversed(sorted(movie_list, key=lambda k:k['score'])))
        return movie_list

    @staticmethod
    def search_imdb(title, year):
        try:
            year = int(year)
            title = title.replace(' ', '_')
            url = 'https://v2.sg.media-imdb.com/suggestion/%s/%s.json' % (title[0], title)
            tmp = get_json(url)
            if 'd' in tmp and tmp['d'][0]['y'] == year:
                return {'id':tmp['d'][0]['id'], 'title':tmp['d'][0]['l'], 'year':year, 'score':100}
        except Exception as e: 
            log_error('Exception:%s', e)
            log_error(traceback.format_exc())
# -*- coding: utf-8 -*-
# Daum Movie
 
import urllib, unicodedata, traceback, re
# 추가
import watcha
import tmdb

DAUM_MOVIE_SRCH   = "http://movie.daum.net/data/movie/search/v2/%s.json?size=20&start=1&searchText=%s"

DAUM_MOVIE_DETAIL = "http://movie.daum.net/data/movie/movie_info/detail.json?movieId=%s"
DAUM_MOVIE_CAST   = "http://movie.daum.net/data/movie/movie_info/cast_crew.json?pageNo=1&pageSize=100&movieId=%s"
DAUM_MOVIE_PHOTO  = "http://movie.daum.net/data/movie/photo/movie/list.json?pageNo=1&pageSize=100&id=%s"

from tv import searchTV, updateTV
from movie import searchMovie

@route('/version') 
def version():
    return '2020-07-27'

def Start():
    #HTTP.CacheTime = CACHE_1HOUR * 12
    HTTP.Headers['Accept'] = 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    HTTP.Headers['Accept-Language'] = 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    HTTP.Headers['Cookie'] = Prefs['cookie']
  
####################################################################################################
"""
def searchDaumMovie(cate, results, media, lang):
  media_name = media.name
  media_name = unicodedata.normalize('NFKC', unicode(media_name)).strip()
  Log.Debug("search: %s %s" %(media_name, media.year))
  data = JSON.ObjectFromURL(url=DAUM_MOVIE_SRCH % (cate, urllib.quote(media_name.encode('utf8'))))
  items = data['data']
  for item in items:
    year = str(item['prodYear'])
    title = String.DecodeHTMLEntities(String.StripTags(item['titleKo'])).strip()
    id = str(item['tvProgramId'] if cate == 'tv' else item['movieId'])
    if year == media.year:
      score = 95
    elif len(items) == 1:
      score = 80
    else:
      score = 10
    Log.Debug('ID=%s, media_name=%s, title=%s, year=%s, score=%d' %(id, media_name, title, year, score))
    results.Append(MetadataSearchResult(id=id, name=title, year=year, score=score, lang=lang))
"""

def update_movie_by_web(metadata, metadata_id):
  try:
      url = 'https://movie.daum.net/moviedb/main?movieId=%s' % metadata_id
      root = HTML.ElementFromURL(url)
      tags = root.xpath('//span[@class="txt_name"]')
      tmp = tags[0].text_content().split('(')
      metadata.title = urllib.unquote(tmp[0])
      metadata.title_sort = unicodedata.normalize('NFKD', metadata.title)
      try: metadata.original_title = root.xpath('//span[@class="txt_origin"]')[0].text_content()
      except: pass

      metadata.year = int(tmp[1][:4])
      try:
        tags = root.xpath('//div[@class="info_origin"]/a/span')
        if len(tags) == 4:
          tmp = '%s.%s' % (tags[1].text_content(), tags[3].text_content())
          metadata.rating = float(tmp)
      except: pass
      try:
        metadata.genres.clear()
        metadata.countries.clear()
        tags = root.xpath('//dl[@class="list_movie list_main"]/dd')
        for item in tags[0].text_content().split('/'):
          metadata.genres.add(item.strip())
        for item in tags[1].text_content().split(','):
          metadata.countries.add(item.strip())
        tmp = tags[2].text_content().strip()
        match = re.compile(r'\d{4}\.\d{2}\.\d{2}').match(tmp)
        if match: 
          metadata.originally_available_at = Datetime.ParseDate(match.group(0).replace('.', '')).date()
          tmp = tags[3].text_content().strip()
          if tmp.find(u'재개봉') != -1:
            tmp = tags[4].text_content().strip()
        else:
          metadata.originally_available_at = None
        match = re.compile(ur'(?P<duration>\d{2,})분[\s,]?(?P<rate>.*?)$').match(tmp)
        if match:
          metadata.duration = int(match.group('duration').strip())*60
          metadata.content_rating = String.DecodeHTMLEntities(String.StripTags(match.group('rate').strip()).strip())
      except Exception as e:
        Log('Exception:%s', e)
        Log(traceback.format_exc())

      #try: metadata.summary = String.DecodeHTMLEntities(String.StripTags(root.xpath('//div[@class="desc_movie"]/p')[0].text_content().strip()).strip())
      try: metadata.summary = String.DecodeHTMLEntities(String.StripTags(root.xpath('//div[@class="desc_movie"]/p')[0].text_content().strip().replace('<br>', '\n\n')).strip())
      except: pass
  except Exception as e:
    Log('Exception:%s', e)
    Log(traceback.format_exc())




def updateDaumMovie(cate, metadata):
  # (1) from detail page
    poster_url = None
    metadata_id = metadata.id.split('_')[0]
    update_movie_by_web(metadata, metadata_id)
    """
    try:
      data = JSON.ObjectFromURL(url=DAUM_MOVIE_DETAIL % metadata_id)
      info = data['data']
      metadata.title = info['titleKo']
      metadata.title_sort = unicodedata.normalize('NFKD', metadata.title)
      metadata.original_title = info['titleEn']
      metadata.genres.clear()
      metadata.year = int(info['prodYear'])
      try: metadata.content_rating = String.DecodeHTMLEntities(String.StripTags(info['admissionDesc']).strip())
      except: pass
      try: metadata.rating = float(info['moviePoint']['inspectPointAvg'])
      except: pass
      for item in info['genres']:
        metadata.genres.add(item['genreName'])
      try: metadata.duration = int(info['showtime'])*60
      except: pass
      try: metadata.originally_available_at = Datetime.ParseDate(info['releaseDate']).date()
      except: pass
      try: metadata.summary = String.DecodeHTMLEntities(String.StripTags(info['plot']).strip())
      except: pass
      metadata.countries.clear()
      for item in info['countries']:
        metadata.countries.add(item['countryKo'])
    except:
      update_movie_by_web(metadata, metadata_id)
    """

    try: poster_url = info['photo']['fullname']
    except:pass

  # (2) cast crew
    directors = list()
    producers = list()
    writers = list()
    roles = list()

    data = JSON.ObjectFromURL(url=DAUM_MOVIE_CAST % metadata_id)
    for item in data['data']:
      cast = item['castcrew']
      if cast['castcrewCastName'] in [u'감독', u'연출']:
        director = dict()
        director['name'] = item['nameKo'] if item['nameKo'] else item['nameEn']
        if item['photo']['fullname']:
          director['photo'] = item['photo']['fullname']
        directors.append(director)
      elif cast['castcrewCastName'] == u'제작':
        producer = dict()
        producer['name'] = item['nameKo'] if item['nameKo'] else item['nameEn']
        if item['photo']['fullname']:
          producer['photo'] = item['photo']['fullname']
        producers.append(producer)
      elif cast['castcrewCastName'] in [u'극본', u'각본']:
        writer = dict()
        writer['name'] = item['nameKo'] if item['nameKo'] else item['nameEn']
        if item['photo']['fullname']:
          writer['photo'] = item['photo']['fullname']
        writers.append(writer)
      elif cast['castcrewCastName'] in [u'주연', u'조연', u'출연', u'진행']:
        role = dict()
        role['role'] = cast['castcrewTitleKo']
        role['name'] = item['nameKo'] if item['nameKo'] else item['nameEn']
        if item['photo']['fullname']:
          role['photo'] = item['photo']['fullname']
        roles.append(role)
      # else:
      #   Log.Debug("unknown role: castcrewCastName=%s" % cast['castcrewCastName'])

    if directors:
      metadata.directors.clear()
      for director in directors:
        meta_director = metadata.directors.new()
        if 'name' in director:
          meta_director.name = director['name']
        if 'photo' in director:
          meta_director.photo = director['photo']
    if producers:
      metadata.producers.clear()
      for producer in producers:
        meta_producer = metadata.producers.new()
        if 'name' in producer:
          meta_producer.name = producer['name']
        if 'photo' in producer:
          meta_producer.photo = producer['photo']
    if writers:
      metadata.writers.clear()
      for writer in writers:
        meta_writer = metadata.writers.new()
        if 'name' in writer:
          meta_writer.name = writer['name']
        if 'photo' in writer: 
          meta_writer.photo = writer['photo']
    if roles:
      metadata.roles.clear()
      for role in roles:
        meta_role = metadata.roles.new()
        if 'role' in role:
          meta_role.role = role['role']
        if 'name' in role:
          meta_role.name = role['name']
        if 'photo' in role:
          meta_role.photo = role['photo']

  # (3) from photo page 
    url_tmpl = DAUM_MOVIE_PHOTO
    data = JSON.ObjectFromURL(url=url_tmpl % metadata_id)
    max_poster = int(Prefs['max_num_posters'])
    max_art = int(Prefs['max_num_arts'])
    idx_poster = 0
    idx_art = 0
    for item in data['data']:
        if item['photoCategory'] == '1' and idx_poster < max_poster:
            art_url = item['fullname']
            if not art_url: continue
            #art_url = RE_PHOTO_SIZE.sub("/image/", art_url)
            idx_poster += 1
            try: metadata.posters[art_url] = Proxy.Preview(HTTP.Request(item['thumbnail']), sort_order = idx_poster)
            except: pass
        elif item['photoCategory'] in ['2', '50'] and idx_art < max_art:
            art_url = item['fullname']
            if not art_url: continue
            #art_url = RE_PHOTO_SIZE.sub("/image/", art_url)
            idx_art += 1
            try: metadata.art[art_url] = Proxy.Preview(HTTP.Request(item['thumbnail']), sort_order = idx_art)
            except: pass
    Log.Debug('Total %d posters, %d artworks' %(idx_poster, idx_art))
    if idx_poster == 0:
        if poster_url:
            poster = HTTP.Request( poster_url )
            try: metadata.posters[poster_url] = Proxy.Media(poster)
            except: pass

    ################ LifeForWhat 추가부분
    watcha_headers = {
        'accept': 'application/vnd.frograms+json;version=20',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://watcha.com',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'x-watcha-client': 'watcha-WebApp',
        'x-watcha-client-language': 'ko',
        'x-watcha-client-region': 'KR',
        'x-watcha-client-version': '1.0.0'
    }
    """movie_name = unicodedata.normalize('NFKC', unicode("기생충")).strip()
    page = HTTP.Request('https://api.watcha.com/api/searches?query=%s' % (movie_name),
                        headers = watcha_headers)
    Log.Info(str(page))"""

    # 리뷰 클리어


    metadata.reviews.clear()

    # 컬렉션 클리어
    metadata.collections.clear()

    # tmdb collection 을 먼저 찾는다.
    tmdb_title_for_search = metadata.original_title
    tmdb_year = metadata.year
    try:
        j , c = tmdb.tmdb().search(name=tmdb_title_for_search , year=tmdb_year)
        try:
            tmdb_collection = c['name']
            if tmdb_collection != "":
                metadata.collections.add('💿 ' +tmdb_collection)
        except Exception as e:
            Log.Info(str(e))
            pass
    except Exception as e:
        Log.Info(str(e))
        pass

    # Watcha
    try:

        Log.Info('WATCHA SEARCHING TITLE : ' + metadata.title)
        Log.Info('WATCHA SEARCHING YEAR : ' + str(metadata.year))
        w = watcha.watcha(keyword = metadata.title, year=int(metadata.year), media_type='movies')
        w2 = w.info
        Log.Info('WATCHA SEARCHED TITLE : ' + str(w2['API_INFO']['title']))
        Log.Info('WATCHA SEARCHED YEAR : ' + str(w2['API_INFO']['year']))
        for item in w2['코멘트']:
            # ⭐
            wname = ''
            wsource = u'왓챠'
            wtext = ''
            wline = ''
            wimage = ''
            offiYN = item['user']['official_user']
            if offiYN == True:
                wname = item['user']['name']
                wtext = item['text']
                wimage = item['user_content_action']['rating']
                if wname != "" and wtext != "" and wimage != "":
                    meta_review = metadata.reviews.new()
                    meta_review.author = wname
                    meta_review.source = u'왓챠'
                    meta_review.text = '⭐ '+ str(wimage) + ' | '+ wtext
                    meta_review.link = 'https://www.watcha.com/'
                    if float(wimage) >= 6:
                        meta_review.image = 'rottentomatoes://image.review.fresh'
                    else:
                        meta_review.image = 'rottentomatoes://image.review.rotten'
        # 이제 Collection 파트

        whitelist = ['수상', '아카데미', '영화제']
        blacklist_keyword = ['여성', '여자', '페미', '소장', '메모', '소장', '베스트', '내가', '나의', '최고', '본 영화', '보물', '볼 영화',
                             '관람', '감상', '본것', '내 영화']
        blacklist_user = ['유정']
        try:
            d = {'watcha' : w2}
            # 복붙하느라...
            temp_list = d['watcha']['컬렉션']
        except:
            temp_list = []
        collections = []
        # 콜렉션용 각종 조건들을 붙인다...
        # 페미니스트가 너무 많음.. 왓챠에는..
        for coll in temp_list:
            for white in whitelist:
                if white in coll['title'] or coll['likes_count'] > 8000:
                    collections.append(coll['title'])
                    break

        for coll in temp_list:
            if coll['likes_count'] < 100:
                continue  # 좋아요가 100개 미만은 버린다.
            keep_going = False
            years_list = re.findall('\d{4}', coll['title'])
            years_list = [item for item in years_list if int(item) > 1890 and int(item) < 2030]
            if len(years_list) > 0:
                continue  # 년도가 들어간 건 버린다
            if keep_going == False:
                for black in blacklist_keyword:
                    if black in coll['title'].replace('  ', ' '):
                        keep_going = True
                        break

            if keep_going == False:
                for blackuser in blacklist_user:
                    if blackuser in coll['user']['name']:
                        keep_going = True
                        break

            if keep_going == False and coll['title'] not in collections:
                collections.append(coll['title'])
        #Log.Error(str(collections))
        for collection in collections:
            temp_string = collection
            if temp_string.count('수상') > 0:
                temp_string = "🏆 " + temp_string
            elif temp_string.count('후보') > 0:
                temp_string = "🏆 " + temp_string
            elif temp_string.count('대상') > 0:
                temp_string = "🏆 " + temp_string
            elif temp_string.count('주연상') > 0:
                try:
                    temp_string = "🏆 " + temp_string
                except:
                    #Log.Info(str(temp_string))
                    pass
            else:
                temp_string = "🎬 " + temp_string
            metadata.collections.add(temp_string)
    except Exception as e:
        import traceback
        Log.Info(str(e))
        Log.Info(traceback.print_exc)

####################################################################################################
class SJ_DaumMovieAgent(Agent.Movies):
    name = "SJ Daum"
    languages = [Locale.Language.Korean]
    primary_provider = True
    accepts_from = ['com.plexapp.agents.localmedia', 'com.plexapp.agents.xbmcnfo', 'com.plexapp.agents.opensubtitles', 'com.plexapp.agents.themoviedb']
    contributes_to = ['com.plexapp.agents.xbmcnfo']
    fallback_agent = 'com.plexapp.agents.imdb'
    def search(self, results, media, lang, manual=False):
        return searchMovie(results, media, lang)

    def update(self, metadata, media, lang):
        Log.Info("in update ID = %s" % metadata.id)
        updateDaumMovie('movie', metadata)


class SJ_DaumTvAgent(Agent.TV_Shows):
    name = "SJ Daum"
    primary_provider = True
    languages = [Locale.Language.Korean]
    accepts_from = ['com.plexapp.agents.localmedia', 'com.plexapp.agents.xbmcnfotv']
    contributes_to = [
        'com.plexapp.agents.xbmcnfotv',
    ]

    def search(self, results, media, lang, manual=False):
        return searchTV(results, media, lang)

    def update(self, metadata, media, lang):
        Log.Info("in update ID = %s" % metadata.id)
        updateTV(metadata, media)
        import local_tv_extras
        local_tv_extras.update(metadata, media)


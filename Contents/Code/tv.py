# -*- coding: utf-8 -*-
import urllib, unicodedata

def searchTV(results, media, lang):
    media_name = media.show
    Log('SEARCH : %s' % media_name)
    url = 'https://search.daum.net/search?w=tv&q=%s' % (urllib.quote(media_name.encode('utf8')))
    data = str(HTTP.Request(url))
    match = Regex(r'<title\>(?P<title>.*)\s\&').search(data)
    title = match.group('title') if match else ''
    match = Regex(r'irk\=(?P<id>\d+)').search(data)
    id = match.group('id') if match else '' 
    if id: results.Append(MetadataSearchResult(id=id, name=title, year='', score=100, lang=lang))

def updateTV(metadata, media):
    url = 'https://search.daum.net/search?w=tv&q=%s&irk=%s&irt=tv-program&DA=TVP' % (urllib.quote(media.title.encode('utf8')), metadata.id)
    Log('LOG : %s ' % url)
    root = HTML.ElementFromURL(url)
    items = root.xpath('//*[@id="tv_program"]/div[1]/div[2]/strong')
    if len(items) == 1:
        title = unicodedata.normalize('NFKC', unicode(items[0].text)).strip()
        Log('TITLE : %s' % title)
        metadata.title = title

    items = root.xpath('//*[@id="tv_program"]/div[1]/div[3]/span')
    studio = unicodedata.normalize('NFKC', unicode(items[0].text)).strip()
    Log('studio : %s' % studio)
    metadata.studio = studio

    summary = ''
    for item in items:
        summary += unicodedata.normalize('NFKC', unicode(item.text)).strip()#.encode('euc-kr')
        summary += ' '
    match = Regex(r'(\d{4}\.\d{1,2}\.\d{1,2})~').search(summary)
    if match:
        metadata.originally_available_at = Datetime.ParseDate(match.group(1)).date()

    metadata.genres.clear()
    items = root.xpath('//*[@id="tv_program"]/div[1]/dl[1]/dd')
    if len(items) == 1:
        genre = unicodedata.normalize('NFKC', unicode(items[0].text)).strip().split(' ')[0]
        Log('genre : %s' % genre)
        metadata.genres.add(genre)

    items = root.xpath('//*[@id="tv_program"]/div[1]/dl[2]/dd')
    if len(items) == 1:
        #summary += unicodedata.normalize('NFKC', unicode(items[0].text)).strip()
        summary += '\r\n' + items[0].text
        Log('summary : %s' % summary)
        metadata.summary = summary.replace('&nbsp', ' ')
    
    items = root.xpath('//*[@id="tv_program"]/div[1]/div[1]/a/img')
    if len(items) == 1:
        image = 'https:%s' % items[0].attrib['src']
        Log('image : %s' % image)
        poster = HTTP.Request( image )
        try: metadata.posters[image] = Proxy.Preview(poster)
        except: pass

    directors = []
    producers = []
    writers = []
    roles = []
    for i in range(1,3):
        items = root.xpath('//*[@id="tv_casting"]/div[%s]/ul//li' % i)
        for item in items:
            entity = {}
            entity['type'] = ''
            entity['role'] = ''
            entity['name'] = ''
            entity['photo'] = ''
            entity['tmp'] = ''
            cast_img = item.xpath('div/a/img')
            if len(cast_img) == 1:
                image = 'https:%s' % cast_img[0].attrib['src']
                entity['photo'] = image
            
            span_tag = item.xpath('span')
            for span in span_tag:
                span_text = unicodedata.normalize('NFKC', unicode(span.text)).strip()
                tmp = span.xpath('a')
                if len(tmp) == 1:
                    role_name = unicodedata.normalize('NFKC', unicode(tmp[0].text)).strip()
                    tail = unicodedata.normalize('NFKC', unicode(tmp[0].tail)).strip()
                    if tail == u'역':
                        entity['type'] = 'actor'
                        entity['role'] = role_name
                    else:
                        entity['name'] = role_name
                else:
                    if span_text.endswith(u'역'): entity['role'] = span_text.replace(u'역', '')
                    elif entity['name'] == '': entity['name'] = span_text
                    else: entity['role'] = span_text
            if entity['type'] == 'actor' or entity['role'].find(u'출연') != -1:
                roles.append(entity)
            elif entity['role'].find(u'감독') != -1 or entity['role'].find(u'연출') != -1:
                directors.append(entity)
            elif entity['role'].find(u'제작') != -1 or entity['role'].find(u'기획') != -1 or entity['role'].find(u'책임프로듀서') != -1:
                producers.append(entity)
            elif entity['role'].find(u'극본') != -1 or entity['role'].find(u'각본') != -1:
                writers.append(entity)
            else:
                roles.append(entity)
    metadata.roles.clear()
    for list in [roles, directors, producers, writers]:
        for e in list:
            meta = metadata.roles.new()
            meta.role = e['role'] if 'role' in e else ''
            meta.name = e['name'] if 'name' in e else ''
            meta.photo = e['photo'] if 'photo' in e else ''

    episode_url_list = []
    items = root.xpath('//*[@id="clipDateList"]/li')
    if len(items) > 300: items = items[len(items)-300:]
    for item in items:
        a_tag = item.xpath('a') 
        if len(a_tag) == 1:
            query = 'https://search.daum.net/search%s' % a_tag[0].attrib['href']
            episode_url_list.append(query)
    metadata.summary = '%s\r\n\r\nDaum:%s' % (metadata.summary, len(episode_url_list))

    count = len(episode_url_list)
    for i in range(count-1, -1, -1):
        root = HTML.ElementFromURL(episode_url_list[i])
        items = root.xpath('//div[@class="tit_episode"]')
        if len(items) == 1:
            tmp = items[0].xpath('strong') 
            if len(tmp) == 1:
                episode_frequency = unicodedata.normalize('NFKC', unicode(tmp[0].text)).strip()
                episode_summary = episode_frequency
                match = Regex(r'(\d+)').search(episode_frequency)
                if match:
                    Log('episode_frequency : %s' % match.group(1))
                    episode = metadata.seasons['1'].episodes[int(match.group(1))]
                else: 
                    Log('episode_frequency not matched!!!')
                    continue
            if episode is None: 
                Log('episode is None')
                continue
            tmp = items[0].xpath('span[@class="txt_date "]')
            if len(tmp) == 1:
                date1 = unicodedata.normalize('NFKC', unicode(tmp[0].text)).strip()
                episode.originally_available_at = Datetime.ParseDate(date1.split('(')[0]).date()
                episode.title = date1
            tmp = items[0].xpath('span[@class="txt_date"]')
            if len(tmp) == 1:
                date2 = unicodedata.normalize('NFKC', unicode(tmp[0].text)).strip()
                episode.title = '%s %s' % (date1, date2)
            
        items = root.xpath('//p[@class="episode_desc"]')
        if len(items) == 1:
            tmp = items[0].xpath('strong')
            if len(tmp) == 1:
                title = unicodedata.normalize('NFKC', unicode(tmp[0].text)).strip()
                Log('TITLE : %s' % title)
                summary = ''
                if title !='None': 
                    episode.title = '%s %s' % (episode.title, title)
        summary2 = '\r\n'.join(txt.strip() for txt in root.xpath('//p[@class="episode_desc"]/text()'))
        episode.summary = '%s\r\n%s' % (episode.title, summary2)

        items = root.xpath('//*[@id="tv_episode"]/div[2]/div[1]/div/a/img')
        if len(items) == 1:
            thumb_url = 'https:%s' % items[0].attrib['src']
            Log('episode thumb : %s' % thumb_url)
            thumb = HTTP.Request( thumb_url )
            try: episode.thumbs[thumb_url] = Proxy.Preview(thumb)
            except: pass

        episode.directors.clear()
        episode.producers.clear()
        episode.writers.clear()
        for e in directors:
            meta = episode.directors.new()
            meta.role = e['role'] if 'role' in e else ''
            meta.name = e['name'] if 'name' in e else ''
            meta.photo = e['photo'] if 'photo' in e else ''
        for e in producers:
            meta = episode.producers.new()
            meta.role = e['role'] if 'role' in e else ''
            meta.name = e['name'] if 'name' in e else ''
            meta.photo = e['photo'] if 'photo' in e else ''
        for e in writers:
            meta = episode.writers.new()
            meta.role = e['role'] if 'role' in e else ''
            meta.name = e['name'] if 'name' in e else ''
            meta.photo = e['photo'] if 'photo' in e else ''
    return


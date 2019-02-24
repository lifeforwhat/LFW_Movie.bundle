# -*- coding: utf-8 -*-
import os, urllib, unicodedata

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
    #flag_ending = False
    url = 'https://search.daum.net/search?w=tv&q=%s&irk=%s&irt=tv-program&DA=TVP' % (urllib.quote(media.title.encode('utf8')), metadata.id)
    Log('LOG : %s ' % url)
    root = HTML.ElementFromURL(url)
    items = root.xpath('//*[@id="tv_program"]/div[1]/div[2]/strong')
    if len(items) == 1:
        title = unicodedata.normalize('NFKC', unicode(items[0].text)).strip()
        Log('TITLE2 : %s' % title)
        metadata.title = title

    items = root.xpath('//*[@id="tv_program"]/div[1]/div[3]/span')
    if items:
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
    else:
        #flag_ending = True
        url2 = url.replace('w=tv&', '') 
        root2 = HTML.ElementFromURL(url2)
        items2 = root2.xpath('//*[@id="tvpColl"]/div[2]/div/div[1]/div')
        tmp = items2[0].text_content().strip()
        summary = tmp + u' 방송종료'
        metadata.studio = tmp.split(' ')[0]
        match = Regex(r'(\d{4}\.\d{1,2}\.\d{1,2})~').search(tmp)
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
        Log('CASTING ITEM LEN : %s' % len(items))
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

    ##############################################################
    # 2019-02-24. 다시 있는 에피소드만 가져오도록 한다. 
    parts = media.all_parts()
    episode_no_list = []
    episode_date_list = []
    #if flag_ending and parts[0].file.find(u'종영') == -1:
    #    metadata.title = u'[종영]%s' % metadata.title
    for p in parts:
        tmp = os.path.basename(p.file)
        match = Regex(r'([sS](?P<season>[0-9]{1,2}))?[eE](?P<ep>[0-9]{1,4})').search(tmp)
        if match:
            value = int(match.group('ep'))
            if value not in episode_no_list:
                episode_no_list.append(value)
        for regex in [
            r'[^0-9a-zA-Z](?P<year>[0-9]{2})(?P<month>[0-9]{2})(?P<day>[0-9]{2})[^0-9a-zA-Z]', # 6자리
            r'(?P<year>[0-9]{4})[^0-9a-zA-Z]+(?P<month>[0-9]{2})[^0-9a-zA-Z]+(?P<day>[0-9]{2})([^0-9]|$)',  # 2009-02-10 
        ]:
            match = Regex(regex).search(tmp)
            if match:
                value = '%s%s%s' % (match.group('year')[-2:], match.group('month'), match.group('day'))
                if value not in episode_date_list:
                    episode_date_list.append(value)
                    break
    Log('episode_no_list : %s', len(episode_no_list))
    Log('episode_date_list : %s', len(episode_date_list))
    episode_url_list = []
    items = root.xpath('//*[@id="clipDateList"]/li')
    if len(items) > 300: items = items[len(items)-300:]
    for item in items:
        a_tag = item.xpath('a') 
        if len(a_tag) != 1:
            continue
        query = 'https://search.daum.net/search%s' % a_tag[0].attrib['href']
        if item.attrib['data-clip'][-6:] in episode_date_list:
            episode_url_list.append(query)
        else:
            # r 뒤의 번호는 회차가 아님
            #match = Regex(r'\&r\=(?P<no>\d+)').search(a_tag[0].attrib['onclick'])
            match = Regex(ur'(?P<no>\d+)회').search(a_tag[0].text_content().strip())
            if match:
                if int(match.group('no')) in episode_no_list: 
                    episode_url_list.append(query)
    metadata.summary = '%s\r\n\r\nDaum:%s Match:%s' % (metadata.summary, len(items), len(episode_url_list))
    ##############################################################

    count = len(episode_url_list)
    Log('episode tag len : %s', count)
    for i in range(count-1, -1, -1):
        root = HTML.ElementFromURL(episode_url_list[i])
        items = root.xpath('//div[@class="tit_episode"]')
        episode = None
        if len(items) == 1:
            tmp = items[0].xpath('strong')
            if len(tmp) == 1:
                episode_frequency = unicodedata.normalize('NFKC', unicode(tmp[0].text)).strip()
                match = Regex(r'(\d+)').search(episode_frequency)
                if match:
                    Log('episode_frequency : %s i:%s', match.group(1), i)
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


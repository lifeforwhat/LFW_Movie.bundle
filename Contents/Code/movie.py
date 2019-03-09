# -*- coding: utf-8 -*-
import urllib, unicodedata

def searchMovie(results, media, lang):
    Log('SEARCH : %s %s' % (media.name, media.year))

    url = 'https://suggest-bar.daum.net/suggest?id=movie&cate=movie&multiple=1&mod=json&code=utf_in_out&q=%s' % (urllib.quote(media.name.encode('utf8')))
    data = JSON.ObjectFromURL(url)
    Log(data)
    for index, item in enumerate(data['items']['movie']):
        tmps = item.split('|')
        score = 95 - (index*5)
        if media.name == tmps[0] and tmps[3] == media.year:
            score = 100
        elif tmps[3] == media.year:
            score = score + 5
        if score < 10:
            score = 10
        results.Append(MetadataSearchResult(id=tmps[1], name=tmps[0], year=tmps[3], score=score, lang=lang))
    if len(data['items']['movie']) > 0:
        return

    url = 'https://search.daum.net/search?nil_suggest=btn&w=tot&DA=SBC&q=%s%s' % ('%EC%98%81%ED%99%94+', urllib.quote(media.name.encode('utf8')))
    html = HTML.ElementFromURL(url)
    try:
        movie = html.get_element_by_id('movieEColl')
        if movie is not None:
            title = movie.get_element_by_id('movieTitle')
            a_tag = title.find('a')
            href = a_tag.attrib['href']
            title = a_tag.find('b').text_content()
            results.Append(MetadataSearchResult(id=href.split('=')[1], name=title, year=media.year, score=100, lang=lang))
            tag_list = movie.find('div[@class="coll_etc"]').findall('.//a')
            for tag in tag_list:
                match = Regex(r'(.*?)\((.*?)\)').search(tag.text_content())
                if match:
                    daum_id = tag.attrib['href'].split('||')[1]
                    score = 80
                    if match.group(2) == media.year:
                        score = 90
                    results.Append(MetadataSearchResult(id=daum_id, name=match.group(1), year=match.group(2), score=score, lang=lang))
    except:
        import traceback
        Log(traceback.format_exc())    

# -*- coding: utf-8 -*-
import os
import urllib
import urllib2
import unicodedata
import traceback
import re
import datetime

def log(msg, *args, **kwargs):
    Log(msg, *args, **kwargs)


class DaumTV(object):
    @staticmethod
    def get_show_info_on_home(root):
        try:
            tags = root.xpath('//*[@id="tvpColl"]/div[2]/div/div[1]/span/a')
            # 2019-05-13
            #일밤- 미스터리 음악쇼 복면가왕 A 태그 2개
            if len(tags) < 1:
                return
            tag_index = len(tags)-1
            entity = {}
            entity['title'] = tags[tag_index].text
            Log('get_show_info_on_home title: %s', entity['title'])
            match = re.compile(r'q\=(?P<title>.*?)&').search(tags[tag_index].attrib['href'])
            if match:
                entity['title'] = urllib.unquote(match.group('title'))
            entity['id'] = re.compile(r'irk\=(?P<id>\d+)').search(tags[tag_index].attrib['href']).group('id')

            entity['status'] = 1  
            tags = root.xpath('//*[@id="tvpColl"]/div[2]/div/div[1]/span/span')
            if len(tags) == 1:
                if tags[0].text == u'방송종료':
                    entity['status'] = 2
                elif tags[0].text == u'방송예정':
                    entity['status'] = 0
            Log('get_show_info_on_home status: %s', entity['status'])
            tags = root.xpath('//*[@id="tvpColl"]/div[2]/div/div[1]/div')
            entity['extra_info'] = tags[0].text_content().strip()
            Log('get_show_info_on_home extra_info: %s', entity['extra_info'])

            entity['studio'] = ''
            tags = root.xpath('//*[@id="tvpColl"]/div[2]/div/div[1]/div/a')
            if len(tags) == 1:
                entity['studio'] = tags[0].text
            else:
                tags = root.xpath('//*[@id="tvpColl"]/div[2]/div/div[1]/div/span[1]')
                if len(tags) == 1:
                    entity['studio'] = tags[0].text
            Log('get_show_info_on_home studio: %s', entity['studio'])

            tags = root.xpath('//*[@id="tvpColl"]/div[2]/div/div[1]/div/span')
            entity['extra_info_array'] = [tag.text for tag in tags]

            try:
                entity['year'] = re.compile(r'(?P<year>\d{4})').search(entity['extra_info_array'][-1]).group('year')
                Log('get_show_info_on_home 1: %s', entity['status'])
            except:
                #entity['year'] = str(datetime.datetime.now().year)
                entity['year'] = ''
            #시리즈
            entity['series'] = []
            entity['series'].append({'title':entity['title'], 'id' : entity['id'], 'year' : entity['year']})
            tags = root.xpath('//*[@id="tv_series"]/div/ul/li')

            if tags:
                # 2019-03-05 시리즈 더보기 존재시
                try:
                    more = root.xpath('//*[@id="tv_series"]/div/div/a')
                    url = more[0].attrib['href']
                    if not url.startswith('http'):
                        url = 'https://search.daum.net/search%s' % url
                    Log('MORE URL : %s', url)
                    if more[0].xpath('span')[0].text == u'시리즈 더보기':
                        more_root = HTML.ElementFromURL(url)
                        tags = more_root.xpath('//*[@id="series"]/ul/li')
                except Exception as e:
                    log('Not More!')
                    log(traceback.format_exc())

                for tag in tags:
                    dic = {}
                    dic['title'] = tag.xpath('a')[0].text
                    dic['id'] = re.compile(r'irk\=(?P<id>\d+)').search(tag.xpath('a')[0].attrib['href']).group('id')
                    if tag.xpath('span'):
                        dic['date'] = tag.xpath('span')[0].text
                        dic['year'] = re.compile(r'(?P<year>\d{4})').search(dic['date']).group('year')
                    else:
                        dic['year'] = None
                    entity['series'].append(dic)
                entity['series'] = sorted(entity['series'] , key=lambda k: int(k['id'])) 
            Log('SERIES : %s', len(entity['series']))
            #동명
            entity['equal_name'] = []
            tags = root.xpath(u'//div[@id="tv_program"]//dt[contains(text(),"동명 콘텐츠")]//following-sibling::dd')
            if tags:
                tags = tags[0].xpath('*')
                for tag in tags:
                    if tag.tag == 'a':
                        dic = {}
                        dic['title'] = tag.text
                        dic['id'] = re.compile(r'irk\=(?P<id>\d+)').search(tag.attrib['href']).group('id')
                    elif tag.tag == 'span':
                        match = re.compile(r'\((?P<studio>.*?),\s*(?P<year>\d{4})?\)').search(tag.text)
                        if match:
                            dic['studio'] = match.group('studio')
                            dic['year'] = match.group('year')
                        elif tag.text == u'(동명프로그램)':
                            entity['equal_name'].append(dic)
                        elif tag.text == u'(동명회차)':
                            continue
            log(entity)
            return entity
        except Exception as e:
            log('Exception get_show_info_by_html : %s', e)
            log(traceback.format_exc())



# -*- coding: utf-8 -*-
import os
import urllib
import urllib2
import unicodedata
import traceback
import re

def log(msg, *args, **kwargs):
    Log(msg, *args, **kwargs)


class DaumTV(object):
    @staticmethod
    def get_show_info_on_home(root):
        try:
            tags = root.xpath('//*[@id="tvpColl"]/div[2]/div/div[1]/span/a')
            if len(tags) != 1:
                return
            entity = {}
            entity['title'] = tags[0].text
            entity['id'] = re.compile(r'irk\=(?P<id>\d+)').search(tags[0].attrib['href']).group('id')

            entity['status'] = 1  
            tags = root.xpath('//*[@id="tvpColl"]/div[2]/div/div[1]/span/span')
            if len(tags) == 1:
                if tags[0].text == u'방송종료':
                    entity['status'] = 2
                elif tags[0].text == u'방송예정':
                    entity['status'] = 0
            
            tags = root.xpath('//*[@id="tvpColl"]/div[2]/div/div[1]/div')
            entity['extra_info'] = tags[0].text_content().strip()

            tags = root.xpath('//*[@id="tvpColl"]/div[2]/div/div[1]/div/a')
            entity['studio'] = tags[0].text
            
            tags = root.xpath('//*[@id="tvpColl"]/div[2]/div/div[1]/div/span')
            entity['extra_info_array'] = [tag.text for tag in tags]

            entity['year'] = re.compile(r'(?P<year>\d{4})').search(entity['extra_info_array'][-1]).group('year')
            
            #시리즈
            entity['series'] = []
            entity['series'].append({'title':entity['title'], 'id' : entity['id'], 'year' : entity['year']})
            tags = root.xpath('//*[@id="tv_series"]/div/ul/li')
            if tags:
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
                        match = re.compile(r'\((?P<studio>.*?),\s*(?P<year>\d{4})\)').search(tag.text)
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



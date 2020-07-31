import os, json
from collections import OrderedDict
#import requests
try:
    import requests
    plex = False
    Log.Info('requests imported')
except:
    import urllib, unicodedata, traceback, re
    plex = True
    Log.Info('requests not imported')
from time import sleep


class watcha:
    def __init__(self, keyword , year=None , year_diff_allow = 1 , media_type='top' , cookie = False): # media_type 에 따라서 movie, tv 를 결정해준다. 정 모르겠으면 top으로 설정할 것.
        self.c_header = {
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
            'x-watcha-client-version': '1.0.0',
            'cookie' : cookie if cookie != False else ''
        }
        if plex == False:
            res = requests.get('https://api.watcha.com/api/searches/contents/movies?query='+keyword, headers = self.c_header)
            j = res.json()
        else:
            movie_name = urllib.quote(keyword.encode('utf8'))
            Log.Info(str(keyword))
            j = JSON.ObjectFromURL('https://api.watcha.com/api/searches/contents/movies?query=%s' % (movie_name),
                        headers = self.c_header)
            Log.Info(str(j))

        """if media_type == "top":
            result = j['result']['top_results']
        elif media_type == "movies":
            result = j['result']['movies']
        elif media_type == "tv":
            result = j['result']['tv_seasons']"""
        result = j['result']['result']

        if year != None: # year값이 주어졌다면 year로 비교해준다.
            year = int(year)
            result_sorted = [item for item in result if str(item['year']) == year] # 이게 베스트
            result_sorted += [item for item in result if str(item['year']) != year and abs(item['year'] - int(year)) <= year_diff_allow] # year_diff_allow 보다 값이 작거나 같아야지만 허용한다
            result = result_sorted

        try:
            best = result[0]
            best_code = best['code']
            diction = {}
            diction['출연'] = self.characters(best_code)
            diction['코멘트'] = self.comments(best_code)
            diction['컬렉션'] = self.collection(best_code)
            diction['API_INFO'] = self.api_info(best_code)
            self.info = diction
            try:
                Log.Info("BESTINFO")
                Log.Info(str(best['current_context']['predicted_rating']))
                self.predicted_rating = best['current_context']['predicted_rating']
            except:
                self.predicted_rating = ""
        except IndexError:
            print("NOTHING FOUND (%s)" % (keyword))

    def api_info(self, code):
        if plex == False:
            res = requests.get('https://api.watcha.com/api/contents/'+code , headers= self.c_header)
            j = res.json()
        else :
            j = JSON.ObjectFromURL('https://api.watcha.com/api/contents/'+code , headers= self.c_header)
            #Log.Info(str(j))
        return j['result']

    def collection(self, code, amount = 100): # amount 는 페이지당 20이 api의 최대값인가본데, 억지로 끌어온다
        if amount <= 20  :
            base_url = 'https://api.watcha.com/api/contents/'+code+'/decks?default_version=20&page=1&size='+str(amount)+'&vendor_string=frograms'
            if plex == False:
                res = requests.get(base_url, headers = self.c_header)
                j = res.json()
            else:
                j = JSON.ObjectFromURL(base_url, headers=self.c_header)
                #Log.Info(str(j))
            result = j['result']['result']
            return result
        else:
            page = 1
            result = []
            while True:
                base_url = 'https://api.watcha.com/api/contents/' + code + '/decks?default_version=20&page='+str(page)+'&size=20&vendor_string=frograms'
                if plex == False:
                    res = requests.get(base_url, headers=self.c_header)
                    if res.status_code != 200:
                        break
                    j = res.json()
                else:
                    try:
                        j = JSON.ObjectFromURL(base_url, headers=self.c_header)
                    except:
                        break
                    #Log.Info(str(j))

                result += j['result']['result']
                if len(result) >= amount or len(j['result']['result']) == 0:
                    break
                page += 1
            return result

    def characters(self, code, amount=50):
        if amount <= 20  :
            base_url = 'https://api.watcha.com/api/contents/'+code+'/credits?default_version=20&page=1&size=20&vendor_string=frograms'
            if plex == False:
                res = requests.get(base_url , headers = self.c_header)
                j = res.json()
            else:
                j = JSON.ObjectFromURL(base_url, headers=self.c_header)
            result = j['result']['result']
            return result
        else:
            page = 1
            result = []
            while True:
                base_url = 'https://api.watcha.com/api/contents/'+code+'/credits?default_version=20&page='+str(page)+'&size=20&vendor_string=frograms'
                if plex == False:
                    res = requests.get(base_url, headers=self.c_header)
                    if res.status_code != 200:
                        break
                    j = res.json()
                else:
                    try:
                        j = JSON.ObjectFromURL(base_url, headers=self.c_header)
                    except:
                        break
                    #Log.Info(str(j))
                result += j['result']['result']
                if len(result) >= amount or len(j['result']['result']) == 0 :
                    break
                page += 1
            return result

    def comments(self, code, style = "popular", amount = 100): # style can be 'popular'(좋아요 순) , 'recommended' (유저 반응 순) , 'high' (높은 평가 순), 'low' (낮은 평가 순), 'recent' (작성 순) , 최대 amount는 20까지 가능하지만 억지로 더 끌어온다
        if amount <= 20  :
            base_url = 'https://api.watcha.com/api/contents/'+code+'/comments?default_version=20&filter=all&order='+str(style)+'&page=1&size='+str(amount)+'&vendor_string=frograms'
            if plex == False:
                res = requests.get(base_url , headers = self.c_header)
                j = res.json()
            else:
                j = JSON.ObjectFromURL(base_url, headers=self.c_header)
            result = j['result']['result']
            return result
        else:
            page = 1
            result = []
            while True:
                base_url = 'https://api.watcha.com/api/contents/'+code+'/comments?default_version=20&filter=all&order='+str(style)+'&page='+str(page)+'&size='+str(amount)+'&vendor_string=frograms'
                if plex == False:
                    res = requests.get(base_url, headers=self.c_header)
                    if res.status_code != 200:
                        break
                    j = res.json()
                else:
                    try:
                        j = JSON.ObjectFromURL(base_url, headers=self.c_header)
                    except:
                        break
                    #Log.Info(str(j))
                result += j['result']['result']
                if len(result) >= amount or len(j['result']['result']) == 0:
                    break
                page += 1
            return result



if __name__ == '__main__':
    a = watcha(keyword='알라딘' ,year=2019 , media_type='movies')
    a
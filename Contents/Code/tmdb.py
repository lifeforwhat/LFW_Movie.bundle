try:
    import requests
    plex = False
except:
    import urllib, unicodedata, traceback, re
    plex = True

class tmdb:
    def search(self, name, year, lang='en'):
        if lang == "en":
            base_url = 'https://api.themoviedb.org/3/search/movie?api_key=b2f505af2cb75d692419696af851e517&language=en-US&query='+name+'&page=1&include_adult=true&year='+str(year)
            if plex == False:
                res = requests.get(base_url)
                j = res.json()['results'][0]
            else:
                j = JSON.ObjectFromURL(base_url)['results'][0]
        elif lang == 'ko':
            base_url = 'https://api.themoviedb.org/3/search/movie?api_key=b2f505af2cb75d692419696af851e517&language=ko-KR&query=' + name + '&page=1&include_adult=true&year=' + str(year)
            if plex == False:
                res = requests.get(base_url)
                j = res.json()['results'][0]
            else:
                j = JSON.ObjectFromURL(base_url)['results'][0]

        c = self.find_in_tmdb_Collection(movie=j)
        return j , c

    def find_in_tmdb_Collection(self, movie):
        ID = movie['id']
        base_url = 'https://api.themoviedb.org/3/movie/' + str(ID) + '?api_key=b2f505af2cb75d692419696af851e517&language=en-US'
        if plex == False:
            res = requests.get(base_url)
            j = res.json()
        else:
            j = JSON.ObjectFromURL(base_url)
        collectionID = ""
        try:
            collectionID = j['belongs_to_collection']['id']
        except:
            pass
        if collectionID != "":
            base_url = 'https://api.themoviedb.org/3/collection/' + str(collectionID) + '?api_key=b2f505af2cb75d692419696af851e517&language=ko-KR'
            if plex == False:
                coll_res = requests.get(base_url)
                jc = coll_res.json()
            else:
                jc = JSON.ObjectFromURL(base_url)
        try:
            return jc
        except:
            return ""

if __name__ == '__main__':
    a , b= tmdb().search('deadpool 2' , year=2018)
    a
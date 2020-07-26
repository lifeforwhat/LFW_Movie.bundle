import requests, os, sys, json, shutil

from bs4 import BeautifulSoup





def FindFirst(first, word):

    Remover_1 = word.find(first)

    Result = word[Remover_1:]

    return Result





def FindExceptFirst(first, word):

    Remover_1 = word.find(first)

    Result = word[Remover_1 + len(first):]

    return Result





def FindEnd(end, word):

    Remover_2 = word.find(end)

    Result = word[:Remover_2]

    return Result





def Except_First_To_And_After_Except_Second(first, second, word):  # first까지 자르고 그 후 다시 찾아서 second까지 자름

    result = FindExceptFirst(first, word)

    result = FindEnd(second, result)

    return result





def find_movie(name):

        try:

            daum_search = requests.get('https://search.daum.net/search?w=tot&q=' + name)

            movieTitle = BeautifulSoup(daum_search.text, 'html.parser').select_one('#movieTitle')

            movieTitle_link = movieTitle.contents[1].attrs['href']

            #best_movie_id = diction['items']['movie'][0].split('|')[1]

            best_movie_id = FindExceptFirst('movieId=',movieTitle_link)
        except:
            return ""



        # 추가적으로 더 다운로드

        url = "https://movie.daum.net/moviedb/video?id=" + best_movie_id

        video_res = requests.get(url)

        vclipid = Except_First_To_And_After_Except_Second(r'vclipId=','"',video_res.text)

        video_list = []

        for i in range(1,5):

            try:

                url = "https://movie.daum.net/moviedb/videolist?id="+best_movie_id+"&vclipId=&mainVclipId=" + vclipid + "&page="+str(i)

                res = requests.get(url)

                soup = BeautifulSoup(res.text , 'html.parser')

                temp_list = soup.contents[3].contents

                for temp in temp_list:

                    try:

                        view_count = Except_First_To_And_After_Except_Second("재생수","\n",temp.text).replace(',','').strip()

                        id = Except_First_To_And_After_Except_Second('(',',',temp.contents[1].attrs['href'])

                        video_list.append([int(view_count), id])

                    except:continue

                print(t)



            except:

                continue

        video_list.sort()

        video_list.reverse()

        maximum = 5

        for i in range(1,maximum+1):

            try:

                id = video_list[i-1][1]

                url = "https://movie.daum.net/moviedb/video?id="+best_movie_id+"&vclipId="+id

                video_res = requests.get(url)

                soup = BeautifulSoup(video_res.text, 'html.parser')

                title = soup.select_one('#mArticle > div.movie_player > div > strong').text

                # meta property="og:image" content="

                video_code = Except_First_To_And_After_Except_Second("getPlayerIframeSrc('", "')",video_res.text)  # .replace('http://.','').strip()

                url = "https://kakaotv.daum.net/api/v3/ft/cliplinks/" + video_code + "@my/raw?player=monet_html5&referer=https%3A%2F%2Fmovie.daum.net%2Fmoviedb%2Fvideo%3Fid%3D61057&uuid=04015a3d236af68de4dbbc65633271a1&service=daum_movie&section=daum_movie&fields=seekUrl,abrVideoLocationList&playerVersion=3.1.4&tid=8314690bf37da0eb3722e43c26c205bc&profile=HIGH&dteType=PC&continuousPlay=false&contentType="

                res = requests.get(url).text

                tri = json.loads(res)

                source = tri['videoLocation']['url']

                folder_name = "Other" # Default

                if title.count('인터뷰') > 0:

                    folder_name = "Interviews"

                if title.count('비하인드') > 0 :

                    folder_name = "Behind The Scenes"

                if title.count('예고편') > 0 :

                    folder_name = "Trailers"

                if title.count('리뷰') > 0 :

                    folder_name = "Trailers"

                if title.count('제작기') > 0 :

                    folder_name = "Behind The Scenes"

                if title.count('코멘터리') > 0 :

                    folder_name = "Interviews"

                if title.count('메이킹') > 0 :

                    folder_name = "Featurette"

                if title.count('시사회') > 0 :

                    folder_name = "Featurette"

                if title.count('삭제') > 0 :

                    folder_name = "Deleted Scenes"

                try:

                    local_filename = os.path.join(os.path.join(fullFilename,folder_name), title + '.mp4')

                    if os.path.isdir(os.path.join(fullFilename,folder_name)) == False:

                        os.mkdir(os.path.join(fullFilename,folder_name))

                    if os.path.isfile(os.path.join(os.path.join(fullFilename,folder_name), title + '.mp4')) == True:

                        print(fullFilename, ' already exist...')

                        continue

                    with requests.get(source, stream=True, timeout=5) as r:

                        with open(local_filename, 'wb') as f:

                            shutil.copyfileobj(r.raw, f)

                    print(local_filename, ' success')

                except Exception as e:

                    print(e + ' :: download failed')

            except:continue

        print(fullFilename, ' DONE!!')

if __name__ == '__main__':
    find_movie('기생충')
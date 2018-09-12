[다음영화](http://movie.daum.net)에서 영화/드라마 정보를 가져오는 Plex용 Metadata Agent입니다.

[드라마를 위한 Metadata Agent](https://github.com/hojel/DaumMovieTv.bundle)가 따로 있었으나 통합됨.

설정
==============

1. 영화 ID 덮어쓰기
   - _None_: 다음영화 ID를 유지
   - _IMDB_: [IMDB](http://www.imdb.com) ID를 대신 넘겨줌. OpenSubtitles Agent와 연결에 필요.
2. 드라마 ID 덮어쓰기
   - _None_: 다음영화 ID를 유지
   - _TVDB_: [TVDB](http://www.thetvdb.com) ID를 대신 넘겨줌. OpenSubtitles Agent와 연결에 필요.

OpenSubtitles과의 연결
==============

1. Plex Plug-in folder에서 OpenSubtitles.bundle 을 찾는다.
2. Contents/Code/__init__.py 를 다음과 같이 수정한다.

    \- contributes_to = ['com.plexapp.agents.imdb']
    \+ contributes_to = ['com.plexapp.agents.imdb', 'com.plexapp.agents.daum_movie']

    \- contributes_to = ['com.plexapp.agents.thetvdb']
    \+ contributes_to = ['com.plexapp.agents.thetvdb', 'com.plexapp.agents.daum_movie']

3. DaumMovie.bundle의 설정에서 영화 ID 덮어쓰기로 _IMDB_, 드라마 ID 덮어쓰기로 _TVDB_를 각각 선택한다.

FanartTV.bundle 에도 사용가능하다.

20180912
==============
다음 TV 수정

업데이트 버전이 나오지 않아 수정했으나, axfree님이 수정해주셨다.
[https://github.com/axfree/DaumMovie.bundle]https://github.com/axfree/DaumMovie.bundle

방식은 별로 다르진 않지만, 이 버전은 에피소드 파일이 있는 에피소드만 긁어온다.
이전에는 JSON으로 한번에 전체 에피소드 내용을 가져왔지만, 이제는 매 에피소드 마다 http request 를 보내야한다. 인간극장을 업데이트 할 경우 500번 정도 http request를 날린다.
이를 방지하고자 파일이 있는 에피소드만 가져오게 했다. (파일명에 방송일 정보가 있어야 함)

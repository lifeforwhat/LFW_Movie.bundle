ChangeLog
==============
#### 20190208
- 영화 search 수정
  - 영화페이지 자동 완성 url 사용
  - 자동완성에서 나오지 않을 경우 메인 검색 이용

#### 20190110
- 에피소드 파일이 있는 부분만 가져오는 부분 제거
- 타 버전과 다른점
  - 제목에 날짜 삽입
  - 에피소드별 이미지도 Daum에서 가져옴

#### 20180912
다음 TV 수정

업데이트 버전이 나오지 않아 수정했으나, axfree님이 수정해주셨다.
[https://github.com/axfree/DaumMovie.bundle](https://github.com/axfree/DaumMovie.bundle)

방식은 별로 다르진 않지만, 이 버전은 에피소드 파일이 있는 에피소드만 긁어온다.
이전에는 JSON으로 한번에 전체 에피소드 내용을 가져왔지만, 이제는 매 에피소드 마다 http request 를 보내야한다. 인간극장을 업데이트 할 경우 500번 정도 http request를 날린다.
이를 방지하고자 파일이 있는 에피소드만 가져오게 했다. (파일명에 방송일 정보나 에피소드 번호가 있어야 함)

#### 20180921
- ~~[스캐너](https://github.com/soju6jan/Plex-Series-Scanner-For-Korea) 연동~~
  + ~~다음에 에피소드 정보가 없을 경우 에피소드 회차가 있더라도 날짜로 먼저 인식~~





# 원본
[다음영화](http://movie.daum.net)에서 영화/드라마 정보를 가져오는 Plex용 Metadata Agent입니다.

[드라마를 위한 Metadata Agent](https://github.com/hojel/DaumMovieTv.bundle)가 따로 있었으나 통합됨.

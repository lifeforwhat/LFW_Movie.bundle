![int3](https://user-images.githubusercontent.com/59600370/88552620-449f9100-d05f-11ea-8b15-9366dc45c1f6.png)
![int4](https://user-images.githubusercontent.com/59600370/88552633-48cbae80-d05f-11ea-9e65-df78d40cb328.png)
![image](https://user-images.githubusercontent.com/59600370/88553054-d0192200-d05f-11ea-81b7-569039cfe1c1.png)
![1595863356064](https://user-images.githubusercontent.com/59600370/88560154-baf4c100-d068-11ea-9d07-0c20be826cbb.jpg)

# SJ_Daum.bundle 에서 포크

포크하면서 추가한 기능 (2020-07-30 추가)

![image](https://user-images.githubusercontent.com/59600370/89054423-b9dad100-d393-11ea-81ce-ce85c2468a8c.png)

imdb 평점 덮어씌우기

![image](https://user-images.githubusercontent.com/59600370/89059267-d975f780-d39b-11ea-8355-9158795ce41a.png)


imdb 점수별 컬렉션 생성

fallback 설정

# 기존 SJ_Daum.bundle 과의 차이점

TMDb 컬렉션

왓챠 컬렉션 

왓챠 평론가 평론 (Official_user == True)

왓챠 컬렉션 블랙리스트

왓챠 개인별 점수 컬렉션화

평론가 블랙리스트

네이버 평론가 크롤

평론가 점수가 특정 점수 이하이면 로튼 토마토 표기

# TODO

평론가 화이트리스트 (특정 평론가 우선순위 정하기)

왓챠 점수 덮어씌우기

챕터

트레일러

구글 DOCS 를 이용해 매칭 시스템 정교화(혹은 수동화 또는 위키화로 부를 수 있을듯)

# 왓챠 쿠키 얻는 법

![image](https://user-images.githubusercontent.com/59600370/88553501-50d81e00-d060-11ea-9eb1-b0d99f0935b2.png)

크롬 개발자모드(F12) 들어가셔서 Network 들어가신 후 찾으시면 됩니다.

## 자세한 왓챠 쿠키 얻는 법

1) https://pedia.watcha.com/ko-KR/contents/m5ewr3z 해당 페이지에 들어갑니다. 로그인이 되어있어야만 합니다.

2) F12를 누릅니다.

3) Network 탭에 들어갑니다.

![image](https://user-images.githubusercontent.com/59600370/88563497-01e4b580-d06d-11ea-8739-83680229b0eb.png)

4) Name 탭에 m5ewr3z 항목을 찾습니다.

5) 오른쪽 탭(Headers)에서 Requests Headers 항목에서 cookie 값을 복사한 뒤 설정에 붙여넣습니다.

# FAQ

## 에이전트가 나타나지 않습니다.

.xml 파일이 형성되지 않은 것으로 보입니다.

에이전트 > 영화 > The Movie Database 에이전트에 들어간 후 아래에 나타나는 LFW Movie 옆 톱니바퀴를 눌러 .xml 파일을 생성해 줍니다.

![image](https://user-images.githubusercontent.com/59600370/89057836-4471ff00-d399-11ea-9288-a43c2da0ce96.png)

그리고 PMS 를 재시작하면 영화 에이전트 내에서 LFW Movie 에이전트가 나타납니다.



## 설정이 저장되지 않습니다.

이는 한글 때문에 저장이 되지 않는 것입니다.

xml 파일을 직접 수정해주시면 됩니다.

윈도우를 기준으로 아래의 경로에 존재합니다.

![image](https://user-images.githubusercontent.com/59600370/89057975-73887080-d399-11ea-9d0c-19c83e298f9f.png)

파일을 열어서 수정하시면 됩니다.


![image](https://user-images.githubusercontent.com/59600370/89058056-9a46a700-d399-11ea-87e7-5da6a17afd6e.png)

아래와 같은 규칙으로 되어있으니, 구분자에 맞게끔 원하는 대로 수정하시길 바랍니다.



# Thanks to

Soju6jan

Naver Travel Time Component
============================
home assistant 용 네이버 경로 소요시간 컴포넌트입니다.

실시간으로 빠른 경로의 소요시간을 출력합니다.

설치방법
---------
  custom_components/sensor 폴더에 naver_travel_time.py를 복사합니다.
  
네이버 지도 api key 획득 방법
 --------------------------  
 1) 네이버 지도 api 사용을 위해 [Naver cloud platform](https://www.ncloud.com/?language=ko-KR)에 가입합니다.

    가입 시 결제 수단 등록이 필요합니다.
 
 **※네이버 지도 api는 2019년 프로모션 중으로 월 60,000건 이하는 무료 사용 가능합니다. 60,000건 이상은 과금됩니다.**
   
   **다만 2019년 이후 과금정책은 어떻게 될지 모르며 과금된 금액에 대해서는 책임지지 않습니다.**
  
  2) 콘솔을 열어 my product에 AI.NAVER API를 추가합니다.
  
  3) Application 등록을 눌러서 내용을 입력합니다.
  
   - Application 이름 설정에 원하시는 이름을 입력합니다.
  
   - Service 선택에서 MAPS의 Directions를 선택합니다.
  
   - 서비스 환경설정에서 Web Service URL에 HA의 URL을 Port를 포함해 입력합니다.(외부접속 가능한 URL)
 
  4) 인증정보를 눌러 client id와 client key를 복사합니다.

HA configuration.yaml 등록 방법
-----------------------------  
  configuration.yaml에 아래 예와 같이 등록하시면 됩니다. entity id는 'sensor.설정한name'으로 설정됩니다. 완료하시면 그림과 같이 사용하실 수 있습니다.

~~~yaml
sensor:
  platform: naver_travel_time
  name: 'Travel Time' #원하는 이름을 입력(entity id로 이용됨)
  client_id: YOUR_CLIENT_ID #획득한 client id를 입력
  api_key: YOUR_CLIENT_KEY #획득한 client key를 입력
  origin: 127.1045942,37.3590548 #출발지를 입력
                                 #(좌표를 longitude,latitude 로 입력, 또는 좌표를 출력하는 device_tracker, zone, sensor이용가능)
  destination: zone.home #도착지를 입력(입력 방법은 출발지와 동일)
  waypoint:  #옵션으로 waypoint를 추가할 수 있습니다.(최대 5개)
    waypoint1: #waypoint입력(입력방법은 출발지, 도착지와 동일)
~~~

SreenShot
---------
<img width="355" alt="screenshot" src="https://user-images.githubusercontent.com/37936802/52165495-01ec4980-2745-11e9-86c1-d1ea2e3e1d45.png">

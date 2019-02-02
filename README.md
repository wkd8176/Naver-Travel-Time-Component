# Naver Travel Time Component
home assistant 용 네이버 경로 소요시간 컴포넌트입니다.
실시간으로 빠른 경로의 소요시간을 출력합니다.

1. 설치방법<br>
  custom_components/sensor 폴더에 naver_travel_time.py를 복사합니다.
  
2. 네이버 지도 api key 획득 방법<br>
  1) 네이버 지도 api 사용을 위해 naver cloud platform에 가입합니다.<https://www.ncloud.com/?language=ko-KR>
  2) 콘솔을 열어 my product에 AI.NAVER API를 추가합닏.
  3) Application 등록을 눌러서 내용을 입력합니다.
   - Application 이름 설정에 원하시는 이름을 입력합니다.
   - Service 선택에서 MAPS의 Directions를 선택합니다.
   - 서비스 환경설정에서 Web Service URL에 HA의 URL을 Port를 포함해 입력합니다.(외부접속 가능한 URL)
  4) 인증정보를 눌러 client id와 client key를 복사합니다.
  
3. HA configuration.yaml 등록 방법<br>
  configuration.yaml에 아래 예와 같이 등록하시면 됩니다. entity id는 'sensor.설정한name'으로 설정됩니다. 완료하시면 그림과 같이 사용하실 수 있습니다.
  
    sensor:
      - platform: naver_travel_time
        name: 'Travel Time' #원하는 이름을 입력(entity id로 이용됨)
        client_id: YOUR_CLIENT_ID #획득한 client id를 입력
        api_key: YOUR_CLIENT_KEY #획득한 client key를 입력
        origin: 127.1045942,37.3590548 #출발지를 입력
                                       #(좌표를 latitude,longitude 로 입력, 또는 좌표를 출력하는 device_tracker, zone, sensor이용가능)
        destination: #도착지를 입력(입력 방법은 출발지와 동일)
      
4. SreenShot<br>
<img width="355" alt="screenshot" src="https://user-images.githubusercontent.com/37936802/52165495-01ec4980-2745-11e9-86c1-d1ea2e3e1d45.png">

# robot-alarm

## 1. 프로젝트 소개
  물리적으로 사용자를 깨워주는 로봇을 만드는 프로젝트입니다.

## 2. 프로젝트 목표와 제약
  잠에서 잘 깨어나지 못하는 사람을 로봇이 적당한 충격을 주거나, 빛을 비춰 깨우는 기능이 목표입니다.
본 프로젝트는 웹을 통해 알람 정보를 설정하게 되어있으므로, 웹 앱이 동작할 수 있는 서버가 필요하고 계속 실행되어야 합니다.
서버와 로봇 간에는 http method를 통한 상호작용이 가능하도록 연결이 되어 있어야 합니다.

## 3. 사용된 기술 스택과 기계

   Ubuntu 20.04

   ROS2
   
   Python 3.8.10

   flask 3.0.3

   MOATECH 35mm 스테퍼 모터(x, y 총 2개)

   MS 905 모터
   
## 4. 프로젝트 구조
   
   #### html
- 사용자 인터페이스로 다음과 같은 정보를 받습니다.
1. 로봇의 IP(ip_address)
2. x 좌표(x_coord)
3. y 좌표(y_coord_
4. 알람 시각(time)
5. 모터(motor)
  
  #### flask
- 사용자의 정보를 받아서 ROS2 node에 topic 방식으로 발행합니다.
1. ip_address_publisher
2. y_coord_publisher
3. y_coord_publisher
4. time_publisher
5. motor_publisher

  #### TimeNode
- time을 topic으로 구독하여 local 시간과 비교하여 같으면 alarm event를 발행하고,
1분 후 ready event를 발행하여 대기 상태로 전환합니다.
1. time_subcriber
2. alarm_publisher
3. ready_publisher

  #### XCoordNode
- ip_address와 x_coord를 구독하여 저장하고, alarm event가 발생하면 http method로 로봇을 제어합니다.
1분 후 ready event가 발생하면 x_coord를 0으로 로봇을 제어합니다.
1. ip_address_subcriber
2. x_coord_subcriber
3. alarm_subcriber
4. ready_subcriber
    
  #### YCoordNode
- ip_address와 y_coord를 구독하여 저장하고, alarm event가 발생하면 http method로 로봇을 제어합니다.
1분 후 ready event가 발생하면 y_coord를 0으로 로봇을 제어합니다.
1. ip_address_subcriber
2. y_coord_subcriber
3. alarm_subcriber
4. ready_subcriber
  
  #### MotorNode
- ip_address와 motor를 구독하여 저장하고, alarm event가 발생하면 http method로 로봇을 제어합니다.
1분 후 ready event가 발생하면 motor를 0으로 로봇을 제어합니다.
1. ip_address_subcriber
2. motor_subcriber
3. alarm_subcriber
4. ready_subcriber

## 5. 컴파일 및 빌드 방법
1. Ubuntu 20.04에 ROS22 설치 (https://puzzling-cashew-c4c.notion.site/ROS-2-Foxy-Linux20-04-58f0c6f2537e498eb8fe163ad1f13ce5)
2. sudo apt update
3. sudo apt install python3
3. flask 설치 (pip install flask)
4. git clone으로 소스코드 받기
5. 프로젝트 최상위 디렉토리에서 colcon build
6. 새로운 터미널을 열고 최상위 디렉토리에서 아래 명령 실행
7. source install/local_setup.bash
8. rosfoxy
9. ros2 run my_package my_node

만약 위의 방법이 되지 않으면,
1. Ubuntu 20.04에 ROS2 설치 (https://puzzling-cashew-c4c.notion.site/ROS-2-Foxy-Linux20-04-58f0c6f2537e498eb8fe163ad1f13ce5)
2. sudo apt update
3. sudo apt install python3
4. flask 설치 (pip install flask)
5. 프로젝트 폴더에서 ros2 pkg create --build-type ament_python --node-name my_node my_package
6. src/my_package/my_package/my_node.py에 다운받은 my_node.py 붙여넣기
7. 최상위 디렉토리에서 colcon build
8. install/my_package/share/my_package/templates/index.html을 생성하여 다운받은 index.html 넣기
9. 새로운 터미널을 열고 최상위 디렉토리에서 아래 명령 실행
10. source install/local_setup.bash
11. rosfoxy
12. ros2 run my_package my_node
   
## 6. 향후 계획
- topic 통신이 잘 안되는 이슈 해결
- 코드를 노드 별로 분할하여 리팩토링
- 빛 관련 노드를 추가해 반짝이는 기능 추가
- 예외 처리 및 실패 시 재전송 추가

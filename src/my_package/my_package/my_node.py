import os
import threading
from ament_index_python.packages import get_package_share_directory
import time
from flask import Flask, request, send_file
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int32

app = Flask(__name__)

# ROS 노드 1: 시각을 구독하고 알람을 발행하는 노드
class TimeNode(Node):

    def __init__(self):
        super().__init__('time_node')
        self.alarm_publisher = self.create_publisher(String, 'alarm_topic', 10)
        self.timer = self.create_timer(60, self.publish_alarm)
        self.ready_publisher = self.create_publisher(String, 'ready_topic', 10)
        self.time_subcriber = self.create_subscription(String, 'time_topic', self.subscribe_time, 10)
        self.get_logger().info('Time node initialized')
        self.alarm_time = None

    def publish_alarm(self):
        current_time = time.strftime("%H:%M", time.localtime())
        print(current_time, type(current_time))
        if self.alarm_time and self.alarm_time == current_time:
            msg = String()
            msg.data = self.alarm_time
            self.alarm_publisher.publish(msg)
            self.get_logger().info('Publishing received time: {}'.format(self.alarm_time))
            # 1분 후 대기
            self.create_timer(60, self.publish_ready)
        elif self.alarm_time and self.alarm_time != current_time:
            self.get_logger().warn('Current time is not alarm time')
        else:
            self.get_logger().warn('No time received yet')

    def publish_ready(self):
        msg = String()
        msg.data = "Ready"
        self.ready_publisher.publish(msg)
        self.get_logger().info('Publishing "Ready" message')

    def subscribe_time(self, time_str):
        time = time_str.data
        self.alarm_time = time
        self.get_logger().info('Received time!!!!!!!!!!!!!--------------------: {}'.format(time_str))
        
# ROS 노드 2: x좌표를 받고, 기계를 제어하는 노드
class XCoordNode(Node):
    def __init__(self):
        super().__init__('x_coord_node')
        self.alarm_subcriber = self.create_subscription(String, 'alarm_topic', self.alarm_callback, 10)
        self.ready_subcriber = self.create_subscription(String, 'ready_topic', self.ready_callback, 10)
        self.x_coord_subcriber = self.create_subscription(Int32, 'x_coord_topic', self.subscribe_x_coord, 10)
        self.ip_address_subcriber = self.create_subscription(String, 'ip_address_topic', self.subscribe_ip_address, 10)

        self.get_logger().info('XCoord node initialized')
        self.x_coord = 0
        self.ip_address = None
    
    def control_x_coord(self, x_coord, ip_address):
        #http://192.168.120.36/command?commandText=G0 X20
        url = f"{ip_address}/command?commandText=G0 X{str(x_coord)}"
        response = requests.get(url)
        if response.status_code == 200:
            self.get_logger().info('HTTP GET 요청 성공: x_coord={}, IP={}, Command={}'.format(x_coord, self.ip_address, self.command))
            if response.text.strip() == 'busy':
                self.get_logger().warn('Busy 상태이므로 다시 요청합니다.')
                self.control_x_coord(x_coord)
        else:
            self.get_logger().warn('HTTP GET 요청 실패: x_coord={}, IP={}, Command={}'.format(x_coord, self.ip_address, self.command))

    def alarm_callback(self, msg):
        control_x_coord(self.y_coord, self.ip_address)

    def ready_callback(self, msg):
        control_x_coord(0, self.ip_address)

    def subscribe_x_coord(self, msg):
        self.x_coord = msg.data
    
    def subscribe_ip_address(self, msg):
        self.ip_address = msg.data
    
# ROS 노드 3: y좌표를 받고, 기계를 제어하는 노드
class YCoordNode(Node):
    def __init__(self):
        super().__init__('y_coord_node')
        self.alarm_subcriber = self.create_subscription(String, 'alarm_topic', self.alarm_callback, 10)
        self.ready_subcriber = self.create_subscription(String, 'ready_topic', self.ready_callback, 10)
        self.y_coord_subcriber = self.create_subscription(Int32, 'y_coord_topic', self.subscribe_y_coord, 3)
        self.ip_address_subcriber = self.create_subscription(String, 'ip_address_topic', self.subscribe_ip_address, 10)

        self.get_logger().info('YCoord node initialized')
        self.y_coord = 0
        self.ip_address = None
    
    def control_y_coord(self, y_coord, ip_address):
        #http://192.168.120.36/command?commandText=G0 Y20
        url = f"{ip_address}/command?commandText=G0 Y{str(y_coord)}"
        response = requests.get(url)
        if response.status_code == 200:
            self.get_logger().info('HTTP GET 요청 성공: x_coord={}, IP={}, Command={}'.format(y_coord, ip_address, self.command))
            if response.text.strip() == 'busy':
                self.get_logger().warn('Busy 상태이므로 다시 요청합니다.')
                self.control_y_coord(y_coord, ip_address)
        else:
            self.get_logger().warn('HTTP GET 요청 실패: x_coord={}, IP={}, Command={}'.format(y_coord, self.ip_address, self.command))

    def alarm_callback(self, msg):
        control_y_coord(self.y_coord, self.ip_address)

    def ready_callback(self, msg):
        control_y_coord(0, self.ip_address)

    def subscribe_y_coord(self, msg):
        self.y_coord = msg.data

    def subscribe_ip_address(self, msg):
        self.ip_address = msg.data

# ROS 노드 4: 모터 값을 받고, 기계를 제어하는 노드
class MotorNode(Node):
    def __init__(self):
        super().__init__('motor_node')
        self.alarm_subcriber = self.create_subscription(String, 'alarm_topic', self.alarm_callback, 10)
        self.ready_subcriber = self.create_subscription(String, 'ready_topic', self.ready_callback, 10)
        self.motor_subcriber = self.create_subscription(Int32, 'motor_topic', self.subscribe_motor, 10)
        self.ip_address_subcriber = self.create_subscription(String, 'ip_address_topic', self.subscribe_ip_address, 10)

        self.get_logger().info('Motor node initialized')
        self.motor = 0
        self.ip_address = None
    
    def control_y_coord(self, motor, ip_address):
        #http://192.168.120.36/command?commandText=M106 P0 0~255
        url = f"{ip_address}/command?commandText=M106 P0 {motor}"
        response = requests.get(url)
        if response.status_code == 200:
            self.get_logger().info('HTTP GET 요청 성공: x_coord={}, IP={}, Command={}'.format(y_coord, ip_address, self.command))
            if response.text.strip() == 'busy':
                self.get_logger().warn('Busy 상태이므로 다시 요청합니다.')
                self.control_y_coord(y_coord, ip_address)
        else:
            self.get_logger().warn('HTTP GET 요청 실패: x_coord={}, IP={}, Command={}'.format(y_coord, self.ip_address, self.command))

    def alarm_callback(self, msg):
        control_motor(self.motor, self.ip_address)

    def ready_callback(self, msg):
        control_motor(0, self.ip_address)

    def subscribe_motor(self, msg):
        self.motor = msg.data

    def subscribe_ip_address(self, msg):
        self.ip_address = msg.data


def run_ros_nodes():
    rclpy.init()
    time_node = TimeNode()
    x_coord_node = XCoordNode()
    y_coord_node = YCoordNode()
    motor_node = MotorNode()
    executor = MultiThreadedExecutor()
    executor.add_node(time_node)
    executor.add_node(x_coord_node)
    executor.add_node(y_coord_node)
    executor.add_node(motor_node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        rclpy.shutdown()
        print("All ROS nodes have been shutdown")

def valid_ip(ip):
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        return True
    except ValueError:
        return False
        
def valid_coordinates(x, y):
    try:
        if isinstance(x, int) and isinstance(y, int):
            return True
    except ValueError:
        return False
    
def valid_time(time):
    try:
        if isinstance(time, str) and len(time) == 5 and time[2] == ':' and 0 <= int(time[:2]) <= 23 and 0 <= int(time[3:]) <= 59:
            return True
    except ValueError:
        return False

def valid_motor(motor):
    try:
        if isinstance(motor, str) and 0 <= int(motor) < 256:
            return True
    except ValueError:
        return False
    
@app.route('/', methods=['GET'])
def hello():
    pkg_path = os.path.join(get_package_share_directory('my_package'))
    index_path = os.path.join(pkg_path, 'templates/index.html')
    return send_file(index_path)

def publish_ip_address_to_ros(ip_address):
    node = rclpy.create_node('flask_publisher')
    ip_address_publisher = node.create_publisher(String, 'ip_address_topic', 10)
    msg = String()
    msg.data = ip_address
    ip_address_publisher.publish(msg)

@app.route('/ip-address', methods=['POST'])
def set_ip_address():
    data = request.get_json()
    ip_address = data['ipAddress']
    if valid_ip(ip_address):
        publish_ip_address_to_ros(ip_address)
        print('IP address received: {}'.format(ip_address))
        return 'Your IP address is: {}'.format(ip_address)
    else:
        print('Invalid IP address received: {}'.format(ip_address))
        return 'Invalid IP address'

def publish_coord_to_ros(x_coord, y_coord):
    if valid_coordinates(x_coord, y_coord):
        node = rclpy.create_node('flask_publisher')
        x_coord_publisher = node.create_publisher(Int32, 'x_coord_topic', 10)
        y_coord_publisher = node.create_publisher(Int32, 'y_coord_topic', 10)
        x_coord_msg = Int32()
        x_coord_msg.data = x_coord
        y_coord_msg = Int32()
        y_coord_msg.data = y_coord
        x_coord_publisher.publish(x_coord_msg)
        y_coord_publisher.publish(y_coord_msg)
        print('Coordinates received: x={}, y={}'.format(x_coord, y_coord))
        return 'Coordinates received: x={}, y={}'.format(x_coord, y_coord)
    else:
        print('Invalid coordinates received: x={}, y={}'.format(x_coord, y_coord))
        return 'Invalid coordinates'
    
@app.route('/coord', methods=['POST'])
def set_coordinates():
    data = request.get_json()
    x_coord_int = data['xCoord']
    y_coord_int = data['yCoord']
    return publish_coord_to_ros(x_coord, y_coord)
    
@app.route('/coord/alarm', methods=['POST'])
def set_alarm_coordinates():
    data = request.get_json()
    x_coord_str = data['xCoord']
    y_coord_str = data['yCoord']
    return publish_coord_to_ros(int(x_coord_str), int(y_coord_str))

def publish_time_to_ros(time):
    node = rclpy.create_node('flask_publisher')
    time_publisher = node.create_publisher(String, 'time_topic', 10)
    msg = String()
    msg.data = time
    time_publisher.publish(msg)

@app.route('/time', methods=['POST'])
def set_time():
    data = request.get_json()
    time = data['time']
    print(type(time), time)
    if valid_time(time):
        print('Time received: {}'.format(time))
        publish_time_to_ros(time)
        return 'Time received: {}'.format(time)
    else:
        print('Invalid time received: {}'.format(time))
        return 'Invalid time'

def publish_motor_to_ros(motor):
    node = rclpy.create_node('flask_publisher')
    motor_publisher = node.create_publisher(String, 'motor_topic', 10)
    msg = String()
    msg.data = motor
    motor_publisher.publish(msg)

@app.route('/motor', methods=['POST'])
def set_motor():
    data = request.get_json()
    motor = data['motor']
    if valid_motor(motor):
        publish_motor_to_ros(motor)
        print('motor received: {}'.format(motor))
        return 'motor received: {}'.format(motor)
    else:
        return 'Invalid motor: {}'.format(motor)

def main(arg=None):
    ros_thread = threading.Thread(target=run_ros_nodes)
    ros_thread.start()

    app.run(debug=False)

if __name__ == '__main__':
    main()
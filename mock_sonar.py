import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import random

class MockSonarNode(Node):
    def __init__(self):
        # Название узла в графе ROS 2
        super().__init__('mock_sonar_front')
        
        # Создаем Publisher: публикуем дистанцию (Float32) в топик '/sensor/sonar_front'
        self.publisher_ = self.create_publisher(Float32, '/sensor/sonar_front', 10)
        
        # Таймер, который вызывает функцию каждую 1 секунду
        timer_period = 1.0
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info('Виртуальный передний ToF-сонар запущен!')

    def timer_callback(self):
        msg = Float32()
        # Симулируем дистанцию от 0.2 до 3.0 метров
        msg.data = random.uniform(0.2, 3.0)
        self.publisher_.publish(msg)
        self.get_logger().info(f'Публикую дистанцию: {msg.data:.2f} м')

def main(args=None):
    rclpy.init(args=args)
    node = MockSonarNode()
    try:
        rclpy.spin(node) # Крутим цикл, пока не нажмем Ctrl+C
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

class SafetyNode(Node):
    def __init__(self):
        super().__init__('safety_node')
        
        # Создаем Subscriber. 
        # Аргументы: Тип сообщения, Имя топика, Функция-колбек, Размер очереди(QoS)
        self.subscription = self.create_subscription(
            Float32,
            '/sensor/sonar_front',
            self.sonar_callback,
            10
        )
        self.subscription  # предотвращаем удаление переменной сборщиком мусора
        
        # Задаем критическую дистанцию в метрах
        self.critical_distance = 0.5 
        
        self.get_logger().info('Узел безопасности запущен. Охраняю периметр!')

    def sonar_callback(self, msg):
        # Эта функция вызывается АВТОМАТИЧЕСКИ каждый раз, когда в топик приходит новое сообщение
        distance = msg.data
        
        if distance < self.critical_distance:
            # Используем уровень логирования WARN (предупреждение) - он выделится цветом
            self.get_logger().warning(f'АВАРИЙНАЯ ОСТАНОВКА! Препятствие на расстоянии {distance:.2f} м!')
        else:
            self.get_logger().info(f'Путь свободен (до препятствия {distance:.2f} м).')

def main(args=None):
    rclpy.init(args=args)
    safety_node = SafetyNode()
    
    try:
        rclpy.spin(safety_node) # Ждем сообщений бесконечно
    except KeyboardInterrupt:
        pass
    finally:
        safety_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()